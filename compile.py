import codegen, jinja2, sys

def compile(path, templates):
	env = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
	print codegen.generate(env, templates)

if __name__ == '__main__':
	compile(sys.argv[1], sys.argv[2:])
