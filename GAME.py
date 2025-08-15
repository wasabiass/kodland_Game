import pgzrun
import math
from pygame import Rect

# Configurações principais do jogo
WIDTH, HEIGHT, TILE_SIZE = 800, 600, 40
game_state = "menu"
menu_instance = None

# Carregamento dos efeitos sonoros
button_sound = sounds.load("button")
step_sound = sounds.load("step")
victory_sound = sounds.load("victory")

# Mapa do jogo (matriz de tiles)
map_matrix = [
    # 0 = parede, 1 = chão, 4 = objetivo/porta
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
    [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 4, 1, 0],
    [0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0],
    [0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

PLAYER_SIZE = 42  # Tamanho do player e inimigos

# Configuração dos frames do inimigo
ENEMY_SPRITESHEET_NAME = "d_walk"
ENEMY_FRAME_WIDTH = 32
ENEMY_FRAME_HEIGHT = 32
ENEMY_FRAME_COUNT = 5
enemy_frames = [
    Rect(i * ENEMY_FRAME_WIDTH, 0, ENEMY_FRAME_WIDTH, ENEMY_FRAME_HEIGHT)
    for i in range(ENEMY_FRAME_COUNT)
]

# Menu principal com botões
class Menu:
    def __init__(self):
        self.buttons = [
            {"rect": Rect(300, 200, 200, 50), "text": "Start Game", "action": "start_game"},
            {"rect": Rect(300, 300, 200, 50), "text": "Music: ON", "action": "toggle_music"},
            {"rect": Rect(300, 400, 200, 50), "text": "Quit", "action": "quit"}
        ]
        self.music_enabled = True

    def draw(self):
        screen.fill((20, 30, 40))
        screen.draw.text("Main Menu", center=(WIDTH // 2, 100), fontsize=50, color="white")
        for button in self.buttons:
            if button["action"] == "toggle_music":
                button["text"] = "Music: ON" if self.music_enabled else "Music: OFF"
            screen.draw.filled_rect(button["rect"], "grey")
            screen.draw.text(button["text"], center=button["rect"].center, fontsize=30, color="white")

    # Lógica dos botões do menu
    def handle_click(self, pos):
        global game_state
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                button_sound.play()
                if button["action"] == "start_game":
                    game_state = "game"
                    # Música só toca se estiver ativada
                    if self.music_enabled:
                        music.play('background_music')
                    else:
                        music.stop()
                elif button["action"] == "toggle_music":
                    self.music_enabled = not self.music_enabled
                    if self.music_enabled:
                        music.play('background_music')
                    else:
                        music.stop()
                elif button["action"] == "quit":
                    exit()

    # Toca música no menu se ativada
    def play_menu_music(self):
        if self.music_enabled:
            music.play('background_music')
            music.set_volume(0.5)
    
    def stop_music(self):
        music.stop()

# Função para desenhar o mapa e a porta
def draw_map():
    screen.clear()
    for y, row in enumerate(map_matrix):
        for x, tile in enumerate(row):
            pos = (x * TILE_SIZE, y * TILE_SIZE)
            if tile == 1:
                screen.blit("fieldstile_01", pos)
            elif tile == 0:
                screen.blit("tile_0014", pos)
            elif tile == 4:
                screen.blit("fieldstile_01", pos)
                screen.blit("door", pos)  # Sprite da porta

# Classe do jogador
class Player:
    def __init__(self):
        self.x, self.y = 1, 1
        self.pixel_x = self.x * TILE_SIZE
        self.pixel_y = self.y * TILE_SIZE
        self.target_x, self.target_y = self.x, self.y
        self.moving = False
        self.speed = 2.1
        self.direction = "right"
        self.sprite_name = "idle_player"
        self.frame = 0
        self.frame_count = 1
        self.frame_timer = 0
        self.frame_delay = 0.15
        self.surf = images.load(self.sprite_name)
        self.frame_width = self.surf.get_width() // self.frame_count
        self.frame_height = self.surf.get_height()

    # Atualiza animação e movimento do player
    def update(self):
        global game_state
        if not self.moving:
            if keyboard.left:
                self.try_move(-1, 0)
                self.direction = "left"
                self.sprite_name = "e_player"
                self.surf = images.load(self.sprite_name)
                self.frame_count = 6
                self.frame_width = self.surf.get_width() // self.frame_count
            elif keyboard.right:
                self.try_move(1, 0)
                self.direction = "right"
                self.sprite_name = "d_player"
                self.surf = images.load(self.sprite_name)
                self.frame_count = 6
                self.frame_width = self.surf.get_width() // self.frame_count
            elif keyboard.up:
                self.try_move(0, -1)
                self.direction = "up"
                self.sprite_name = "d_player"
                self.surf = images.load(self.sprite_name)
                self.frame_count = 6
                self.frame_width = self.surf.get_width() // self.frame_count
            elif keyboard.down:
                self.try_move(0, 1)
                self.direction = "down"
                self.sprite_name = "d_player"
                self.surf = images.load(self.sprite_name)
                self.frame_count = 6
                self.frame_width = self.surf.get_width() // self.frame_count
            else:
                self.sprite_name = "idle_player"
                self.surf = images.load(self.sprite_name)
                self.frame_count = 1
                self.frame_width = self.surf.get_width()
        else:
            self.move_towards_target()
            # Verifica vitória
            if not self.moving and map_matrix[self.y][self.x] == 4:
                game_state = "win"
                victory_sound.play()
        # Atualiza frame da animação
        self.frame_timer += 1 / 60
        if self.frame_timer >= self.frame_delay:
            self.frame = (self.frame + 1) % self.frame_count
            self.frame_timer = 0

    # Movimento suave do player
    def move_towards_target(self):
        tx, ty = self.target_x * TILE_SIZE, self.target_y * TILE_SIZE
        dx, dy = tx - self.pixel_x, ty - self.pixel_y
        dist = math.sqrt(dx**2 + dy**2)
        if dist < self.speed:
            self.pixel_x, self.pixel_y = tx, ty
            self.x, self.y = self.target_x, self.target_y
            self.moving = False
        else:
            self.pixel_x += self.speed * dx / dist
            self.pixel_y += self.speed * dy / dist

    # Tenta mover o player e toca som de passo
    def try_move(self, dx, dy):
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < len(map_matrix[0]) and 0 <= new_y < len(map_matrix):
            if map_matrix[new_y][new_x] in [1, 4]:
                self.target_x, self.target_y = new_x, new_y
                self.moving = True
                step_sound.play()

    # Desenha o player com o frame correto
    def draw(self):
        frame_rect = Rect(self.frame * self.frame_width, 0, self.frame_width, self.frame_height)
        pos = (int(self.pixel_x + TILE_SIZE // 2 - self.frame_width // 2), 
               int(self.pixel_y + TILE_SIZE // 2 - self.frame_height // 2))
        screen.surface.blit(self.surf, pos, area=frame_rect)

# Classe dos inimigos
class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        self.speed = 1.5
        self.moving = False
        self.target_x = self.x
        self.target_y = self.y
        self.frame = 0
        self.frame_timer = 0
        self.frame_delay = 0.15
        self.spritesheet = images.load(ENEMY_SPRITESHEET_NAME)

    # Atualiza animação e movimento do inimigo
    def update(self, player):
        self.frame_timer += 1 / 60
        if self.frame_timer >= self.frame_delay:
            self.frame = (self.frame + 1) % ENEMY_FRAME_COUNT
            self.frame_timer = 0
        if not self.moving:
            moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            best_move = None
            min_dist = float('inf')
            for dx, dy in moves:
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < len(map_matrix[0]) and 0 <= ny < len(map_matrix):
                    if map_matrix[ny][nx] in [1, 4]:
                        dist = abs(player.x - nx) + abs(player.y - ny)
                        if dist < min_dist:
                            min_dist = dist
                            best_move = (nx, ny)
            if best_move:
                self.target_x, self.target_y = best_move
                self.moving = True
        else:
            self.move_towards_target()

    # Movimento suave do inimigo
    def move_towards_target(self):
        tx, ty = self.target_x * TILE_SIZE, self.target_y * TILE_SIZE
        dx, dy = tx - self.pixel_x, ty - self.pixel_y
        dist = math.sqrt(dx**2 + dy**2)
        if dist < self.speed:
            self.pixel_x, self.pixel_y = tx, ty
            self.x, self.y = self.target_x, self.target_y
            self.moving = False
        else:
            self.pixel_x += self.speed * dx / dist
            self.pixel_y += self.speed * dy / dist

    # Desenha o inimigo com o frame correto
    def draw(self):
        frame_rect = enemy_frames[self.frame]
        pos = (
            int(self.pixel_x + TILE_SIZE // 2 - ENEMY_FRAME_WIDTH // 2),
            int(self.pixel_y + TILE_SIZE // 2 - ENEMY_FRAME_HEIGHT // 2)
        )
        screen.surface.blit(self.spritesheet, pos, area=frame_rect)

# Lista de inimigos (pode adicionar mais se quiser)
enemies = [
    Enemy(10, 6),
    Enemy(17, 8),
    Enemy(7, 12)
]

player = Player()

# Inicializa o menu e toca música se ativada
def initialize():
    global menu_instance
    menu_instance = Menu()
    menu_instance.play_menu_music()

initialize()

# Atualiza o estado do jogo
def update():
    global game_state
    if game_state == "game":
        player.update()
        for enemy in enemies:
            enemy.update(player)
            # Verifica colisão com inimigo
            if enemy.x == player.x and enemy.y == player.y:
                game_state = "lose"

# Desenha a tela de acordo com o estado do jogo
def draw():
    if game_state == "menu":
        menu_instance.draw()
    elif game_state == "game":
        draw_map()
        player.draw()
        for enemy in enemies:
            enemy.draw()
    elif game_state == "win":
        screen.fill((0, 0, 0))
        screen.draw.text("Você venceu!", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="yellow")
    elif game_state == "lose":
        screen.fill((0, 0, 0))
        screen.draw.text("Você perdeu!", center=(WIDTH // 2, HEIGHT // 2 - 40), fontsize=60, color="red")
        btn_rect = Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
        screen.draw.filled_rect(btn_rect, "grey")
        screen.draw.text("Jogar Novamente", center=btn_rect.center, fontsize=32, color="white")

# Lida com cliques do mouse (menu e botão de reiniciar)
def on_mouse_down(pos):
    global game_state, player, enemies
    if game_state == "menu":
        menu_instance.handle_click(pos)
    elif game_state == "lose":
        btn_rect = Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
        if btn_rect.collidepoint(pos):
            button_sound.play()
            player = Player()
            enemies = [
                Enemy(10, 6),
                Enemy(17, 8),
                Enemy(7, 12)
            ]
            game_state = "game"
            # Música segue o estado do botão Music ao reiniciar
            if menu_instance.music_enabled:
                music.play('background_music')
            else:
                music.stop()

pgzrun.go()