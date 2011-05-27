from jinja2.compiler import CodeGenerator, Frame, EvalContext
from jinja2.parser import Parser
from jinja2 import nodes

class JSCodeGen(CodeGenerator):
	
	def jsmacro(self, node, frame):
		
		self.writeline('')
		self.write('"%s": function(' % node.name)
		for n in node.args:
			self.write(n.name)
		self.write(') {')
		self.indent()
		self.writeline('var _buf = [];')
		
		frame = Frame(frame.eval_ctx, frame)
		for n in node.body:
			self.visit(n, frame)
		
		self.writeline('return _buf.join("");')
		self.outdent()
		self.newline()
		self.write('}')
	
	def visit_Template(self, node, frame=None):
		
		frame = Frame(EvalContext(self.environment, self.name))
		frame.buffer = '_buf'
		
		self.indent()
		self.writeline('')
		self.writeline('"%s": {' % self.name)
		self.indent()
		self.writeline('')
		
		self.writeline('')
		self.write('"macros": ')
		macros = list(node.find_all(nodes.Macro))
		if not macros:
			self.write('{},')
		else:
			self.write('{')
			self.indent()
			self.writeline('')
			for i, n in enumerate(macros):
				self.jsmacro(n, frame)
				if i != len(macros) - 1: self.write(',')
			self.writeline('')
			self.outdent()
			self.writeline('},')
		
		self.writeline('')
		self.writeline('"render": function(ctx) {')
		self.indent()
		self.writeline('var _buf = [];')
		
		for n in node.body:
			self.visit(n, frame)
		
		self.writeline('return _buf.join("");')
		self.outdent()
		self.writeline('}')
		self.outdent()
		self.writeline('')
		self.writeline('}')
		self.writeline('')
	
	def visit_Macro(self, node, frame):
		pass
	
	def visit_Call(self, node, frame):
		self.write('this.macros.' + node.node.name)
		self.write('(')
		for n in node.args:
			self.visit(n, frame)
		self.write(')')
		
	def visit_Output(self, node, frame):
		for n in node.nodes:
			self.newline()
			self.write('_buf.push(')
			self.visit(n, frame)
			self.write(');')
		
	def visit_Name(self, node, frame):
		if frame.parent is None:
			self.write('ctx["%s"]' % node.name)
		else:
			self.write(node.name)
	
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
	
	def visit_Getattr(self, node, frame):
		self.visit(node.node, frame)
		self.write('.')
		self.write(node.attr)
	
	def visit_Getitem(self, node, frame):
		if isinstance(node.arg, nodes.Slice):
			
			assert node.arg.step is None
			self.write('filters._slice(')
			self.visit(node.node, frame)
			self.write(', ')
			
			if node.arg.start is not None:
				self.visit(node.arg.start, frame)
			else:
				self.write('0')
			
			self.write(', ')
			if node.arg.stop is not None:
				self.visit(node.arg.stop, frame)
			else:
				self.write('undefined')
			
			self.write(')')
			
		else:
			assert False
	
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

def generate(env, templates):
	
	out = []
	for name in templates:
		src, fn, up = env.loader.get_source(env, name)
		gen = JSCodeGen(env, name, fn, None, False)
		gen.visit(compile(env, src))
		out.append(gen.stream.getvalue().rstrip())
	
	src = open('meta.js').read()
	return src.replace('[DATA]', ',\n    \n'.join(out))

def pygen(env, name):
	src, fn, up = env.loader.get_source(env, name)
	gen = CodeGenerator(env, 'blah', 'index.html', None, False)
	gen.visit(compile(env, src))
	return gen.stream.getvalue()
