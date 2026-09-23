window.Game = window.Game || {};

(function(G) {

G.cloneArray = function(arr) {
    return arr.map(function(item) {
        if (Array.isArray(item)) return G.cloneArray(item);
        if (item && typeof item === 'object') return G.cloneObj(item);
        return item;
    });
};

G.cloneObj = function(obj) {
    var cloned = {};
    for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
            var val = obj[key];
            if (Array.isArray(val)) cloned[key] = G.cloneArray(val);
            else if (val && typeof val === 'object') cloned[key] = G.cloneObj(val);
            else cloned[key] = val;
        }
    }
    return cloned;
};

G.log = function(text) {
    var out = document.getElementById('output');
    if (out) {
        out.textContent += text + '\n';
        out.scrollTop = out.scrollHeight;
    }
    console.log(text);
};

G.clearOutput = function() {
    var out = document.getElementById('output');
    if (out) out.textContent = '';
};

// Timer helper. Uses setTimeout (not rAF) so animation keeps progressing
// even when the tab is in the background (rAF gets throttled/paused).
G.delay = function(ms, callback) {
    setTimeout(callback, ms);
};

})(window.Game);
