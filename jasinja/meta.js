var Jasinja = {
		
	"utils": {
		
		"extend": function(base, child) {
			if (child == undefined) return base;
			var current = {"blocks": {}};
			for (var key in base.blocks) {
				if (!child.blocks[key]) {
					current.blocks[key] = base.blocks[key];
				} else {
					current.blocks[key] = child.blocks[key];
				}
			}
			return current;
		},
		
		"slice": function(val, start, stop) {
			if (typeof(val) == "string") {
				return val.substring(start, stop);
			} else if (val instanceof Array) {
				return val.slice(start, stop);
			}
		},
		
		"loop": function(iter) {
			function LoopObject() {
				this.iter = iter;
				this.l = iter.length;
				this.i = 0;
				this.update = function() {
					if (arguments.length) this.i = arguments[0];
					this.index = this.i + 1;
					this.index0 = this.i;
					this.revindex = this.l - this.i;
					this.revindex0 = this.l - this.i - 1;
					this.first = !this.i;
					this.last = this.i == this.l - 1;
				}
				this.cycle = function() {
					return arguments[this.index0 % arguments.length];
				};
			}
			return new LoopObject();
		},
		
		"contains": function(n, hs) {
			if (hs instanceof Array) {
				for (var i = 0; i < hs.length; i++) {
					if (hs[i] == n) return true;
				}
				return false;
			} else if (typeof(hs) == "string") {
				return !!hs.match(RegExp(n));
			} else if (typeof(hs) == "object") {
				return hs[n] !== undefined;
			} else {
				throw new TypeError("containment is undefined: " + n + " in " + JSON.stringify(hs));
			}
		},
		
		"strjoin": function() {
			var buf = [];
			for (var i = 0; i < arguments.length; i++) {
				buf.push(arguments[i].toString());
			}
			return buf.join("");
		},
		
		"strmul": function(s, n) {
			var buf = [];
			for (var i = 0; i < n; i++) {
				buf.push(s);
			}
			return buf.join('');
		},
		
	},
	
	"filters": {
		
		"attr": function(obj, name) {
			return obj[name];
		},
		
		"abs": function(n) {
			return Math.abs(n);
		},
		
		"batch": function(ls, num, fill) {
			fill = fill === undefined ? null : fill;
			var res = [];
			var tmp = [];
			for (var i = 0; i < ls.length; i++) {
				if (tmp.length == num) {
					res.push(tmp);
					tmp = [];
				}
				tmp.push(ls[i]);
			}
			if (tmp.length && tmp.length < num && fill) {
				for (var i = num - 1; i > 0; i--) {
					tmp.push(fill);
				}
			}
			if (tmp.length) res.push(tmp);
			return res;
		},
		
		"capitalize": function(s) {
			s = s.toLowerCase();
			return s.charAt(0).toUpperCase() + s.substring(1);
		},
		
		"center": function(s, width) {
			width = arguments[1] ? width : 80;
			var pre = Math.floor((width - s.length) / 2);
			var post = Math.ceil((width - s.length) / 2);
			var buf = [];
			for (var i = 0; i < pre; i++) {
				buf.push(' ');
			}
			buf.push(s);
			for (var i = 0; i < post; i++) {
				buf.push(' ');
			}
			return buf.join('');
		},
		
		"count": function(val) {
			return this.length(val);
		},
		
		"d": function(val, alt, bool) {
			return this.default(val, alt, bool);
		},
		
		"default": function(val, alt, bool) {
			bool = bool || false;
			if (!bool) {
				return val !== undefined ? val : alt;
			} else {
				return val ? val : alt;
			}
		},
		
		"dictsort": function(val) {
			var keys = this.list(val);
			keys.sort();
			var ls = [];
			for (var i = 0; i < keys.length; i++) {
				ls.push([keys[i], val[keys[i]]]);
			}
			return ls;
		},
		
		"e": function(s) {
			return this.escape(s);
		},
		
		"escape": function(s) {
			s = s.replace('&', '&amp;');
			s = s.replace('<', '&lt;');
			s = s.replace('>', '&gt;');
			s = s.replace('"', '&#34;');
			s = s.replace("'", '&#39;');
			return s;
		},
		
		"forceescape": function(s) {
			return this.escape(s);
		},
		
		"filesizeformat": function(val, binary) {
			binary = arguments[1] ? binary : false;
			var bytes = parseFloat(val);
			var base = binary ? 1024 : 1000;
			var middle = binary ? 'i' : '';
			if (bytes < base) {
				var multi = bytes == 1 ? '' : 's';
				return this.format("%i Byte%s", bytes, multi);
			} else if (bytes < base * base) {
				return this.format("%.1f K%sB", bytes / base, middle);
			} else if (bytes < base * base * base) {
				return this.format("%.1f M%sB", bytes / (base * base), middle);
			}
			return this.format("%.1f G%sB", bytes / (base * base * base), middle);
		},
		
		"first": function(val) {
			if (typeof(val) == "string") {
				return val.charAt(0);
			} else if (val instanceof Array) {
				return val[0];
			}
		},
		
		"float": function(val) {
			return parseFloat(val) || 0.0;
		},
		
		"format": function(fmt) {
			var vals = Array.prototype.slice.call(arguments, 1);
			var regex = new RegExp('\%([0 ]?)((?:[0-9]+)?)(\.[0-9]+)?([fis%])');
			while (regex.test(fmt)) {
				
				var parts = regex.exec(fmt);
				var ext = parts[1] ? parts[1] : ' ';
				var wantlen = parseInt(parts[2]);
				var type = parts[0].substring(parts[0].length - 1);
				var val = vals.shift();
				
				if (type == "f") {
					
					val = parseFloat(val);
					if (parts[3]) {
						val = val.toFixed(parseInt(parts[3].substring(1)));
					} else {
						val = val.toString();
					}
					if (val.length < wantlen) {
						val = Jasinja.utils.strmul(ext, wantlen - val.length) + val;
					}
					fmt = fmt.replace(parts[0], val);
					
				} else if (type == "i") {
					
					val = parseInt(val).toString();
					if (val.length < wantlen) {
						val = Jasinja.utils.strmul(ext, wantlen - val.length) + val;
					}
					fmt = fmt.replace(parts[0], val);
					
				} else if (type == "s") {
					
					if (val.length < wantlen) {
						val = Jasinja.utils.strmul(ext, wantlen - val.length) + val;
					}
					fmt = fmt.replace(parts[0], val.toString());
					
				} else if (type == "%") {
					fmt = fmt.replace("%%", "%");
				}
				
			}
			return fmt;
		},
		
		"groupby": function(ls, attr) {
			
			var groups = {};
			for (var i = 0; i < ls.length; i++) {
				var key = ls[i][attr];
				if (!(key in groups)) groups[key] = [];
				groups[key].push(ls[i]);
			}
			var res = [];
			for (var key in groups) {
				res.push({0: key, grouper: key, 1: groups[key], list: groups[key]});
			}
			
			return res;
			
		},
		
		"indent": function(s, w, first) {
			w = w === undefined ? 4 : w;
			first = first === undefined ? false : first;
			var indent = Jasinja.utils.strmul(' ', w);
			var res = s.split('\n').join('\n' + indent);
			if (first) res = indent + res;
			return res;
		},
		
		"int": function(val) {
			return Math.floor(val) || 0;
		},
		
		"last": function(val) {
			if (typeof(val) == "string") {
				return val.charAt(val.length - 1);
			} else if (val instanceof Array) {
				return val[val.length - 1];
			}
		},
		
		"length": function(val) {
			return val.length;
		},
		
		"list": function(val) {
			if (val instanceof Array) {
				return val;
			} else if (typeof(val) == "string") {
				var ls = [];
				for (var i = 0; i < val.length; i++) {
					ls.push(val.charAt(i));
				}
				return ls;
			} else if (typeof(val) == "object") {
				var ls = [];
				for (var key in val) {
					ls.push(key);
				}
				return ls;
			} else {
				throw new TypeError("containment is undefined");
			}
		},
		
		"lower": function(s) {
			return s.toLowerCase();
		},
		
		"join": function(val, d) {
			return val.join(d);
		},
		
		"random": function(ls) {
			return ls[Math.floor(Math.random() * ls.length)]
		},
		
		"replace": function(s, o, n) {
			return s.replace(o, n, 'g');
		},
		
		"reverse": function(r) {
			var c = r.slice(0);
			c.reverse();
			return c;
		},
		
		"round": function(val) {
			var num = arguments[1] ? arguments[1] : 0;
			var mul = num ? num * 10 : 1;
			return Math.round(val * mul) / mul;
		},
		
		"safe": function(s) {
			return s;
		},
		
		"slice": function(ls, num, fill) {
			var ssize = Math.floor(ls.length / num);
			var extra = ls.length % num;
			var offset = 0;
			var res = [];
			var offset = 0;
			for (var i = 0; i < num; i++) {
				var start = offset + i * ssize;
				if (i < extra) offset += 1;
				var end = offset + (i + 1) * ssize;
				var tmp = ls.slice(start, end);
				if (fill !== undefined && i >= extra) {
					tmp.push(fill);
				}
				res.push(tmp);
			}
			return res;
		},
		
		"sort": function(val) {
			var c = val.slice(0);
			c.sort();
			return c;
		},
		
		"string": function(val) {
			return val.toString();
		},
		
		"sum": function(ls, attrib, start) {
			start = start === undefined ? 0 : start;
			for (var i = 0; i < ls.length; i++) {
				if (attrib === undefined) start += ls[i];
				else start += ls[i][attrib];
			}
			return start;
		},
		
		"title": function(s) {
			return s.replace(/[a-zA-Z]+/g, this.capitalize);
		},
		
		"trim": function(s) {
			return s.replace(/^\s+|\s+$/g, '');
		},
		
		"truncate": function(s, len, kill, end) {
			
			len = len === undefined ? 255 : len;
			if (s.length < len) return s;
			kill = kill === undefined ? false : kill;
			end = end === undefined ? '...' : end;
			if (kill) return s.substring(0, len) + end;
			
			var words = s.split(' ');
			var result = [];
			var m = 0;
			for (var i = 0; i < words.length; i++) {
				m += words[i].length + 1
				if (m > len) break;
				result.push(words[i]);
			}
			result.push(end);
			return result.join(' ');
			
		},
		
		"upper": function(s) {
			return s.toUpperCase();
		},
		
		"wordcount": function(s) {
			return s.split(/\s+/g).length;
		},
		
		"xmlattr": function(d, space) {
			space = space === undefined ? true : space;
			var tmp = [];
			for (var k in d) {
				if (d[k] === null || d[k] === undefined) continue;
				tmp.push(this.format('%s="%s"', this.escape(k), this.escape(d[k])));
			}
			var res = (space ? ' ' : '') + tmp.join(' ');
			return res;
		}
		
	},
		
	"tests": {
		"callable": function(val) {
			return typeof(val) == "function";
		},
		"defined": function(val) {
			return val !== undefined;
		},
		"divisibleby": function(val, num) {
			return !(val % num);
		},
		"even": function(val) {
			return this.divisibleby(val, 2);
		},
		"lower": function(val) {
			return val.toLowerCase() == val;
		},
		"none": function(val) {
			return val === null;
		},
		"number": function(val) {
			return typeof(val) == "number";
		},
		"odd": function(val) {
			return !this.divisibleby(val, 2);
		},
		"undefined": function(val) {
			return val === undefined;
		},
		"upper": function(val) {
			return val.toUpperCase() == val;
		},
		"string": function(val) {
			return typeof(val) == "string";
		}
	},
	
	"templates": {
		
		%(templates)s
		
	}
	
};
