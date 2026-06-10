window.Game = window.Game || {};

(function(G) {

var C = G.CONST;

// Game logic state (modified by Skulpt during execution)
var g = {
    row: 4, col: 3, dir: 0,
    crystals_on_map: [],
    crystals_collected: 0
};

// Display state (updated during animation playback)
var d = {
    row: 4, col: 3, dir: 0,
    crystals_on_map: [],
    crystals_collected: 0
};

// Stage progress
var currentStageNum = 1;
var maxUnlockedStage = 1;
var userCodes = {};
var stageEndPositions = { 0: { row: 4, col: 3, dir: 0 } };

var animationQueue = [];
var isAnimating = false;
var execTimeoutId = null;
var _muted = false;

// === Getters ===
G.getG = function() { return g; };
G.getD = function() { return d; };
G.getCurrentStage = function() { return currentStageNum; };
G.getMaxUnlockedStage = function() { return maxUnlockedStage; };
G.getUserCodes = function() { return userCodes; };
G.getStageEndPositions = function() { return stageEndPositions; };
G.getAnimationQueue = function() { return animationQueue; };
G.isAnimating = function() { return isAnimating; };
G.getExecTimeoutId = function() { return execTimeoutId; };

// === Setters ===
G.setAnimating = function(val) { isAnimating = val; };
G.setExecTimeoutId = function(id) { execTimeoutId = id; };
G.setCurrentStage = function(n) { currentStageNum = n; };
G.setMaxUnlockedStage = function(n) { maxUnlockedStage = n; };
G.isMuted = function() { return _muted; };
G.toggleMute = function() { _muted = !_muted; return _muted; };
G.setMuted = function(val) { _muted = val; };

// === Stage management ===

G.fullReset = function() {
    userCodes = {};
    stageEndPositions = { 0: { row: 4, col: 3, dir: 0 } };
    maxUnlockedStage = 1;
    currentStageNum = 1;
    G.applyStageState(1);
    G.syncToDisplay();
};

G.applyStageState = function(stageNum) {
    var collected = stageNum - 1;
    var pos = stageEndPositions[stageNum - 1] || { row: 4, col: 3, dir: 0 };
    g.row = pos.row; g.col = pos.col; g.dir = pos.dir;
    g.crystals_collected = collected;
    g.crystals_on_map = G.CRYSTAL_CONFIG.slice(collected).map(function(c) {
        return { row: c.row, col: c.col, colorKey: c.colorKey };
    });
};

G.syncToDisplay = function() {
    d.row = g.row; d.col = g.col; d.dir = g.dir;
    d.crystals_on_map = g.crystals_on_map.map(function(c) {
        return { row: c.row, col: c.col, colorKey: c.colorKey };
    });
    d.crystals_collected = g.crystals_collected;
    animationQueue = [];
    isAnimating = false;
};

G.recordEndPosition = function(collectedCount) {
    stageEndPositions[collectedCount] = { row: g.row, col: g.col, dir: g.dir };
};

})(window.Game);
