var utils = {

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

};

var filters = {
    
    "attr": function(obj, name) {
        return obj[name];
    },
    
    "abs": function(n) {
        return Math.abs(n);
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
        return filters.length(val);
    },
    
    "d": function(val, alt) {
        return filters.default(val, alt);
    },
    
    "default": function(val, alt) {
        return val ? val : alt;
    },
    
    "dictsort": function(val) {
        var keys = filters.list(val);
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
    
    "filesizeformat": function(val, binary) {
    	binary = arguments[1] ? binary : false;
    	var bytes = parseFloat(val);
    	var base = binary ? 1024 : 1000;
    	var middle = binary ? 'i' : '';
    	if (bytes < base) {
    		var multi = bytes == 1 ? '' : 's';
    	    return filters.format("%i Byte%s", bytes, multi);
    	} else if (bytes < base * base) {
    	    return filters.format("%.1f K%sB", bytes / base, middle);
    	} else if (bytes < base * base * base) {
    	    return filters.format("%.1f M%sB", bytes / (base * base), middle);
    	}
    	return filters.format("%.1f G%sB", bytes / (base * base * base), middle);
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
	        		val = utils.strmul(ext, wantlen - val.length) + val;
	        	}
	        	fmt = fmt.replace(parts[0], val);
	        	
	        } else if (type == "i") {
	        	
	            val = parseInt(val).toString();
	            if (val.length < wantlen) {
	            	val = utils.strmul(ext, wantlen - val.length) + val;
	            }
	            fmt = fmt.replace(parts[0], val);
	            
	        } else if (type == "s") {
	        	
	        	if (val.length < wantlen) {
	        		val = utils.strmul(ext, wantlen - val.length) + val;
	        	}
	        	fmt = fmt.replace(parts[0], val.toString());
	        	
	        } else if (type == "%") {
	        	fmt = fmt.replace("%%", "%");
	        }
	        
        }
        return fmt;
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
    
    "sort": function(val) {
        var c = val.slice(0);
        c.sort();
        return c;
    },
    
    "string": function(val) {
        return val.toString();
    },
    
    "sum": function(ls, start) {
        start = start === undefined ? 0 : start;
        for (var i = 0; i < ls.length; i++) {
            start += ls[i];
        }
        return start;
    },
    
    "title": function(s) {
        return s.replace(/[a-zA-Z]+/g, filters.capitalize);
    },
    
    "upper": function(s) {
        return s.toUpperCase();
    }

};

var tests = {
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
        return tests.divisibleby(val, 2);
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
        return !tests.divisibleby(val, 2);
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
}

var templates = {
[DATA]
    
};
