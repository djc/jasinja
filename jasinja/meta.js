var utils = {

    "slice": function(val, start, stop) {
        if (typeof(val) == "string") {
            return val.substring(start, stop);
        } else if (val instanceof Array) {
            return val.slice(start, stop);
        }
    },

    "loop": {
        "index": function(i, l) { return i + 1; },
        "index0": function(i, l) { return i; },
        "revindex": function(i, l) { return l - i; },
        "revindex0": function(i, l) { return l - i - 1; },
        "first": function(i, l) { return !i; },
        "last": function(i, l) { return i == l - 1; },
        "length": function(i, l) { return l; },
        "cycle": function(i, l) {
            return function() { return arguments[i % arguments.length]; }
        }
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
    }

};

var filters = {

    "format": function(fmt, vals) {
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
	        } else if (type == "%") {
	        	fmt = fmt.replace("%%", "%");
	        }
        }
        return fmt;
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
