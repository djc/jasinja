import jinja2, spidermonkey, sys, os
import simplejson as json
from jasinja import codegen

dir = os.path.dirname(__file__)

def testdir(x):
	return jinja2.FileSystemLoader(os.path.join(dir, x))

def testfile(x):
	return open(os.path.join(dir, x)).read()

TESTS = [
	('{{ test }}', {'test': 'crap'}),
	('{% if a %}x{% endif %}', {'a': True}),
	('{% if a %}c{% endif %}b', {'a': False}),
	('{{ 1 if a else 2 }}', {'a': True}),
	('{{ 1 if a else 2 }}', {'a': False}),
	('{% if a %}d{% else %}e{% endif %}', {'a': False}),
	('{% if a %}f{% elif b %}g{% endif %}', {'b': True}),
	("{{ '%4.2f'|format(x) }}", {'x': 17.0}),
	('{{ d[:7] }}', {'d': '2011-05-27'}),
	('{{ a.x }}', {'a': {'x': 'z'}}),
	('{{ "%.6f"|format(a / b) }}', {'a': 5.0, 'b': 3}),
	('{{ "%.1f"|format(a.x / b.y * 100) }}', {'a': {'x': 20}, 'b': {'y': 5}}),
	('{% macro x(y) %}{{ y / 2 }}{% endmacro %}{{ x(z) }}', {'z': 512}),
	(
		'{% macro x(y, z) %}{{ y + z }}{% endmacro %}{{ x(y, z) }}',
		{'z': 512, 'y': 3},
	),
	('{{ x is none }}', {'x': None}),
	('{{ "%.2f%%"|format(a) }}', {'a': 5}),
	(testdir('basic-blocks'), {}),
	('{{ a[x] }}', {'a': {'y': 1}, 'x': 'y'}),
	('{% for x in ls %}{{ x }}{% endfor %}', {'ls': ['a', 'b']}),
	('{% set x = y %}{{ x }}', {'y': 1}),
	('{% for x in y %}{{ loop.index % 2 }}{% endfor %}', {'y': ['a', 'b']}),
	('{{ 1 if not x else 0 }}', {'x': False}),
	('{{ 1 if x is not defined else 0 }}', {}),
	('\n\n{{- x }}\t\t', {'x': 1}),
	('alpha {# beta #}', {}),
	('{% raw %}{{ my template }}{% endraw %}', {}),
	('{{ x }}## flabby\n{{ x }}', {'x': 'a'}),
	('{{ x.y.z }}', {'x': {'y': {'z': 1}}}),
	("{{ x.split('-', 1)[0] }}", {'x': '3-1'}),
	(
		'{% for i in x %}{% if loop.first %}{{ i }}{% endif %}{% endfor %}',
		{'x': ['a', 'b', 'c']},
	),
	('{% for i in x %}{{ loop.cycle("o", "e") }}{% endfor %}', {'x': [1, 2]}),
	('{{ x or y }}', {'x': 1, 'y': 0}),
	('{{ x and y }}', {'x': 2, 'y': 1}),
	('{{ x in y }}', {'y': [1, 2], 'x': 1}),
	('{{ x in y }}', {'y': 'alpha', 'x': 'ph'}),
	('{{ "x" in y }}', {'y': {'x': 1}}),
	('{{ "hi" ~ x ~ "there!" }}', {'x': 1}),
	(testdir('no-override'), {}),
	('''{{ '&<>"'|e }}{{ "'"|e }}''', {}),
	('{% filter e %}&<>{% endfilter %}', {}),
	('{{ ("a", "b")[1] }}', {}),
	(testdir('include'), {}),
	("{{ 1 if 'a' not in ['a', 'b'] else 2 }}", {}),
	('{% for x in a|reverse %}{{ x }}{% endfor %}', {'a': ['alpha', 'beta']}),
	('{{ a }} {{ a|abs }}', {'a': -1}),
	(testfile('scoping.html'), {'a': 'alpha', 'b': ['beta']}),
	('{{ "%s: %s"|format(a, b) }}', {'a': 1, 'b': 'alpha'}),
	(testfile('nested-for.html'), {}),
]

def loader(i):
	if isinstance(TESTS[i][0], str):
		return jinja2.DictLoader({'index': TESTS[i][0]})
	else:
		return TESTS[i][0]

def jstest(env, data):
	run = spidermonkey.Runtime()
	ctx = run.new_context()
	js = codegen.generate(env)
	jsobj = json.dumps(data)
	code = js + '\ntemplates.index.render(%s);' % jsobj
	return str(ctx.execute(code))

def pytest(env, data):
	tmpl = env.get_template('index')
	return tmpl.render(data)

def run(i, verbose=False):
	
	src, data = TESTS[i]
	env = jinja2.Environment(loader=loader(i))
	ast = codegen.compile(env, src)
	
	if verbose:
		print ast
		print codegen.generate(env)
		#print codegen.pygen(env, 'index')
	
	js = jstest(env, data)
	py = pytest(env, data)
	
	if verbose:
		print 'js:', repr(js)
		print 'py:', repr(py)
	
	res = js == py
	if isinstance(js, str) and js.isdigit():
		res = float(js) == float(py)
	if {'true': 'True', 'false': 'False'}.get(js, js) == py:
		res = True
	
	if verbose:
		print 'EQ:', res
	
	return res

def test():
	
	for i, t in enumerate(TESTS):
		res = run(i)
		sys.stdout.write('.' if res else 'F')
		if not res:
			print
			run(i, True)
			break
	
	sys.stdout.write('\n')

if __name__ == '__main__':
	args = sys.argv[1:]
	if args:
		run(int(args[0]), True)
	else:
		test()
