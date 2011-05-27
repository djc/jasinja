var filters = {

    "_slice": function(val, start, stop) {
        if (typeof(val) == "string") {
            return val.substring(start, stop);
        } else if (val instanceof Array) {
            return val.slice(start, stop);
        }
    },

    "format": function(fmt, vals) {
        var regex = new RegExp('\%.*?[fis]');
        while (regex.test(fmt)) {
	        var m = regex.exec(fmt)[0];
	        var type = m.substring(m.length - 1);
        	var val = vals.shift();
	        if (type == "f") {
	        	val = parseFloat(val);
	        	var mods = m.substring(1, m.length - 1).split('.');
	        	if (mods[1]) val = val.toFixed(parseInt(mods[1], 10));
	        	fmt = fmt.replace(m, val);
	        }
        }
        return fmt;
    }

};

var tests = {
    "none": function(val) {
        return val === null;
    }
}

var templates = {
[DATA]
    
};
