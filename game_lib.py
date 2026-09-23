# =====  遊戲核心引擎 (Game Engine) ===== #
#      請勿修改此檔案內容，以免遊戲無法執行        #
# ============================================  #
import os
import pygame
from pygame.locals import *

try:
    pygame.init()
except Exception as e:
    print(f"[錯誤] pygame 初始化失敗：{e}")
    raise SystemExit(1)

try:
    pygame.mixer.init()
    _AUDIO_OK = True
except Exception as e:
    print(f"[警告] 音效初始化失敗，將以靜音模式執行：{e}")
    _AUDIO_OK = False

width, height = 860, 640
white, black, gray = (255, 255, 255), (0, 0, 0), (128, 128, 128)
red, green, blue = (200, 0, 0), (0, 200, 0), (0, 0, 255)
bright_red, bright_green = (255, 0, 0), (0, 255, 0)
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
pygame.display.set_caption('水晶遊戲')
FPS = 10

# 選單按鈕版面（中文標籤較長，主按鈕加寬）
BTN_PRIMARY = {'x': 532, 'y': 460, 'w': 170, 'h': 50}
BTN_QUIT = {'x': 720, 'y': 460, 'w': 100, 'h': 50}
BTN_MUTE = {'x': 422, 'y': 460, 'w': 100, 'h': 50}

# 設定資源路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATERIAL_DIR = os.path.join(BASE_DIR, 'material')

def get_asset_path(filename):
    return os.path.join(MATERIAL_DIR, filename)

def _load_img(filename):
    """載入圖片，缺檔時顯示中文提示並結束（而非丟出難懂的 pygame 錯誤）。"""
    try:
        return pygame.image.load(get_asset_path(filename))
    except Exception as e:
        print(f"[錯誤] 找不到遊戲圖片 material/{filename}，請確認 material 資料夾完整：{e}")
        raise SystemExit(1)

# 載入圖片資源
bg = _load_img('bg_1024x768.png')
bg256 = _load_img('bg_256.png')
road = _load_img('road_64.png')
wall = _load_img('wall_64.png')
c1 = _load_img('crystal_red.png')
c2 = _load_img('crystal_orange.png')
c3 = _load_img('crystal_green.png')
c4 = _load_img('crystal_blue.png')
c5 = _load_img('crystal_black.png')
mc0 = _load_img('mc0.png')
mc1 = _load_img('mc1.png')
mc2 = _load_img('mc2.png')
mc3 = _load_img('mc3.png')
arrow0 = _load_img('arrow0_32.png')
arrow1 = _load_img('arrow1_32.png')
arrow2 = _load_img('arrow2_32.png')
arrow3 = _load_img('arrow3_32.png')
box = _load_img('box_64.png')
func = _load_img('funs.png')
m1 = _load_img('m1.png')
m2 = _load_img('m2.png')
m3 = _load_img('m3.png')
m4 = _load_img('m4.png')
m5 = _load_img('m5.png')
victory = _load_img('victory.png')
defeat = _load_img('defeat.png')

# 水晶座標 -> 對應圖片（查表取代 index+crystals 的偏移寫法）
CRYSTAL_IMG = {(3, 3): c1, (3, 6): c2, (6, 3): c3, (4, 1): c4, (1, 6): c5}

def _load_sfx(filename):
    if not _AUDIO_OK:
        return None
    try:
        return pygame.mixer.Sound(get_asset_path(filename))
    except Exception as e:
        print(f"[警告] 音效 material/{filename} 載入失敗，將跳過此音效：{e}")
        return None

# 預先載入音效（Sound 物件可重疊播放、不阻塞畫面）
SFX = {
    'get': _load_sfx('get.mp3'),
    'knock': _load_sfx('knock_on_wall.mp3'),
    'fail': _load_sfx('fail.mp3'),
    'victory': _load_sfx('victory.mp3'),
}

set_map = [[0,0,0,0,0,0,0,0],
           [0,1,1,1,1,1,1,0],
           [0,1,0,0,0,0,0,0],
           [0,1,0,1,1,1,1,0],
           [0,1,0,1,0,0,1,0],
           [0,1,0,0,0,0,1,0],
           [0,1,1,1,1,1,1,0],
           [0,0,0,0,0,0,0,0]]
set_crystal = [[3, 3], [3, 6], [6, 3], [4, 1], [1, 6]]
bak_crystal = set_crystal.copy()
curr_row, curr_col, direction, crystals = 4, 3, 0, 0

# === 無限迴圈防護 ===
MAX_INSTRUCTIONS = 500
_instr_count = 0
_muted = False
# success() 選單的選擇（供 _play_stage 讀取，因為學生函式內無法回傳值）
_pending_action = None

class InstructionLimitError(Exception):
    pass

class StageAborted(Exception):
    """學生程式被中斷（撞牆/失敗選單選擇了 Restart 或 Quit），用來 unwind 學生函式。"""
    pass

def _check_instr():
    global _instr_count
    _instr_count += 1
    if _instr_count > MAX_INSTRUCTIONS:
        _instr_count = 0
        raise InstructionLimitError()

# 儲存學生定義的關卡函式
stages = {}

def set_stages(s1, s2, s3, s4, s5):
    global stages
    stages[1] = s1
    stages[2] = s2
    stages[3] = s3
    stages[4] = s4
    stages[5] = s5

def safe_stage_call(n):
    """執行學生關卡函式。回傳 (ok, count_or_errmsg)；StageAborted 會直接向上传遞。"""
    global _instr_count
    _instr_count = 0
    try:
        stages[n]()
        return True, _instr_count
    except InstructionLimitError:
        return False, '指令數量過多！請檢查迴圈條件'
    except StageAborted:
        raise
    except Exception as e:
        return False, f'程式發生錯誤：{type(e).__name__}: {e}'

def start_game():
    """遊戲總入口：單一主迴圈驅動選單與關卡，所有結束路徑只在這裡關閉 pygame。"""
    try:
        action = initial_game()
        while True:
            if action == 'quit':
                break
            if action == 'restart':
                action = initial_game()
                continue
            if action == 'stage':
                n = crystals + 1
                if n > 5:
                    action = initial_game()
                    continue
                result = _play_stage(n)
                if result == 'quit':
                    break
                elif result == 'restart':
                    action = initial_game()
                elif result == 'stage':
                    action = 'stage'  # crystals 已+1，繼續下一關
                else:
                    # 學生函式跑完但沒有結果（例如只寫 pass）：回到選單
                    action = initial_game()
    finally:
        pygame.quit()

def text_box(text, font):
    text = font.render(text, True, black)
    return text, text.get_rect()

def check_mute_key():
    """只回報按鍵事件，不關閉 pygame（關閉由 _menu_loop / start_game 統一處理）。"""
    global _muted
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            return 'quit'
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            _toggle_mute()
            return 'mute'
    return None

def _toggle_mute():
    global _muted
    _muted = not _muted
    for snd in SFX.values():
        if snd is not None:
            try:
                snd.set_volume(0.0 if _muted else 1.0)
            except Exception:
                pass

def play_sfx(path):
    """播放音效（非阻塞）。靜音或載入失敗時自動跳過。"""
    if _muted:
        return
    key = {'get.mp3': 'get', 'knock_on_wall.mp3': 'knock',
           'fail.mp3': 'fail', 'victory.mp3': 'victory'}.get(os.path.basename(path))
    snd = SFX.get(key)
    if snd is not None:
        try:
            snd.play()
        except Exception:
            pass

def button(msg, x, y, w, h, ic, ac):
    """繪製按鈕。被點擊的當下回傳 True，否則 False（點擊結果由 _menu_loop 處理）。"""
    pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    hovered = x + w > pos[0] > x and y + h > pos[1] > y
    pygame.draw.rect(screen, ic if hovered else ac, (x, y, w, h))
    smallText = pygame.font.SysFont('arial', 20)
    textSurf, textRect = text_box(msg, smallText)
    textRect.center = (x + w / 2, y + h / 2)
    screen.blit(textSurf, textRect)
    return hovered and click[0] == 1

def _wait_mouse_release():
    """避免按住滑鼠連續觸發多個按鈕。"""
    while pygame.mouse.get_pressed()[0]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass
        clock.tick(FPS)

def _mkbtn(text, geom, ic, ac, ret):
    return {'text': text, 'x': geom['x'], 'y': geom['y'], 'w': geom['w'],
            'h': geom['h'], 'ic': ic, 'ac': ac, 'ret': ret}

def _mute_button():
    mute_text = "音效：開" if not _muted else "音效：關"
    return _mkbtn(mute_text, BTN_MUTE, gray, gray, '__mute__')

def _paint_mute_hint():
    smallText = pygame.font.SysFont('arial', 14)
    hint, _ = text_box("[M] 靜音  [ESC] 離開", smallText)
    screen.blit(hint, (440, 430))

def _menu_loop(paint, buttons):
    """通用選單迴圈：每幀重繪 paint()，回傳被點按鈕的 ret，或 'quit'。
    '__mute__' 為保留動作：切換靜音後繼續選單。"""
    while True:
        action = check_mute_key()
        if action == 'quit':
            return 'quit'
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
        paint()
        for b in buttons:
            if button(b['text'], b['x'], b['y'], b['w'], b['h'], b['ic'], b['ac']):
                _wait_mouse_release()
                if b['ret'] == '__mute__':
                    _toggle_mute()
                    break
                return b['ret']
        pygame.display.update()
        clock.tick(FPS)

def _blit_mc():
    """繪製角色與方向箭頭（不翻頁，供 paint 函式重複呼叫）。"""
    if direction == 0:
        screen.blit(mc0, (curr_col*64, curr_row*64))
        screen.blit(arrow0, (curr_col*64+16, (curr_row-1)*64+48))
    elif direction == 1:
        screen.blit(mc1, (curr_col*64, curr_row*64))
        screen.blit(arrow1, ((curr_col+1)*64-16, curr_row*64+16))
    elif direction == 2:
        screen.blit(mc2, (curr_col*64, curr_row*64))
        screen.blit(arrow2, (curr_col*64+16, (curr_row+1)*64-16))
    elif direction == 3:
        screen.blit(mc3, (curr_col*64, curr_row*64))
        screen.blit(arrow3, ((curr_col-1)*64+48, curr_row*64+16))

def show_mc(d):
    _blit_mc()
    pygame.display.update()
    clock.tick(FPS)

def chk_crystal(r, c):
    """若 (r, c) 仍有水晶，依座標查表畫出正確顏色的水晶。"""
    if [r, c] in set_crystal:
        img = CRYSTAL_IMG.get((r, c))
        if img is not None:
            screen.blit(img, (c*64, r*64))

def chk_legal(r, c):
    if set_map[r][c] == 0:
        return False
    else:
        return True

def re_draw():
    global direction, curr_row, curr_col
    screen.blit(road, (curr_col*64, curr_row*64))
    if direction == 0:  n_row, n_col = curr_row-1, curr_col
    elif direction == 1: n_row, n_col = curr_row, curr_col+1
    elif direction == 2: n_row, n_col = curr_row+1, curr_col
    elif direction == 3: n_row, n_col = curr_row, curr_col-1
    if set_map[n_row][n_col] == 0:
        screen.blit(wall, (n_col*64, n_row*64))
    elif set_map[n_row][n_col] == 1:
        screen.blit(road, (n_col*64, n_row*64))
    chk_crystal(curr_row, curr_col)
    chk_crystal(n_row, n_col)
    pygame.display.update()
    clock.tick(FPS)

def _paint_board():
    """繪製棋盤、地圖上的水晶與角色（不翻頁）。"""
    screen.blit(bg, (0, 0))
    for i in range(8):
        for j in range(8):
            if set_map[i][j] == 0:
                screen.blit(wall, (j*64, i*64))
            elif set_map[i][j] == 1:
                screen.blit(road, (j*64, i*64))
    for (r, c) in set_crystal:
        img = CRYSTAL_IMG.get((r, c))
        if img is not None:
            screen.blit(img, (c*64, r*64))
    _blit_mc()

def _paint_stage_labels():
    """底部進度列：Mission 與各關水晶標籤。"""
    largeText = pygame.font.SysFont('comicsansms', 20)
    TextSurf, TextRect = text_box('任務：收集水晶', largeText)
    TextRect.center = (120, 532)
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_box('第一關', largeText)
    TextRect.center = (60, 590)
    screen.blit(TextSurf, TextRect)
    screen.blit(c1, (100, 548))
    TextSurf, TextRect = text_box('-> 第二關', largeText)
    TextRect.center = (210, 590)
    screen.blit(TextSurf, TextRect)
    screen.blit(c2, (260, 558))
    TextSurf, TextRect = text_box('-> 第三關', largeText)
    TextRect.center = (375, 590)
    screen.blit(TextSurf, TextRect)
    screen.blit(c3, (425, 558))
    TextSurf, TextRect = text_box('-> 第四關', largeText)
    TextRect.center = (540, 590)
    screen.blit(TextSurf, TextRect)
    screen.blit(c4, (590, 548))
    TextSurf, TextRect = text_box('-> 第五關', largeText)
    TextRect.center = (710, 590)
    screen.blit(TextSurf, TextRect)
    screen.blit(c5, (760, 558))

def turn_left():
    global direction
    _check_instr()
    re_draw()
    direction = (direction-1) % 4
    show_mc(direction)

def turn_right():
    global direction
    _check_instr()
    re_draw()
    direction = (direction+1) % 4
    show_mc(direction)

def draw_right():
    for i in range(2):
        screen.blit(bg256, (512, i*256))
    right_text = str(crystals) + ' / 5 '
    largeText = pygame.font.SysFont('comicsansms', 20)
    TextSurf, TextRect = text_box(right_text, largeText)
    TextRect.center = (570, 20)
    screen.blit(TextSurf, TextRect)
    for i in range(5):
        screen.blit(box, (526+i*64, 40))
    screen.blit(func, (526, 120))
    if crystals == 0:
        screen.blit(m1, (480, 310))
    if crystals >= 1:
        screen.blit(m2, (480, 310))
        screen.blit(pygame.transform.scale(c1, (40, 40)), (538, 50))
    if crystals >= 2:
        screen.blit(m3, (480, 310))
        screen.blit(pygame.transform.scale(c2, (40, 40)), (602, 50))
    if crystals >= 3:
        screen.blit(m4, (480, 310))
        screen.blit(pygame.transform.scale(c3, (40, 40)), (666, 50))
    if crystals >= 4:
        screen.blit(m5, (480, 310))
        screen.blit(pygame.transform.scale(c4, (40, 40)), (730, 50))
    if crystals == 5:
        screen.blit(pygame.transform.scale(c5, (40, 40)), (794, 50))

def _blit_instr_count(count):
    largeText = pygame.font.SysFont('comicsansms', 18)
    TextSurf, TextRect = text_box('指令數：%d 個' % count, largeText)
    TextRect.center = (430, 340)
    screen.blit(TextSurf, TextRect)

def crash(idx):
    """撞牆 / 撿錯水晶。顯示失敗畫面與選單後，以 StageAborted 中斷學生函式。"""
    if idx == 1:
        play_sfx(get_asset_path('knock_on_wall.mp3'))
    elif idx == 2:
        play_sfx(get_asset_path('fail.mp3'))

    def paint():
        _paint_board()
        draw_right()
        screen.blit(defeat, (50, 50))
        _paint_mute_hint()

    buttons = [
        _mkbtn('重新開始', BTN_PRIMARY, green, bright_green, 'restart'),
        _mkbtn('離開遊戲', BTN_QUIT, red, bright_red, 'quit'),
        _mute_button(),
    ]
    choice = _menu_loop(paint, buttons)
    raise StageAborted(choice)

def move_forward():
    global direction, curr_row, curr_col
    _check_instr()
    re_draw()
    if direction == 0:  n_row, n_col = curr_row-1, curr_col
    elif direction == 1: n_row, n_col = curr_row, curr_col+1
    elif direction == 2: n_row, n_col = curr_row+1, curr_col
    elif direction == 3: n_row, n_col = curr_row, curr_col-1
    if chk_legal(n_row, n_col) == True:
        curr_row, curr_col = n_row, n_col
        show_mc(direction)
    else:
        crash(1)

def reach_crystal():
    global direction, curr_row, curr_col
    _check_instr()
    if [curr_row, curr_col] in set_crystal:
        return True
    else:
        return False

def is_forward_path():
    global direction, curr_row, curr_col
    _check_instr()
    if direction == 0:  n_row, n_col = curr_row-1, curr_col
    elif direction == 1: n_row, n_col = curr_row, curr_col+1
    elif direction == 2: n_row, n_col = curr_row+1, curr_col
    elif direction == 3: n_row, n_col = curr_row, curr_col-1
    return set_map[n_row][n_col]

def success():
    global crystals, curr_row, curr_col, direction, _instr_count, _pending_action
    count = _instr_count
    set_crystal.remove([curr_row, curr_col])
    re_draw()
    show_mc(direction)
    crystals += 1
    draw_right()
    if crystals == 5:
        screen.blit(victory, (50, 100))
        pygame.display.update()
        play_sfx(get_asset_path('victory.mp3'))
    else:
        play_sfx(get_asset_path('get.mp3'))

    if crystals == 5:
        next_text, next_ret = '重新開始', 'restart'
    else:
        next_text, next_ret = '下一關', 'stage'

    def paint():
        _paint_board()
        draw_right()
        if crystals == 5:
            screen.blit(victory, (50, 100))
        _blit_instr_count(count)
        _paint_mute_hint()

    buttons = [
        _mkbtn(next_text, BTN_PRIMARY, green, bright_green, next_ret),
        _mkbtn('離開遊戲', BTN_QUIT, red, bright_red, 'quit'),
        _mute_button(),
    ]
    _pending_action = _menu_loop(paint, buttons)

def _play_stage(n):
    """執行第 n 關學生函式，回傳後續動作：'stage' / 'restart' / 'quit' / None。"""
    global _pending_action
    _pending_action = None
    try:
        ok, info = safe_stage_call(n)
    except StageAborted as e:
        return e.args[0] if e.args else 'quit'
    if not ok:
        return _show_error_screen(info)
    return _pending_action

def _show_error_screen(message):
    """指令超量或程式錯誤時的錯誤畫面，回傳選單選擇。"""
    def paint():
        _paint_board()
        draw_right()
        screen.blit(defeat, (50, 50))
        largeText = pygame.font.SysFont('comicsansms', 22)
        warning, _ = text_box(message, largeText)
        warning_rect = warning.get_rect(center=(430, 250))
        screen.blit(warning, warning_rect)
        _paint_mute_hint()

    buttons = [
        _mkbtn('重新開始', BTN_PRIMARY, green, bright_green, 'restart'),
        _mkbtn('離開遊戲', BTN_QUIT, red, bright_red, 'quit'),
        _mute_button(),
    ]
    return _menu_loop(paint, buttons)

def get_crystal():
    global crystals, curr_row, curr_col
    _check_instr()
    if [curr_row, curr_col] == set_crystal[0]:
        success()
    else:
        crash(2)

def initial_game():
    """重設棋盤並顯示主選單。回傳 'stage'（開始第一關）或 'quit'。"""
    global curr_row, curr_col, direction, crystals, set_crystal, bak_crystal, _muted
    curr_row, curr_col, direction, crystals = 4, 3, 0, 0
    set_crystal = bak_crystal.copy()

    def paint():
        _paint_board()
        _paint_stage_labels()
        draw_right()
        _paint_mute_hint()

    buttons = [
        _mkbtn('開始遊戲（第一關）', BTN_PRIMARY, green, bright_green, 'stage'),
        _mkbtn('離開遊戲', BTN_QUIT, red, bright_red, 'quit'),
        _mute_button(),
    ]
    return _menu_loop(paint, buttons)
