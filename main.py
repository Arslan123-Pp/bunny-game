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

    return list(map(lambda x: x.ljust(max_width, '4'), level_map))


tile_images = {
    'block1': load_image('block1.png'),
    'block2': load_image('block2.png'),
    'block3': load_image('block3.png'),
    'block4': load_image('block4.png'),
    'block5': load_image('block5.png'),
    'block6': load_image('block6.png'),
    'block7': load_image('block7.png'),
    'block8': load_image('block8.png'),
    'block9': load_image('block9.png')
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
        self.duration = False
        self.speed = 4
        self.jump = False
        self.jumpCount = 0
        self.jumpMx = 2
        self.jumpN = None

    def update(self, *args):
        x = (self.x + 24) // tile_width
        if self.duration:
            self.x += self.speed
            self.rect = self.rect.move(self.speed, 0)
        else:
            self.x -= self.speed
            self.rect = self.rect.move(-self.speed, 0)
        if args and args[0].type == pygame.KEYDOWN:
            if ((not self.jump and level[(self.y + 40) // tile_height][(self.x) // tile_width] != ' ' and
                 level[(self.y + 40) // tile_height][x] != ' ') or
                    self.jumpCount < 2):
                if args[0].key == pygame.K_SPACE:
                    self.jump = True
                    self.jumpN = self.y // tile_height
                    self.jumpCount += 1
                    if level[self.y // tile_height][x] != ' ':
                        self.duration = False
                        self.x -= 10
                        self.rect = self.rect.move(-10, 0)
                    if level[self.y // tile_height][self.x // tile_width] != ' ':
                        self.duration = True
                        self.x += self.speed
                        self.rect = self.rect.move(self.speed, 0)
        if not self.jump:
            if level[(self.y + 40) // tile_height][self.x // tile_width] == ' ' \
                    or level[(self.y + 40) // tile_height][x] == ' ':
                self.rect = self.rect.move(0, 4)
                self.y += 4
            else:
                self.jumpCount = 0
        if self.jump:
            if (level[self.y // tile_height][self.x // tile_width] == ' ' and
                    abs(self.y // tile_height - self.jumpN) != self.jumpMx):
                self.rect = self.rect.move(0, -4)
                self.y -= 4
            else:
                self.jump = False

        if level[self.y // tile_height][x] != ' ' or level[self.y // tile_height][self.x // tile_width] != ' ':
            if (level[(self.y + 40) // tile_height][self.x // tile_width] == ' ' or
                     level[(self.y + 40) // tile_height][x] == ' '):
                self.jumpCount = 0
                if self.duration:
                    self.x -= self.speed
                    self.rect = self.rect.move(-self.speed, 0)
                else:
                    self.x += self.speed
                    self.rect = self.rect.move(self.speed, 0)
            else:
                if level[self.y // tile_height][x] != ' ' and self.duration is True:
                    self.duration = False
                if level[self.y // tile_height][self.x // tile_width] != ' ' and self.duration is False:
                    self.duration = True

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
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x].isdigit():
                Tile(f'block{level[y][x]}', x, y)
            elif level[y][x] == '@':
                level[y] = level[y].replace('@', ' ')
                new_player = Player(x, y)
    return new_player, x, y


if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT = width, height = 700, 500

    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Bunny game')
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.update(event)
        screen.fill(pygame.Color('lightblue'))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        clock.tick(FPS) / 1000
    pygame.quit()
