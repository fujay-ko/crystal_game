# =====  遊戲核心引擎 (Game Engine) ===== #
#      請勿修改此檔案內容，以免遊戲無法執行        #
# ============================================  #
import pygame, time, os
from pygame.locals import *

pygame.init()
pygame.mixer.init()

width, height = 860, 640
white, black, gray = (255, 255, 255), (0, 0, 0), (128, 128, 128)
red, green, blue = (200, 0, 0), (0, 200, 0), (0, 0, 255)
bright_red, bright_green = (255, 0, 0), (0, 255, 0)
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
pygame.display.set_caption('水晶遊戲')
FPS = 10

# 設定資源路徑 (解決找不到檔案的問題)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATERIAL_DIR = os.path.join(BASE_DIR, 'material')

def get_asset_path(filename):
    return os.path.join(MATERIAL_DIR, filename)

# 載入圖片資源
bg = pygame.image.load(get_asset_path('bg_1024x768.png'))
bg256 = pygame.image.load(get_asset_path('bg_256.png'))
road = pygame.image.load(get_asset_path('road_64.png'))
wall = pygame.image.load(get_asset_path('wall_64.png'))
c1 = pygame.image.load(get_asset_path('crystal_red.png'))
c2 = pygame.image.load(get_asset_path('crystal_orange.png'))
c3 = pygame.image.load(get_asset_path('crystal_green.png'))
c4 = pygame.image.load(get_asset_path('crystal_blue.png'))
c5 = pygame.image.load(get_asset_path('crystal_black.png'))
mc0 = pygame.image.load(get_asset_path('mc0.png'))
mc1 = pygame.image.load(get_asset_path('mc1.png'))
mc2 = pygame.image.load(get_asset_path('mc2.png'))
mc3 = pygame.image.load(get_asset_path('mc3.png'))
arrow0 = pygame.image.load(get_asset_path('arrow0_32.png'))
arrow1 = pygame.image.load(get_asset_path('arrow1_32.png'))
arrow2 = pygame.image.load(get_asset_path('arrow2_32.png'))
arrow3 = pygame.image.load(get_asset_path('arrow3_32.png'))
box = pygame.image.load(get_asset_path('box_64.png'))
func = pygame.image.load(get_asset_path('funs.png'))
m1 = pygame.image.load(get_asset_path('m1.png'))
m2 = pygame.image.load(get_asset_path('m2.png'))
m3 = pygame.image.load(get_asset_path('m3.png'))
m4 = pygame.image.load(get_asset_path('m4.png'))
m5 = pygame.image.load(get_asset_path('m5.png'))
victory = pygame.image.load(get_asset_path('victory.png'))
defeat = pygame.image.load(get_asset_path('defeat.png'))

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

# 儲存學生定義的關卡函式
stages = {}

def set_stages(s1, s2, s3, s4, s5):
    global stages
    stages[1] = s1
    stages[2] = s2
    stages[3] = s3
    stages[4] = s4
    stages[5] = s5

def start_game():
    initial_game()
    pygame.quit()

def text_box(text, font):
    text = font.render(text, True, black)
    return text, text.get_rect()

def button(msg, x, y, w, h, ic, ac, action=None):
    pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    pygame.draw.rect(screen, ac, (x, y, w, h))
    smallText = pygame.font.SysFont('arial', 20)
    textSurf, textRect = text_box(msg, smallText)
    textRect.center = (x+w/2, y+h/2)
    screen.blit(textSurf, textRect)    
    if x+w > pos[0] > x and y+h > pos[1] > y:
        if click[0] == 1 and action != None:
            action()
        else:
            pygame.draw.rect(screen, ic, (x, y, w, h))
            textSurf, textRect = text_box(msg, smallText)
            textRect.center = (x+w/2, y+h/2)
            screen.blit(textSurf, textRect)

def show_mc(d):
    global direction, curr_row, curr_col, pygame, clock
    if d==0:
        screen.blit(mc0, (curr_col*64, curr_row*64))
        screen.blit(arrow0, (curr_col*64+16, (curr_row-1)*64+48))
    elif d==1:
        screen.blit(mc1, (curr_col*64, curr_row*64))
        screen.blit(arrow1, ((curr_col+1)*64-16, curr_row*64+16))
    elif d==2:
        screen.blit(mc2, (curr_col*64, curr_row*64))
        screen.blit(arrow2, (curr_col*64+16, (curr_row+1)*64-16))
    elif d==3:
        screen.blit(mc3, (curr_col*64, curr_row*64))
        screen.blit(arrow3, ((curr_col-1)*64+48, curr_row*64+16))
    pygame.display.update()
    clock.tick(FPS)

def chk_crystal(r, c):
    global crystals
    x = -1
    if [r, c] in set_crystal: x = set_crystal.index([r, c])+crystals
    if x==0: screen.blit(c1, (c*64, r*64))
    elif x==1: screen.blit(c2, (c*64, r*64))
    elif x==2: screen.blit(c3, (c*64, r*64))
    elif x==3: screen.blit(c4, (c*64, r*64))
    elif x==4: screen.blit(c5, (c*64, r*64))

def chk_legal(r, c):
    if set_map[r][c]==0: return False
    else: return True        

def re_draw():
    global direction, curr_row, curr_col
    screen.blit(road, (curr_col*64, curr_row*64))
    if direction==0:  n_row, n_col = curr_row-1, curr_col
    elif direction==1: n_row, n_col = curr_row, curr_col+1
    elif direction==2: n_row, n_col = curr_row+1, curr_col
    elif direction==3: n_row, n_col = curr_row, curr_col-1
    if set_map[n_row][n_col]==0: screen.blit(wall, (n_col*64, n_row*64))
    elif set_map[n_row][n_col]==1: screen.blit(road, (n_col*64, n_row*64))
    chk_crystal(curr_row, curr_col)
    chk_crystal(n_row, n_col)
    pygame.display.update()
    clock.tick(FPS)

def turn_left():
    global direction
    re_draw()
    direction = (direction-1)%4
    show_mc(direction)

def turn_right():
    global direction
    re_draw()
    direction = (direction+1)%4
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
    

def crash(idx):
    if idx==1: pygame.mixer.music.load(get_asset_path('knock_on_wall.mp3'))  
    elif idx==2: pygame.mixer.music.load(get_asset_path('fail.mp3'))
    pygame.mixer.music.play()
    time.sleep(0.5)
    pygame.mixer.music.stop()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()
        screen.blit(defeat, (50, 50))        
        button("Restart", 552, 460, 100, 50, green, bright_green, initial_game)
        button("Quit", 720, 460, 100, 50, red, bright_red, quit_game)
        pygame.display.update()
        clock.tick(FPS)

def move_forward():
    global direction, curr_row, curr_col
    re_draw()
    if direction==0:  n_row, n_col = curr_row-1, curr_col
    elif direction==1: n_row, n_col = curr_row, curr_col+1
    elif direction==2: n_row, n_col = curr_row+1, curr_col
    elif direction==3: n_row, n_col = curr_row, curr_col-1
    if chk_legal(n_row, n_col)==True:  curr_row, curr_col = n_row, n_col; show_mc(direction) 
    else: crash(1)  

def reach_crystal():
    global direction, curr_row, curr_col
    if [curr_row, curr_col] in set_crystal: return True
    else: return False

def is_forward_path():
    global direction, curr_row, curr_col
    if direction==0:  n_row, n_col = curr_row-1, curr_col
    elif direction==1: n_row, n_col = curr_row, curr_col+1
    elif direction==2: n_row, n_col = curr_row+1, curr_col
    elif direction==3: n_row, n_col = curr_row, curr_col-1
    return set_map[n_row][n_col]

def success():
    global crystals, curr_row, curr_col, direction
    set_crystal.remove([curr_row, curr_col])
    re_draw()
    show_mc(direction)
    crystals += 1
    draw_right()
    if crystals == 5:
        screen.blit(victory, (50, 100))
        pygame.display.update()
        pygame.mixer.music.load(get_asset_path('victory.mp3'))
        pygame.mixer.music.play()
        time.sleep(1)
        pygame.mixer.music.stop()
    else:
        pygame.mixer.music.load(get_asset_path('get.mp3'))
        pygame.mixer.music.play()
        time.sleep(0.5)
        pygame.mixer.music.stop()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()

        btn_txt = 'Stage' + str(crystals+1)
        if crystals == 1: button(btn_txt, 552, 460, 100, 50, green, bright_green, stages.get(2))
        elif crystals == 2: button(btn_txt, 552, 460, 100, 50, green, bright_green, stages.get(3))
        elif crystals == 3: button(btn_txt, 552, 460, 100, 50, green, bright_green, stages.get(4))
        elif crystals == 4: button(btn_txt, 552, 460, 100, 50, green, bright_green, stages.get(5))
        elif crystals == 5:
            button('Restart' , 552, 460, 100, 50, green, bright_green, initial_game)
            screen.blit(victory, (50, 100))
        button("Quit", 720, 460, 100, 50, red, bright_red, quit_game)
        pygame.display.update()
        clock.tick(FPS)

def get_crystal():
    global crystals, curr_row, curr_col
    if [curr_row, curr_col] == set_crystal[0]: success()
    else: crash(2)

def quit_game():
    pygame.quit()

def initial_game():
    global curr_row, curr_col, direction, crystals, set_crystal, bak_crystal
    screen.blit(bg, (0, 0))
    for i in range(8):
        for j in range(8):
            if set_map[i][j]==0: screen.blit(wall, (j*64, i*64))
            elif set_map[i][j]==1: screen.blit(road, (j*64, i*64))
    curr_row, curr_col, direction, crystals = 4, 3, 0, 0
    set_crystal = bak_crystal.copy()
    screen.blit(c1, (set_crystal[0][1]*64, set_crystal[0][0]*64))
    screen.blit(c2, (set_crystal[1][1]*64, set_crystal[1][0]*64))
    screen.blit(c3, (set_crystal[2][1]*64, set_crystal[2][0]*64))
    screen.blit(c4, (set_crystal[3][1]*64, set_crystal[3][0]*64))
    screen.blit(c5, (set_crystal[4][1]*64, set_crystal[4][0]*64))
    screen.blit(mc0, (curr_col*64, curr_row*64))
    screen.blit(arrow0, (curr_col*64+16, (curr_row-1)*64+48))
    largeText = pygame.font.SysFont('comicsansms', 20)
    TextSurf, TextRect = text_box('Mission: Get Crystals', largeText)
    TextRect.center = (120, 532)
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_box('Stage1', largeText)
    TextRect.center = (60, 590)
    screen.blit(TextSurf, TextRect)
    screen.blit(c1, (100, 548))
    TextSurf, TextRect = text_box('-> Stage2', largeText)
    TextRect.center = (210, 590)
    screen.blit(TextSurf, TextRect)
    screen.blit(c2, (260, 558))
    TextSurf, TextRect = text_box('-> Stage3', largeText)
    TextRect.center = (375, 590)
    screen.blit(TextSurf, TextRect)
    screen.blit(c3, (425, 558))
    TextSurf, TextRect = text_box('-> Stage4', largeText)
    TextRect.center = (540, 590)
    screen.blit(TextSurf, TextRect)
    screen.blit(c4, (590, 548))
    TextSurf, TextRect = text_box('-> Stage5', largeText)
    TextRect.center = (710, 590)
    screen.blit(TextSurf, TextRect)
    screen.blit(c5, (760, 558))

    right_text = str(crystals) + ' / 5 '
    TextSurf, TextRect = text_box(right_text, largeText)
    TextRect.center = (570, 20)
    screen.blit(TextSurf, TextRect)
    for i in range(5):
        screen.blit(box, (526+i*64, 40))
    screen.blit(func, (526, 120))
    screen.blit(m1, (480, 310))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                pygame.quit()
                
        button("Stage1", 552, 460, 100, 50, green, bright_green, stages.get(1))
        button("Quit", 720, 460, 100, 50, red, bright_red, quit_game)
       
        pygame.display.update()
        clock.tick(FPS)