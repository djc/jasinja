from jinja2.compiler import CodeGenerator, Frame, EvalContext
from jinja2.parser import Parser

PREFIX = 'prefix.js'

class JSCodeGen(CodeGenerator):
	
	def visit_Template(self, node, frame=None):
		
		with open(PREFIX) as f:
			for ln in f:
				self.writeline(ln.rstrip())
		
		self.writeline('')
		self.writeline('var template = {')
		self.indent()
		
		self.writeline('')
		self.writeline('"render": function(ctx) {')
		self.indent()
		self.writeline('var _buf = [];')
		
		frame = Frame(EvalContext(self.environment, self.name))
		frame.buffer = '_buf'
		
		for n in node.body:
			self.visit(n, frame)
		
		self.writeline('return _buf.join("");')
		self.outdent()
		self.writeline('}')
		self.outdent()
		self.writeline('')
		self.outdent()
		self.writeline('};')
	
	def visit_Output(self, node, frame):
		for n in node.nodes:
			self.newline()
			self.write('_buf.push(')
			self.visit(n, frame)
			self.write(');')
	
	def visit_Name(self, node, frame):
		self.write('ctx["%s"]' % node.name)
	
	def visit_TemplateData(self, node, frame):
		val = node.as_const(frame.eval_ctx)
		if isinstance(val, unicode):
			val = val.encode('utf-8')
		self.write(repr(val))
	
	def visit_CondExpr(self, node, frame):
		self.write('(')
		self.visit(node.test, frame)
		self.write(' ? ')
		self.visit(node.expr1, frame)
		self.write(' : ')
		self.visit(node.expr2, frame)
		self.write(')')
	
	def visit_Filter(self, node, frame):
		self.write('filters.' + node.name + '(')
		self.visit(node.node, frame)
		self.write(', [')
		
		first = True
		for n in node.args:
			if not first: self.write(', ')
			self.visit(n, frame)
			first = False
		
		self.write('])')
	
	def visit_If(self, node, frame):
		
		self.newline()
		self.write('if (')
		self.visit(node.test, frame)
		self.write(') {')
		
		self.indent()
		for n in node.body:
			self.visit(n, frame)
		
		self.outdent()
		if not node.else_:
			self.writeline('}')
			return
		
		self.writeline('} else {')
		self.indent()
		for n in node.else_:
			self.visit(n, frame)
		self.outdent()
		self.writeline('}')
		

def compile(env, src):
	return Parser(env, src, 'test', 'test.html').parse()

def generate(env, tmpl):
	gen = JSCodeGen(env, 'blah', 'index.html', None, False)
	gen.visit(tmpl)
	return gen.stream.getvalue()

def pygen(env, tmpl):
	gen = CodeGenerator(env, 'blah', 'index.html', None, False)
	gen.visit(tmpl)
	return gen.stream.getvalue()
