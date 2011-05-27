import codegen, jinja2, spidermonkey, sys
import simplejson as json

def jstest(env, src, data):
	run = spidermonkey.Runtime()
	ctx = run.new_context()
	js = codegen.generate(env, codegen.compile(env, src))
	jsobj = json.dumps(data)
	code = js + '\ntemplate.render(%s);' % jsobj
	return ctx.execute(code)

def pytest(env, src, data):
	tmpl = env.from_string(src)
	return tmpl.render(data)

WORKS = [
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
]

# next:
# - assignment + cond-expr
# - for-loop

src, data = WORKS[int(sys.argv[1])]
env = jinja2.Environment()
ast = codegen.compile(env, src)
print ast
print codegen.generate(env, ast)

print 'js:', repr(jstest(env, src, data))
print 'py:', repr(pytest(env, src, data))
