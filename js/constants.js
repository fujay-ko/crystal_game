window.Game = window.Game || {};

(function(G) {

G.CONST = {
    TILE_SIZE: 64,
    ASSETS_PATH: './material/',
    MAX_STEPS: 200,
    EXEC_TIMEOUT_MS: 20000,
    CANVAS_WIDTH: 860,
    CANVAS_HEIGHT: 640,
    STAGE_COUNT: 5
};

G.CRYSTAL_CONFIG = [
    { stage: 1, row: 3, col: 3, colorKey: 'c1' },
    { stage: 2, row: 3, col: 6, colorKey: 'c2' },
    { stage: 3, row: 6, col: 3, colorKey: 'c3' },
    { stage: 4, row: 4, col: 1, colorKey: 'c4' },
    { stage: 5, row: 1, col: 6, colorKey: 'c5' }
];

G.MAP_DATA = [
    [0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,0],
    [0,1,0,0,0,0,0,0],
    [0,1,0,1,1,1,1,0],
    [0,1,0,1,0,0,1,0],
    [0,1,0,0,0,0,1,0],
    [0,1,1,1,1,1,1,0],
    [0,0,0,0,0,0,0,0]
];

G.IMAGE_FILES = {
    'bg': 'bg_1024x768.png', 'bg256': 'bg_256.png',
    'road': 'road_64.png', 'wall': 'wall_64.png',
    'c1': 'crystal_red.png', 'c2': 'crystal_orange.png',
    'c3': 'crystal_green.png', 'c4': 'crystal_blue.png', 'c5': 'crystal_black.png',
    'mc0': 'mc0.png', 'mc1': 'mc1.png', 'mc2': 'mc2.png', 'mc3': 'mc3.png',
    'arrow0': 'arrow0_32.png', 'arrow1': 'arrow1_32.png',
    'arrow2': 'arrow2_32.png', 'arrow3': 'arrow3_32.png',
    'box': 'box_64.png', 'func': 'funs.png',
    'm1': 'm1.png', 'm2': 'm2.png', 'm3': 'm3.png', 'm4': 'm4.png', 'm5': 'm5.png',
    'victory': 'victory.png', 'defeat': 'defeat.png'
};

G.AUDIO_FILES = {
    'victory': 'victory.mp3',
    'get': 'get.mp3',
    'fail': 'fail.mp3',
    'knock': 'knock_on_wall.mp3'
};

G.LAYOUT = {
    BACKPACK_TEXT: { x: 570, y: 30 },
    BACKPACK_START: { x: 526, y: 40 },
    BACKPACK_SLOT_SIZE: 64,
    BACKPACK_ICON_OFFSET: 12,
    BACKPACK_ICON_SIZE: 40,
    FUNC_PANEL: { x: 526, y: 120 },
    SCROLL: { x: 480, y: 310 },
    PROGRESS_TITLE: { x: 120, y: 532 },
    STAGE_LABELS: [
        { text: "Stage1",      x: 60,  y: 590, icon: 'c1', iconX: 100,  iconY: 548, iconSize: null },
        { text: "-> Stage2",   x: 210, y: 590, icon: 'c2', iconX: 260,  iconY: 558, iconSize: null },
        { text: "-> Stage3",   x: 375, y: 590, icon: 'c3', iconX: 425,  iconY: 558, iconSize: null },
        { text: "-> Stage4",   x: 540, y: 590, icon: 'c4', iconX: 590,  iconY: 548, iconSize: null },
        { text: "-> Stage5",   x: 710, y: 590, icon: 'c5', iconX: 760,  iconY: 558, iconSize: null }
    ],
    VICTORY_IMG: { x: 50, y: 100 },
    DEFEAT_IMG: { x: 50, y: 50 }
};

G.LEVELS = {
    1: "def stage1():\n    # Stage 1: 基礎移動\n    # 任務：幫主角走到紅色水晶的位置，然後撿起來！\n    #\n    # 提示：\n    # 使用 move_forward() 向前走\n    # 到了之後用 get_crystal() 撿起來\n    ",
    2: "def stage2():\n    # Stage 2: 轉彎與迴圈\n    # 任務：走到橙色水晶並撿起來。\n    #\n    # 提示：\n    # [基礎] 一步一步寫指令走到終點。\n    # [進階] 發現有重複的動作嗎？試試看用「for 迴圈」讓電腦幫你重複執行！\n    ",
    3: "def stage3():\n    # Stage 3: 規律的路徑\n    # 任務：取得綠色水晶。\n    #\n    # 提示：\n    # [基礎] 數數看有幾格，用 for 迴圈走過去。\n    # [進階] 觀察路徑，是不是有「走一段路 + 轉彎」的形狀重複出現呢？\n    #       試試看用「雙層迴圈」(迴圈裡面包著迴圈) 來解決！\n    ",
    4: "def stage4():\n    # Stage 4: 聰明的探險家\n    # 任務：取得藍色水晶。\n    #\n    # 提示：\n    # [基礎] 路線不是直線，走到一半需要右轉。\n    #       你可以試著把路分成「轉彎前」和「轉彎後」兩段來寫。\n    # [進階] 試試 while 迴圈，搭配 is_forward_path() 判斷前方，\n    #       再用 not reach_crystal() 當作繼續走的條件，\n    #       讓主角自己走到水晶。\n    ",
    5: "def stage5():\n    # Stage 5: 最終考驗\n    # 任務：取得最後的黑色水晶！\n    #\n    # 提示：\n    # [基礎] 把你在第四關寫好的程式碼直接拿來用，\n    #       不用改任何邏輯，就能走到黑色水晶。\n    # [進階] 試試 while True 的做法：\n    #       用 if 判斷條件是否成立，\n    #       成立時做該做的事，然後記得用 break 中斷迴圈。\n    "
};

})(window.Game);
