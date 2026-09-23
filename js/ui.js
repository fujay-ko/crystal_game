window.Game = window.Game || {};

(function(G) {

var C = G.CONST;
var editor = null;
var _lastStepCount = 0;

// ============================================================
//  CodeMirror Editor
// ============================================================
G.initEditor = function() {
    editor = CodeMirror.fromTextArea(document.getElementById('code'), {
        mode: { name: 'python', version: 3, singleLineStringErrors: false },
        theme: 'dracula',
        lineNumbers: true,
        indentUnit: 4,
        matchBrackets: true,
        extraKeys: {
            'Tab': function(cm) {
                if (cm.somethingSelected()) {
                    cm.indentSelection('add');
                } else {
                    cm.replaceSelection('    ', 'end');
                }
            }
        }
    });
    return editor;
};

G.getEditor = function() { return editor; };

G.updateEditorContent = function(level) {
    var userCodes = G.getUserCodes();
    var code = userCodes[level] !== undefined ? userCodes[level] : (G.LEVELS[level] || '# 恭喜通關！');
    editor.setValue(code);
    G.updateStageSelectorUI();
};

// ============================================================
//  Stage Selector UI
// ============================================================
G.updateStageSelectorUI = function() {
    var current = G.getCurrentStage();
    var maxUnlocked = G.getMaxUnlockedStage();
    for (var i = 1; i <= 5; i++) {
        var btn = document.getElementById('sbtn-' + i);
        if (!btn) continue;
        btn.classList.remove('active', 'completed');
        if (i < maxUnlocked) {
            btn.classList.add('completed');
            btn.textContent = '\u2705 S' + i;
        } else if (i === maxUnlocked && i !== current) {
            btn.textContent = '\u2B50 S' + i;
        } else if (i > maxUnlocked) {
            btn.textContent = '\uD83D\uDD12 S' + i;
        } else {
            btn.textContent = '\u2B50 S' + i;
        }
        if (i === current) btn.classList.add('active');
    }
    document.getElementById('level-indicator').textContent = 'Stage ' + current;
};

G.selectStage = function(stageNum) {
    if (stageNum > G.getMaxUnlockedStage()) {
        G.log('Stage ' + stageNum + ' 尚未解鎖，請先完成前面的關卡！');
        return;
    }
    if (G.isAnimating()) return;

    var userCodes = G.getUserCodes();
    userCodes[G.getCurrentStage()] = editor.getValue();

    G.setCurrentStage(stageNum);
    G.applyStageState(stageNum);
    G.syncToDisplay();
    G.updateEditorContent(stageNum);
    G.drawGame();
    G.log('>>> 切換到 Stage ' + stageNum + ' <<<');
    G.saveProgress();
};

G.retryCurrentStage = function() {
    if (G.isAnimating()) return;
    var userCodes = G.getUserCodes();
    userCodes[G.getCurrentStage()] = editor.getValue();
    G.applyStageState(G.getCurrentStage());
    G.syncToDisplay();
    G.drawGame();
    G.log('\u21BA 重試 Stage ' + G.getCurrentStage());
};

G.confirmFullReset = function() {
    if (confirm('\u26A0 確定要從頭開始嗎？\n所有關卡的程式碼與進度都會清除！')) {
        G.fullReset();
        G.updateEditorContent(1);
        G.updateStageSelectorUI();
        G.drawGame();
        G.log('遊戲已完全重置 (Stage 1)');
        G.saveProgress();
    }
};

// ============================================================
//  Skulpt / Python Bridge
// ============================================================
function builtinRead(x) {
    if (Sk.builtinFiles === undefined || Sk.builtinFiles['files'][x] === undefined)
        throw "File not found: '" + x + "'";
    return Sk.builtinFiles['files'][x];
}

function sk_none() { return Sk.builtin.none.none$; }
function sk_bool(b) { return new Sk.builtin.bool(b); }
function sk_int(n) { return new Sk.builtin.int_(n); }

function cancelExecTimeout() {
    var id = G.getExecTimeoutId();
    if (id) {
        clearTimeout(id);
        G.setExecTimeoutId(null);
    }
}

G.runPython = function() {
    if (G.isAnimating()) return;

    G.syncToDisplay();
    cancelExecTimeout();

    var btn = document.getElementById('btn-run');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '執行中...';
    }

    var prog = editor.getValue();
    var stageNum = G.getCurrentStage();
    var funcName = 'stage' + stageNum;

    var runCode = prog + '\n\n';
    runCode += "if '" + funcName + "' in globals():\n";
    runCode += '    ' + funcName + '()\n';

    G.log('--- 執行 Stage ' + stageNum + ' ---');

    var stepCount = 0;
    var limitHit = false;
    _lastStepCount = 0;

    // 步數上限守衛：五個遊戲 API 共用，超限只推一次 fail 並回傳 false
    function guardStep() {
        stepCount++;
        if (stepCount > C.MAX_STEPS || G.getAnimationQueue().length > 500) {
            if (!limitHit) {
                limitHit = true;
                G.getAnimationQueue().push({ type: 'fail' });
                G.log('[錯誤] 指令數量過多，可能有無限迴圈！');
            }
            return false;
        }
        return true;
    }

    // 指令即時紀錄：讓學生把程式碼與角色動作一一對照
    function traceCmd(name) {
        G.log('  [' + stepCount + '] ' + name + '()');
    }

    Sk.configure({
        output: G.log,
        read: builtinRead,
        syspath: ['skulpt-stdlib'],
        retries: -1,
        execLimit: 5000
    });

    // Timeout protection
    var timeoutId = setTimeout(function() {
        G.log('[錯誤] 執行逾時（超過 ' + (C.EXEC_TIMEOUT_MS / 1000) + ' 秒），可能是無限迴圈，已強制中止');
        G.getAnimationQueue().push({ type: 'fail' });
        cancelExecTimeout();
        // 播放失敗動畫（播完後 startAnimation 會自動恢復按鈕）
        G.startAnimation();
    }, C.EXEC_TIMEOUT_MS);
    G.setExecTimeoutId(timeoutId);

    // Python API
    Sk.builtins.move_forward = new Sk.builtin.func(function() {
        if (!guardStep()) return sk_none();
        traceCmd('move_forward');
        var g = G.getG();
        var nr = g.row, nc = g.col;
        if (g.dir === 0) nr--;
        else if (g.dir === 1) nc++;
        else if (g.dir === 2) nr++;
        else if (g.dir === 3) nc--;

        var isWall = (nr < 0 || nr >= 8 || nc < 0 || nc >= 8) || G.MAP_DATA[nr][nc] === 0;
        if (isWall) {
            G.getAnimationQueue().push({ type: 'crash' });
        } else {
            g.row = nr; g.col = nc;
            G.getAnimationQueue().push({ type: 'move', row: g.row, col: g.col });
        }
        return sk_none();
    });

    Sk.builtins.turn_left = new Sk.builtin.func(function() {
        if (!guardStep()) return sk_none();
        traceCmd('turn_left');
        var g = G.getG();
        g.dir = (g.dir - 1 + 4) % 4;
        G.getAnimationQueue().push({ type: 'turn', dir: g.dir });
        return sk_none();
    });

    Sk.builtins.turn_right = new Sk.builtin.func(function() {
        if (!guardStep()) return sk_none();
        traceCmd('turn_right');
        var g = G.getG();
        g.dir = (g.dir + 1) % 4;
        G.getAnimationQueue().push({ type: 'turn', dir: g.dir });
        return sk_none();
    });

    Sk.builtins.get_crystal = new Sk.builtin.func(function() {
        if (!guardStep()) return sk_none();
        traceCmd('get_crystal');
        var g = G.getG();
        var targetCrystal = G.CRYSTAL_CONFIG[g.crystals_collected];
        if (!targetCrystal) {
            G.getAnimationQueue().push({ type: 'fail' });
            G.log('[錯誤] 沒有可收集的水晶了！');
            return sk_none();
        }
        if (g.row === targetCrystal.row && g.col === targetCrystal.col) {
            g.crystals_on_map = g.crystals_on_map.filter(function(c) {
                return !(c.row === g.row && c.col === g.col);
            });
            g.crystals_collected++;
            G.getAnimationQueue().push({ type: 'get', row: g.row, col: g.col });
            G.recordEndPosition(g.crystals_collected);

            if (g.crystals_collected === 5) {
                G.getAnimationQueue().push({ type: 'win' });
            } else {
                G.getAnimationQueue().push({ type: 'stage_clear' });
            }
        } else {
            G.getAnimationQueue().push({ type: 'fail' });
            G.log('[錯誤] 這裡沒有水晶！請前往正確的位置。');
        }
        return sk_none();
    });

    Sk.builtins.is_forward_path = new Sk.builtin.func(function() {
        // 感測器也計入步數，避免「純感測器無限迴圈」繞過上限
        if (!guardStep()) return sk_int(0);
        var g = G.getG();
        var nr = g.row, nc = g.col;
        if (g.dir === 0) nr--;
        else if (g.dir === 1) nc++;
        else if (g.dir === 2) nr++;
        else if (g.dir === 3) nc--;
        if (nr < 0 || nr >= 8 || nc < 0 || nc >= 8) return sk_int(0);
        return sk_int(G.MAP_DATA[nr][nc]);
    });

    Sk.builtins.reach_crystal = new Sk.builtin.func(function() {
        // 感測器也計入步數，避免「純感測器無限迴圈」繞過上限
        if (!guardStep()) return sk_bool(false);
        var g = G.getG();
        var targetCrystal = G.CRYSTAL_CONFIG[g.crystals_collected];
        if (!targetCrystal) return sk_bool(false);
        return sk_bool(g.row === targetCrystal.row && g.col === targetCrystal.col);
    });

    Sk.misceval.asyncToPromise(function() {
        return Sk.importMainWithBody('<stdin>', false, runCode, true);
    }).then(function() {
        cancelExecTimeout();
        _lastStepCount = stepCount;
        G.log('Python 執行完畢（共 ' + stepCount + ' 個指令）');
        G.saveProgress();
        G.startAnimation();
    }, function(err) {
        cancelExecTimeout();
        G.log(G.friendlyError(err));
        G.setAnimating(false);
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '▶ 執行程式 <span class="key-hint">(Ctrl+Enter)</span>';
        }
    });
};

// ============================================================
//  Friendly (Chinese) Error Messages
// ============================================================
G.friendlyError = function(err) {
    var raw = '';
    try { raw = err.toString(); } catch (e) { raw = String(err); }
    var hint = null;
    if (/IndentationError|expected an indented block|unindent/i.test(raw)) {
        hint = '縮排錯誤：Python 用「縮排（4 個空格）」來表示程式區塊，for / while / if / def 的下一行記得縮排。';
    } else if (/SyntaxError|invalid syntax/i.test(raw)) {
        hint = '語法錯誤：寫法不符合 Python 規則，請檢查括號、冒號、引號是否成對，關鍵字是否拼對。';
    } else if (/NameError|is not defined/i.test(raw)) {
        hint = '名稱錯誤：用到了沒有定義的名稱。可用指令只有 move_forward()、turn_left()、turn_right()、get_crystal()、is_forward_path()、reach_crystal()，注意大小寫與括號。';
    } else if (/TypeError/i.test(raw)) {
        hint = '型別錯誤：可能把不同種類的資料混在一起用（例如數字加文字），或某個函式用法不對。';
    } else if (/ValueError/i.test(raw)) {
        hint = '數值錯誤：某個值不合法（例如 range() 的參數），請檢查數字。';
    } else if (/ZeroDivisionError|division by zero/i.test(raw)) {
        hint = '除以零錯誤：不可以除以 0，請檢查除數。';
    } else if (/outside loop/i.test(raw)) {
        hint = '迴圈錯誤：break / continue 只能寫在迴圈裡面。';
    } else if (/File not found/i.test(raw)) {
        hint = '系統錯誤：找不到 Python 標準函式庫（skulpt-stdlib.js），請確認 lib/ 資料夾完整。';
    }
    if (hint) {
        return '[錯誤] ' + hint + '\n（原始訊息：' + raw + '）';
    }
    return '[錯誤] ' + raw;
};

// ============================================================
//  Keyboard Shortcuts
// ============================================================
G.initKeyboard = function() {
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey && e.key === 'Enter') || e.key === 'F5') {
            e.preventDefault();
            G.runPython();
        }
    });
};

// ============================================================
//  localStorage Persistence
// ============================================================
var STORAGE_KEY = 'crystal_game_save';

G.saveProgress = function() {
    try {
        var data = {
            userCodes: G.getUserCodes(),
            maxUnlockedStage: G.getMaxUnlockedStage(),
            stageEndPositions: G.getStageEndPositions(),
            currentStageNum: G.getCurrentStage(),
            muted: G.isMuted(),
            speedFactor: G.getSpeedFactor()
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
        // Storage full or unavailable — proceed silently
    }
};

G.loadProgress = function() {
    try {
        var raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return false;
        var data = JSON.parse(raw);
        if (data.userCodes) {
            var uc = G.getUserCodes();
            for (var key in data.userCodes) {
                uc[key] = data.userCodes[key];
            }
        }
        if (data.maxUnlockedStage) G.setMaxUnlockedStage(data.maxUnlockedStage);
        if (data.currentStageNum) G.setCurrentStage(data.currentStageNum);
        if (data.stageEndPositions) {
            var sep = G.getStageEndPositions();
            for (var k in data.stageEndPositions) {
                sep[k] = data.stageEndPositions[k];
            }
        }
        if (data.muted !== undefined) G.setMuted(data.muted);
        if (data.speedFactor !== undefined) G.setSpeedFactor(data.speedFactor);
        return true;
    } catch (e) {
        return false;
    }
};

// ============================================================
//  Animation Speed (1x/2x/4x)
// ============================================================
G.setSpeed = function(n) {
    G.setSpeedFactor(n);
    G.updateSpeedButtons();
    G.saveProgress();
};

G.updateSpeedButtons = function() {
    var s = G.getSpeedFactor();
    [1, 2, 4].forEach(function(n) {
        var b = document.getElementById('btn-speed-' + n);
        if (b) b.classList.toggle('active', s === n);
    });
};

// ============================================================
//  Sound Toggle
// ============================================================
G.toggleSound = function() {
    var muted = G.toggleMute();
    var btn = document.getElementById('btn-toggle-sound');
    if (btn) {
        btn.textContent = muted ? '\uD83D\uDD07 音效' : '\uD83D\uDD0A 音效';
    }
    G.saveProgress();
};

G.updateSoundButton = function() {
    var muted = G.isMuted();
    var btn = document.getElementById('btn-toggle-sound');
    if (btn) {
        btn.textContent = muted ? '\uD83D\uDD07 音效' : '\uD83D\uDD0A 音效';
    }
};

// ============================================================
//  Single Stage Reset
// ============================================================
G.resetCurrentCode = function() {
    if (G.isAnimating()) return;
    var stage = G.getCurrentStage();
    var tmpl = G.LEVELS[stage];
    if (!tmpl) return;
    if (confirm('\u26A0 確定要將 Stage ' + stage + ' 的程式碼恢復為預設範本嗎？')) {
        var userCodes = G.getUserCodes();
        userCodes[stage] = tmpl;
        editor.setValue(tmpl);
        G.log('Stage ' + stage + ' 程式碼已重置');
        G.saveProgress();
    }
};

// ============================================================
//  Newbie Guide
// ============================================================
var GUIDE_KEY = 'crystal_game_guide_done';

G.showGuide = function() {
    var overlay = document.getElementById('guide-overlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
};

G.hideGuide = function() {
    var overlay = document.getElementById('guide-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
    try {
        localStorage.setItem(GUIDE_KEY, '1');
    } catch (e) {}
};

G.checkGuide = function() {
    try {
        var done = localStorage.getItem(GUIDE_KEY);
        if (done === '1') return;
    } catch (e) {}
    // Show guide after assets loaded
    G.delay(500, G.showGuide);
};

// ============================================================
//  Canvas Overlay Buttons (declared in HTML)
// ============================================================

// ============================================================
//  Init
// ============================================================
G.init = function() {
    G.initEditor();

    // Restore progress or start fresh
    var hasSave = G.loadProgress();
    if (hasSave) {
        G.applyStageState(G.getCurrentStage());
        G.syncToDisplay();
        G.updateEditorContent(G.getCurrentStage());
        G.log('已讀取上次的遊戲進度 (Stage ' + G.getCurrentStage() + ')');
    }

    G.loadAssets(function() {
        document.getElementById('loader').style.display = 'none';
        if (!hasSave) {
            G.applyStageState(1);
            G.syncToDisplay();
            G.updateEditorContent(1);
        }
        G.updateStageSelectorUI();
        G.updateSoundButton();
        G.updateSpeedButtons();
        G.drawGame();
        G.initKeyboard();
        G.checkGuide();
        G.log('系統準備就緒，歡迎來到水晶遊戲！');
    });

    // Auto-save on editor changes
    editor.on('change', function() {
        G.saveProgress();
    });
};

})(window.Game);
