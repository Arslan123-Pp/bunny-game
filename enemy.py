import pygame
import sys
import os


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    clock = pygame.time.Clock()
    FPS = 50
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

name_file = 'map.txt'


def load_level(filename):
    filename = "data/" + filename

    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
    except FileNotFoundError:
        print('Такого файла не существует')
        sys.exit()

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 10)
        self.x = tile_width * pos_x + 15
        self.y = tile_height * pos_y + 10
        self.duration = True
        self.speed = 4

    def update(self):
        if self.duration:
            self.x += self.speed
            self.rect = self.rect.move(self.speed, 0)
        else:
            self.x -= self.speed
            self.rect = self.rect.move(-self.speed, 0)
        if level[(self.y + 40) // tile_height][(self.x) // tile_width] != '.':
            self.rect = self.rect.move(0, 5)
            self.y += 5
        if (level[self.y // tile_height][(self.x + 20) // tile_width] == '.' or
                level[self.y // tile_height][(self.x) // tile_width] == '.'):
            self.duration = not self.duration


class Enemy(pygame.sprite.Sprite):
    image = load_image("box.png", -1)

    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.image = Enemy.image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y - 10)
        self.x = tile_width * pos_x
        self.y = tile_height * pos_y
        self.nx = pos_x
        self.ny = pos_y
        self.duration = True
        self.speed = 3

    def update(self):
        if self.duration:
            self.x += self.speed
            self.rect = self.rect.move(self.speed, 0)
        else:
            self.x -= self.speed
            self.rect = self.rect.move(-self.speed, 0)
        if level[(self.y + 40) // tile_height][(self.x) // tile_width] != '.':
            self.rect = self.rect.move(0, 5)
            self.y += 5
        x = self.x // tile_width
        if (level[self.y // tile_height][(self.x + 20) // tile_width] == '.' or
                level[self.y // tile_height][(self.x) // tile_width] == '.') or\
                abs(self.nx - x) == 2:
            self.duration = not self.duration






class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


def generate_level(level):
    new_player, x, y = None, None, None
    new_enemy, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                new_player = Player(x, y)
            elif level[y][x] == '!':
                new_enemy = Enemy(x, y)
    return new_player, x, y


if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT = width, height = 500, 500

    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Перемещение героя')
    level = load_level(name_file)
    player, level_x, level_y = generate_level(level)
    start_screen()
    camera = Camera()
    clock = pygame.time.Clock()
    FPS = 60

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(pygame.Color('black'))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        clock.tick(FPS) / 1000
    pygame.quit()
