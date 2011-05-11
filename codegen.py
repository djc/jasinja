from jinja2.compiler import CodeGenerator, Frame, EvalContext
from jinja2.parser import Parser

class JSCodeGen(CodeGenerator):
	
	def visit_Template(self, node, frame=None):
		
		self.writeline('var template = {')
		self.indent()
		self.writeline('')
		
		frame = Frame(EvalContext(self.environment, self.name))
		for n in node.body:
			self.visit(n, frame)
		
		self.writeline('')
		self.outdent()
		self.writeline('};')
	
	def visit_Output(self, node, frame):
		
		self.writeline('"output": function(ctx) {')
		self.indent()
		
		self.writeline('return [')
		self.indent()
		
		for n in node.nodes:
			self.visit(n, frame)
		
		self.outdent()
		self.writeline('].join("");')
		
		self.outdent()
		self.writeline('}')
	
	def visit_Name(self, node, frame):
		self.writeline('ctx["%s"]' % node.name)

def compile(env, src):
	return Parser(env, src, 'test', 'test.html').parse()

def generate(env, tmpl):
	gen = JSCodeGen(env, 'blah', 'index.html', None, False)
	gen.visit(tmpl)
	return gen.stream.getvalue()
