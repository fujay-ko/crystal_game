window.Game = window.Game || {};

(function(G) {

var C = G.CONST;
var images = {};
var audio = {};
var assetsLoaded = 0;
var totalAssets = 0;

G.getImage = function(key) { return images[key]; };
G.getAudio = function(key) { return audio[key]; };

G.imgReady = function(key) {
    return images[key] && images[key].complete;
};

G.loadAssets = function(callback) {
    var path = C.ASSETS_PATH;
    totalAssets = Object.keys(G.IMAGE_FILES).length;

    // Load images
    for (var key in G.IMAGE_FILES) {
        (function(k) {
            var img = new Image();
            img.src = path + G.IMAGE_FILES[k];
            img.onload = function() { assetsLoaded++; checkDone(); };
            img.onerror = function() {
                console.error('Failed to load: ' + k);
                assetsLoaded++; checkDone();
            };
            images[k] = img;
        })(key);
    }

    // Load audio
    for (var key2 in G.AUDIO_FILES) {
        (function(k) {
            audio[k] = new Audio(path + G.AUDIO_FILES[k]);
        })(key2);
    }

    function checkDone() {
        if (assetsLoaded === totalAssets) {
            if (callback) callback();
        }
    }
};

})(window.Game);
