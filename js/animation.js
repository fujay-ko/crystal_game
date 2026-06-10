window.Game = window.Game || {};

(function(G) {

var queue;
var stageClearOverlay = null;
var stageClearTimer = null;

function init() {
    queue = G.getAnimationQueue();
    stageClearOverlay = document.getElementById('stage-clear-overlay');
}

function showOverlay(show) {
    if (!stageClearOverlay) return;
    stageClearOverlay.classList.toggle('show', show);
}

function enableRunButton(enabled) {
    var btn = document.getElementById('btn-run');
    if (!btn) return;
    btn.disabled = !enabled;
    btn.innerHTML = enabled
        ? '▶ 執行程式 <span class="key-hint">(Ctrl+Enter)</span>'
        : '執行中...';
}

function processNext() {
    var queueNow = G.getAnimationQueue();
    if (queueNow.length === 0) {
        G.setAnimating(false);
        G.log('--- 動作結束 ---');
        enableRunButton(true);
        return;
    }

    G.setAnimating(true);
    var action = queueNow.shift();
    var d = G.getD();
    var audio = G.getAudio;

    switch (action.type) {
        case 'move':
            d.row = action.row;
            d.col = action.col;
            G.drawGame();
            G.delay(300, processNext);
            break;

        case 'turn':
            d.dir = action.dir;
            G.drawGame();
            G.delay(200, processNext);
            break;

        case 'get':
            d.crystals_on_map = d.crystals_on_map.filter(function(c) {
                return !(c.row === action.row && c.col === action.col);
            });
            d.crystals_collected++;
            if (!G.isMuted()) {
                var getSfx = audio('get');
                if (getSfx) getSfx.play().catch(function() {});
            }
            G.drawGame();
            G.delay(500, processNext);
            break;

        case 'stage_clear':
            showOverlay(true);
            G.log('--- 關卡完成！準備進入下一關 ---');
            G.delay(1200, function() {
                showOverlay(false);
                advanceToNextStage();
                G.setAnimating(false);
                enableRunButton(true);
            });
            break;

        case 'crash':
            if (!G.isMuted()) {
                var knockSfx = audio('knock');
                if (knockSfx) knockSfx.play().catch(function() {});
            }
            G.drawGame('defeat');
            G.setAnimating(false);
            enableRunButton(true);
            break;

        case 'fail':
            if (!G.isMuted()) {
                var failSfx = audio('fail');
                if (failSfx) failSfx.play().catch(function() {});
            }
            G.drawGame('defeat');
            G.setAnimating(false);
            enableRunButton(true);
            break;

        case 'win':
            if (!G.isMuted()) {
                var winSfx = audio('victory');
                if (winSfx) winSfx.play().catch(function() {});
            }
            G.drawGame('victory');
            G.setAnimating(false);
            enableRunButton(true);
            G.log('=== 恭喜！遊戲全部通關！ ===');
            break;
    }
}

function advanceToNextStage() {
    var d = G.getD();
    var nextStage = d.crystals_collected + 1;
    if (nextStage > G.CONST.STAGE_COUNT) return;

    var ed = G.getEditor();
    var userCodes = G.getUserCodes();
    var currentStageNum = G.getCurrentStage();

    if (ed) userCodes[currentStageNum] = ed.getValue();

    if (nextStage > G.getMaxUnlockedStage()) {
        G.setMaxUnlockedStage(nextStage);
    }
    G.setCurrentStage(nextStage);
    G.applyStageState(nextStage);
    G.syncToDisplay();
    G.updateEditorContent(nextStage);
    G.updateStageSelectorUI();
    G.log('>>> 解鎖並進入 Stage ' + nextStage + ' <<<');
}

G.startAnimation = function() {
    init();
    processNext();
};

G.cancelStageClearTimer = function() {
    if (stageClearTimer) {
        clearTimeout(stageClearTimer);
        stageClearTimer = null;
    }
};

})(window.Game);
