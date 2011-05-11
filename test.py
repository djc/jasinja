import codegen, jinja2, spidermonkey
import simplejson as json

def jstest(src, data):
	env = jinja2.Environment()
	run = spidermonkey.Runtime()
	ctx = run.new_context()
	js = codegen.generate(env, codegen.compile(env, src))
	jsobj = json.dumps(data)
	code = js + '\ntemplate.output(%s);' % jsobj
	return ctx.execute(code)

def pytest(src, data):
	return jinja2.Template(src, 'test').render(data)

src = '{{ test }}'
data = {'test': 'crap'}
print repr(jstest(src, data))
print repr(pytest(src, data))
