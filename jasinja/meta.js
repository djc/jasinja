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
            throw new TypeError("containment is undefined");
        }
    },

    "strjoin": function() {
        var buf = [];
        for (var i = 0; i < arguments.length; i++) {
            buf.push(arguments[i].toString());
        }
        return buf.join("");
    }

};

var filters = {
    
    "abs": function(n) {
        return Math.abs(n);
    },
    
    "capitalize": function(s) {
        return s.charAt(0).toUpperCase() + s.substring(1);
    },
    
    "count": function(val) {
        return filters.length(val);
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
    
    "float": function(val) {
        return parseFloat(val) || 0.0;
    },
    
    "format": function(fmt) {
        var vals = Array.prototype.slice.call(arguments, 1);
        var regex = new RegExp('\%.*?[fis%]');
        while (regex.test(fmt)) {
	        var m = regex.exec(fmt)[0];
	        var type = m.substring(m.length - 1);
        	var val = vals.shift();
	        if (type == "f") {
	        	val = parseFloat(val);
	        	var mods = m.substring(1, m.length - 1).split('.');
	        	if (mods[1]) val = val.toFixed(parseInt(mods[1], 10));
	        	fmt = fmt.replace(m, val);
	        } else if (type == "s") {
	        	fmt = fmt.replace(m, val.toString());
	        } else if (type == "%") {
	        	fmt = fmt.replace("%%", "%");
	        }
        }
        return fmt;
    },
    
    "int": function(val) {
        return Math.floor(val) || 0;
    },
    
    "length": function(val) {
        return val.length;
    },
    
    "join": function(val, d) {
        return val.join(d);
    },
    
    "sort": function(val) {
        var c = val.slice(0);
        c.sort();
        return c;
    },
    
    "reverse": function(r) {
    	var c = r.slice(0);
    	c.reverse();
    	return c;
    }

};

var tests = {
    "none": function(val) {
        return val === null;
    },
    "defined": function(val) {
        return val !== undefined;
    }
}

var templates = {
[DATA]
    
};
