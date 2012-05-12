import jinja2, spidermonkey, sys, os, unittest
from jasinja import codegen

try:
	import simplejson as json
except ImportError:
	import json

DIR = os.path.dirname(__file__)

def testdir(x):
	return jinja2.FileSystemLoader(os.path.join(DIR, x))

def testfile(x):
	return open(os.path.join(DIR, x)).read()

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
	(testfile('scoping.txt'), {'a': 'alpha', 'b': ['beta']}),
	('{{ "%s: %s"|format(a, b) }}', {'a': 1, 'b': 'alpha'}),
	(testfile('nested-for.txt'), {}),
	('{{ x|join(", ") }}', {'x': ['1', '2', 3]}),
	('{{ x|sort|join(", ") }}', {'x': [1, 2, 3]}),
	('{{ x|length }} {{ x|count }}', {'x': [1, 2]}),
	('{{ x|int }} {{ y|int }} {{ z|int }}', {'x': 3.5, 'y': 'a', 'z': '13'}),
	('{{ x|capitalize }}', {'x': 'hello!'}),
	('{{ "%.1f %.1f"|format(y|float, z|float) }}', {'y': 'a', 'z': '4.5'}),
	('{{ x|d(1) ~ " " ~ y|d(2, true) }}', {'y': 0}),
	('{{ (x|list)[0] ~ (y|list)[1] }}', {'x': 'foo', 'y': {'a': 1, 'b': 2}}),
	('{{ (x|dictsort)[1][1] }}', {'x': {'b': 1, 'a': 3}}),
	('{{ x|round|int ~ " " ~ y|round(2) }}', {'x': 3.55, 'y': 4.553}),
	('{{ x|capitalize }}', {'x': 'ALPHA'}),
	('{{ x|title }}', {'x': 'dsaldsa AKSDAS A3FDAS"s'}),
	('{{ (x|string)[0:4] }}', {'x': 2143942}),
	('{% set a, b = x %}{{ a }}', {'x': (1, 2)}),
	('{% for a, b in x %}{{ a }}{% endfor %}', {'x': [(1, 2)]}),
	('{{ x|center(20) }}', {'x': 'aaaa'}),
	('{{ x|center(20) }}', {'x': 'aaaaa'}),
	('{{ x|filesizeformat }} {{ y|filesizeformat }}', {'x': 13, 'y': 21324}),
	('{{ x|first ~ y|first }}', {'x': [1, 2], 'y': 'days'}),
	('{{ x|last ~ y|last }}', {'x': [1, 2], 'y': 'days'}),
	('{{ x is divisibleby(3) }}', {'x': 6}),
	('{{ x is odd }}', {'x': 6}),
	('{{ x is even }}', {'x': 6}),
	('{{ x is odd }}', {'x': 7}),
	('{{ x is even }}', {'x': 7}),
	('{{ x is upper }}', {'x': 'AAADSADSA'}),
	('{{ x is lower }}', {'x': 'AAADSadsa'}),
	('{{ x is string }}', {'x': 'a'}),
	('{{ x is number }}', {'x': 'a'}),
	('{{ x is string }}', {'x': 3}),
	('{{ x is number }}', {'x': 3}),
	('{{ x is undefined }}', {}),
	(testfile('macro-nest.txt'), {'x': 1}),
	('{{ "%03i"|format(x) }}', {'x': 1}),
	('{{ "% 5i"|format(x) }}', {'x': 13}),
	('{{ "%10.2f"|format(x) }}', {'x': 13.6}),
	('{{ "%6i"|format(x) }}', {'x': 7}),
	('{{ "%.2f"|format(x) }}', {'x': 3.758}),
	('{{ "%20s"|format(x) }}', {'x': 'xxx'}),
	('{{ x|upper }}{{ y|lower }}', {'x': 'aAa', 'y': 'AaA'}),
	('{{ x|sum(start=10) }}', {'x': [1, 2, 3]}),
	(testfile('batched.txt'), {'x': [1, 2, 3, 4, 5, 6]}),
	(testfile('batched.txt'), {'x': [1, 2, 3]}),
	(testfile('groupby.txt'), {'x': [{'a': 1, 'b': 2}, {'a': 1, 'b': 3}]}),
	('{{ x|indent }}', {'x': 'one\ntwo\nthree'}),
	('{{ x|indent(4, true) }}', {'x': 'one\ntwo\nthree'}),
	('{{ x|replace("a", "b") }}', {'x': 'abcdefa'}),
	(testfile('sliced.txt'), {'x': [1, 2, 3]}),
	(testfile('sliced.txt'), {'x': [1, 2, 3, 4, 5, 6]}),
	('{{ x|xmlattr }}', {'x': {'a': 'c', 'b': 'd'}}),
	('{{ x|xmlattr(false) }}', {'x': {'a': None, 'b': 'd'}}),
	('{{ x|trim }}', {'x': '\na\t '}),
	('{{ x|truncate(3) }}', {'x': 'xxxxxxxxx'}),
	('{{ x|truncate(3, false) }}', {'x': 'xxxxxxxxx'}),
	('{{ x|truncate(3, false, ">") }}', {'x': 'xx xxxxxxx'}),
	('{{ x|wordcount }}', {'x': 'foo bar crap\t\nsomething'}),
	('{{ x|default("A") }}', {'x': ''}),
	('{{ x|default("A", true) }}', {'x': ''}),
	(testfile('macro-assign.txt'), {'b': 1}),
	('{% macro a() %}{{ x }}{% endmacro %}{% set x = y %}', {'y': 1}),
	('{% macro a(b=1) %}{{ b }}{% endmacro %}{{ a() }}', {}),
	('{% macro a(b=1) %}{{ b }}{% endmacro %}{{ a(x) }}', {'x': 2}),
	('{% macro a(b=1) %}{{ b }}{% endmacro %}{{ a(x) }}', {'x': 2}),
	('{% macro a(b, c=1) %}{{ b }}{{ c }}{% endmacro %}{{ a(3) }}', {}),
	('{% for x in y if x % 2 %}{{ x }}{% endfor %}', {'y': range(6)}),
	(testfile('loop-filter.txt'), {'y': range(6)}),
	(testfile('loop-shadow.txt'), {'x': [0, 1, 2]}),
	('{% macro m() %}{{ x }}{% endmacro %}{{ m() }}', {'x': 1}),
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
	code = js + '\nJasinja.templates.index.render(%s);' % jsobj
	try:
		return str(ctx.execute(code))
	except spidermonkey.JSError, e:
		return e

def pytest(env, data):
	tmpl = env.get_template('index')
	return tmpl.render(data)

def run(self, i, verbose=False):
	
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
	if isinstance(js, str) and js.isdigit() and py:
		res = float(js) == float(py)
	if {'true': 'True', 'false': 'False'}.get(js, js) == py:
		res = True
	
	if verbose:
		print 'EQ:', res
	
	assert res

def test():
	
	for i, t in enumerate(TESTS):
		res = run(i)
		sys.stdout.write('.' if res else 'F')
		if not res:
			print
			run(i, True)
			break
	
	sys.stdout.write('\n')

def testfunc(i):
	def do(self):
		return self._do(i)
	return do

attrs = {'_do': run}
for i, case in enumerate(TESTS):
	m = testfunc(i)
	m.__name__ = 'test_%i' % i
	if isinstance(case[0], basestring) and len(case[0]) < 40:
		m.__doc__ = '%i: %s' % (i, case[0])
	else:
		m.__doc__ = 'Test case %i' % i
	attrs['test_%i' % i] = m

JasinjaTests = type('JasinjaTests', (unittest.TestCase,), attrs)

def suite():
    return unittest.makeSuite(JasinjaTests, 'test')

if __name__ == '__main__':
	args = sys.argv[1:]
	if args:
		run(None, int(args[0]), True)
	else:
	    unittest.main(defaultTest='suite')
