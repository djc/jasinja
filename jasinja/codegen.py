from jinja2.compiler import CodeGenerator, Frame, EvalContext
from jinja2.parser import Parser
from jinja2 import nodes
import os

META = os.path.join(os.path.dirname(__file__), 'meta.js')
FILTER_ARGS = {
	'attr': ('name',),
	'batch': ('linecount', 'fill_with'),
	'center': ('width',),
	'default': ('default_value', 'boolean'),
	'd': ('default_value', 'boolean'),
	'dictsort': ('case_sensitive', 'by'),
	'filesizeformat': ('binary',),
	'float': ('default',),
	'groupby': ('attribute',),
	'indent': ('width', 'indentfirst'),
	'int': ('default',),
	'join': ('d', 'attribute'),
	'replace': ('old', 'new', 'count'),
	'round': ('precision', 'method'),
	'slice': ('slices', 'fill_with'),
	'sort': ('reverse', 'case_sensitive', 'attribute'),
	'sum': ('attribute', 'start'),
	'truncate': ('length', 'killwords', 'end'),
	'xmlattr': ('autospace',),
}

def nextvar(frame, prefix):
	idx, n = 0, prefix + '0'
	while n in frame.identifiers.declared:
		idx, n = idx + 1, prefix + str(idx + 1)
	return n

class JSCodeGen(CodeGenerator):
	
	def jsmacro(self, node, frame):
		
		self.writeline('')
		self.write('"%s": function(ctx, tmpl' % node.name)
		
		args = set()
		for n in node.args:
			self.write(', ')
			self.write(n.name)
			args.add(n.name)
		
		frame = Frame(frame.eval_ctx, frame)
		frame.identifiers.declared = args
		self.write(') {')
		self.indent()
		self.newline()
		
		for arg, val in zip(node.args[-len(node.defaults):], node.defaults):
			self.visit(arg, frame)
			self.write(' = ')
			self.visit(arg, frame)
			self.write(' || ')
			self.visit(val, frame)
			self.write(';')
		
		self.newline()
		self.writeline('var %s = [];' % frame.buffer)
		for n in node.body:
			self.visit(n, frame)
		
		self.writeline('return %s.join("");' % frame.buffer)
		self.outdent()
		self.newline()
		self.write('}')
	
	def block(self, node, frame):
		
		self.writeline('')
		self.write('"%s": function(ctx) {' % node.name)
		self.indent()
		self.writeline('var %s = [];' % frame.buffer)
		
		frame = Frame(frame.eval_ctx, frame)
		for n in node.body:
			self.visit(n, frame)
		
		self.writeline('return %s.join("");' % frame.buffer)
		self.outdent()
		self.newline()
		self.write('}')
	
	def visit_Include(self, node, frame):
		self.newline()
		self.write('%s.push(Jasinja.templates[' % frame.buffer)
		self.visit(node.template, frame)
		self.write('].render(ctx));')
		self.newline()
	
	def visit_Template(self, node, frame=None):
		
		frame = Frame(EvalContext(self.environment, self.name))
		frame.buffer = '_buf'
		frame.toplevel = True
		
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
		self.write('"blocks": ')
		blocks = list(node.find_all(nodes.Block))
		if not blocks:
			self.write('{},')
		else:
			self.write('{')
			self.indent()
			self.writeline('')
			for i, n in enumerate(blocks):
				self.block(n, frame)
				if i != len(blocks) - 1: self.write(',')
			self.writeline('')
			self.outdent()
			self.writeline('},')
		
		self.writeline('')
		self.writeline('"render": function(ctx, tmpl) {')
		self.indent()
		
		extends = node.find(nodes.Extends)
		if extends:
			self.newline()
			self.write('return Jasinja.templates[')
			self.visit(extends.template, frame)
			self.write('].render(ctx, this);')
		else:
			self.writeline('')
			self.writeline('tmpl = Jasinja.utils.extend(this, tmpl);')
			self.writeline('')
			self.writeline('var %s = [];' % frame.buffer)
			for n in node.body:
				self.visit(n, frame)
			self.writeline('return %s.join("");' % frame.buffer)
			self.writeline('')
		
		self.outdent()
		self.writeline('}')
		self.outdent()
		self.writeline('')
		self.writeline('}')
		self.writeline('')
	
	def visit_Const(self, node, frame):
		val = node.value
		if isinstance(val, float):
			self.write(str(val))
		elif val is False:
			self.write('false')
		elif val is True:
			self.write('true')
		elif val is None:
			self.write('null')
		else:
			self.write(repr(val))
	
	def visit_Tuple(self, node, frame):
		self.visit_List(node, frame)
	
	def visit_Block(self, node, frame):
		bits = frame.buffer, node.name
		self.writeline('%s.push(tmpl.blocks["%s"](ctx));' % bits)
	
	def visit_Extends(self, node, frame):
		pass
	
	def visit_Macro(self, node, frame):
		pass
	
	def visit_FilterBlock(self, node, frame):
		
		local = Frame(EvalContext(self.environment, self.name))
		local.buffer = '_fbuf'
		local.toplevel = frame.toplevel
		
		self.writeline('var %s = [];' % local.buffer)
		for n in node.body:
			self.visit(n, local)
		
		bits = frame.buffer, node.filter.name, local.buffer
		self.writeline('%s.push(Jasinja.filters.%s(%s.join("")));' % bits)
	
	def visit_Assign(self, node, frame):
		
		if isinstance(node.target, nodes.Tuple):
			for target in node.target.items:
				frame.identifiers.declared.add(target.name)
		else:
			frame.identifiers.declared.add(node.target.name)
		
		self.newline()
		self.write('var ')
		self.visit(node.target, frame)
		self.write(' = ')
		self.visit(node.node, frame)
		self.write(';')
	
	def visit_Call(self, node, frame):
		
		if isinstance(node.node, nodes.Name):
			self.write('tmpl.macros.' + node.node.name)
			self.write('(ctx, tmpl')
			if node.args: self.write(', ')
		else:
			self.visit(node.node, frame)
			self.write('(')
		
		if not node.args:
			self.write(')')
			return
		
		first = True
		for n in node.args:
			if not first: self.write(', ')
			self.visit(n, frame)
			first = False
		self.write(')')
		
	def visit_Output(self, node, frame):
		for n in node.nodes:
			self.newline()
			self.write('%s.push(' % frame.buffer)
			self.visit(n, frame)
			self.write(');')
		
	def visit_Name(self, node, frame):
		if node.name in frame.identifiers.declared:
			self.write(node.name)
		else:
			self.write('ctx.%s' % node.name)
	
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
			self.write('Jasinja.utils.slice(')
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
			self.visit(node.node, frame)
			self.write('[')
			self.visit(node.arg, frame)
			self.write(']')
	
	def for_targets(self, node, loopvar, frame, pre=''):
		
		self.newline()
		if isinstance(node, nodes.Tuple):
			for i, target in enumerate(node.items):
				frame.identifiers.declared.add(target.name)
				self.write('var ')
				self.visit(target, frame)
				bits = pre + loopvar, pre + loopvar, i
				self.write(' = %s.iter[%s.i][%s];' % bits)
				self.newline()
		else:
			frame.identifiers.declared.add(node.name)
			self.write('var ')
			self.visit(node, frame)
			self.write(' = %s.iter[%s.i];' % (pre + loopvar, pre + loopvar))
	
	def visit_For(self, node, frame):
		
		before = frame.identifiers.declared.copy()
		loopvar = nextvar(frame, '_loopvar')
		if loopvar.endswith('0') and 'loop' in frame.identifiers.declared:
			self.writeline('var _pre_loop = loop;')
		
		frame.identifiers.declared.add(loopvar)
		frame.identifiers.declared.add('loop')
		if node.test:
			
			self.newline()
			self.write('var f%s = Jasinja.utils.loop(' % loopvar)
			self.visit(node.iter, frame)
			self.write(');')
			self.newline()
			
			vars = (loopvar,) * 4
			self.writeline('var g%s = [];' % loopvar)
			self.writeline('for (f%s.i = 0; f%s.i < f%s.l; f%s.i++) {' % vars)
			self.indent()
			
			self.newline()
			self.for_targets(node.target, loopvar, frame, 'f')
			self.newline()
			self.write('if (!')
			self.visit(node.test, frame)
			self.write(') continue;')
			self.newline()
			
			bits = (loopvar,) * 3
			self.write('g%s.push(f%s.iter[f%s.i]);' % bits)
			self.outdent()
			self.writeline('}')
			self.writeline('')
		
		self.newline()
		self.write('var %s = Jasinja.utils.loop(' % loopvar)
		if not node.test:
			self.visit(node.iter, frame)
		else:
			self.write('g%s' % loopvar)
		self.write(');')
		
		self.newline()
		vars = (loopvar,) * 4
		self.write('for (%s.i = 0; %s.i < %s.l; %s.i++) {' % vars)
		self.indent()
		self.writeline('')
		
		self.for_targets(node.target, loopvar, frame)
		self.writeline('loop = %s;' % loopvar);
		self.writeline('loop.update();')
		self.writeline('')
		
		for n in node.body:
			self.visit(n, frame)
		
		self.writeline('')
		self.outdent()
		self.writeline('}')
		if loopvar[8:] != '0':
			self.writeline('loop = _loopvar%s;' % (int(loopvar[8:]) - 1))
		
		frame.identifiers.declared = before
		if loopvar.endswith('0') and 'loop' in frame.identifiers.declared:
			self.writeline('loop = _pre_loop;')
	
	def visit_Filter(self, node, frame):
		
		self.write('Jasinja.filters.' + node.name + '(')
		self.visit(node.node, frame)
		
		if not node.args and not node.kwargs:
			self.write(')')
			return
		
		if node.args and not node.kwargs:
			for n in node.args:
				self.write(', ')
				self.visit(n, frame)
			self.write(')')
			return
		
		spec = dict((k, i) for (i, k) in enumerate(FILTER_ARGS[node.name]))
		args = [None] * (len(spec))
		for i, arg in enumerate(node.args):
			args[i] = arg
		for arg in node.kwargs:
			args[spec[arg.key]] = arg.value
		while args and args[-1] is None:
			args.pop()
		
		for n in args:
			self.write(', ')
			if n is None:
				self.write('undefined')
			else:
				self.visit(n, frame)
		self.write(')')
	
	def visit_Test(self, node, frame):
		self.write('Jasinja.tests.' + node.name + '(')
		self.visit(node.node, frame)
		self.write(')')
	
	def visit_Not(self, node, frame):
		self.write('!')
		self.visit(node.node, frame)
	
	def visit_Concat(self, node, frame):
		self.write('Jasinja.utils.strjoin(')
		first = True
		for n in node.nodes:
			if not first: self.write(', ')
			self.visit(n, frame)
			first = False
		self.write(')')
	
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
	
	def visit_Compare(self, node, frame):
		
		if node.ops[0].op not in ('in', 'notin'):
			CodeGenerator.visit_Compare(self, node, frame)
			return
		
		oper = node.ops[0]
		if oper.op == 'notin':
			self.write('!')
		self.write('Jasinja.utils.contains(')
		self.visit(node.expr, frame)
		self.write(', ')
		self.visit(oper.expr, frame)
		self.write(')')
	
	def binop(op): # copied from CodeGenerator:binop()
		def visitor(self, node, frame):
			self.write('(')
			self.visit(node.left, frame)
			self.write(' %s ' % op)
			self.visit(node.right, frame)
			self.write(')')
		return visitor
	
	visit_And = binop('&&')
	visit_Or = binop('||')
		
def compile(env, src):
	return Parser(env, src, 'test', 'test.html').parse()

def generate(env, templates=None):
	
	if templates is None:
		templates = env.loader.list_templates()
	
	out = []
	for name in templates:
		src, fn, up = env.loader.get_source(env, name)
		gen = JSCodeGen(env, name, fn, None, False)
		gen.visit(compile(env, src))
		out.append(gen.stream.getvalue().rstrip())
	
	src = open(META).read()
	return src.replace('%(templates)s', ',\n\t\n'.join(out))

def pygen(env, name):
	src, fn, up = env.loader.get_source(env, name)
	gen = CodeGenerator(env, 'blah', 'index.html', None, False)
	gen.visit(compile(env, src))
	return gen.stream.getvalue()
