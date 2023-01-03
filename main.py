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


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
thorns_group = pygame.sprite.Group()
decor_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()

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

    return list(map(lambda x: x.ljust(max_width, ' '), level_map))


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

thorn_images = {
    'thornz': load_image('thorn1.png'),
    'thornx': load_image('thorn2.png'),
    'thornc': load_image('thorn3.png'),
    'thornv': load_image('thorn4.png')
}

decor_images = {
    'decorq': load_image('zabor.png'),
    'decorw': load_image('grass1.png'),
    'decore': load_image('bush1.png')
}
background = load_image('background.png')
player_image = load_image('mar.png')

tile_width = tile_height = 50
thorn_width = thorn_height = 50
decor_width = decor_height = 50

bunny_animations = {
    'run': load_image('bunnyRun.png'),
    'jump': load_image('bunnyJump.png'),
    'fall': load_image('bunnyFall.png'),
    'slide': load_image('bunnySlide.png')
}


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class BackGround(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(decor_group)
        self.image = background
        self.rect = self.image.get_rect()
        self.rect.move(x, y)

    def update(self, x, y):
        self.rect.move(x, y)


class Decor(pygame.sprite.Sprite):
    def __init__(self, decor_type, pos_x, pos_y):
        super().__init__(decor_group, all_sprites)
        self.image = decor_images[decor_type]
        if decor_type != 'decore':
            self.rect = self.image.get_rect().move(
                decor_width * pos_x, decor_height * pos_y)
        else:
            self.rect = self.image.get_rect().move(
                decor_width * pos_x, decor_height * pos_y - 50)


class Thorn(pygame.sprite.Sprite):
    def __init__(self, thorn_type, pos_x, pos_y):
        super().__init__(thorns_group, all_sprites)
        self.image = thorn_images[thorn_type]
        if level[pos_y][pos_x - 1] != thorn_type[-1]:
            self.rect = self.image.get_rect().move(
                thorn_width * pos_x, thorn_height * pos_y)
        else:
            self.rect = self.image.get_rect().move(
                thorn_width * pos_x + 25, thorn_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.i = 0
        self.counter = 0

        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.x = tile_width * pos_x
        self.y = tile_height * pos_y
        self.duration = True
        self.inwall, self.fall = False, False
        self.speedx, self.speedy = 4, 5
        self.jump, self.jumpCount, self.jumpMx, self.jumpN = False, 0, 1.5, None
        self.mxsx, self.mxsy = self.rect.size
        self.error, self.flag = False, False

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        if self.counter % 6 == 0:
            if self.jump is True:
                self.image = bunny_animations['jump']
                self.i = 0
            elif self.fall is True:
                self.image = bunny_animations['fall']
                self.i = 0
            elif self.inwall is True:
                self.image = bunny_animations['slide']
                self.i = 0
            else:
                self.image = self.frames[self.i % 4]
                self.i += 1
            if self.duration is False:
                self.image = pygame.transform.flip(self.image, True, False)
        self.counter += 1
        if not pygame.sprite.spritecollideany(self, thorns_group):
            if self.duration:
                self.rect = self.rect.move(self.speedx, 0)
                self.x += self.speedx
            else:
                self.rect = self.rect.move(-self.speedx, 0)
                self.x -= self.speedx

            th1 = level[int(self.y // tile_height)][self.x // tile_width]
            th2 = level[int(self.y // tile_height)][(self.x + self.mxsx) // tile_width]
            th3 = level[int((self.y + self.mxsy)) // tile_height][self.x // tile_width]
            th4 = level[int((self.y + self.mxsy)) // tile_height][(self.x + self.mxsx) // tile_width]
            th5 = level[int(self.y + self.mxsy - 5) // tile_height][self.x // tile_width]
            th6 = level[int(self.y + self.mxsy - 5) // tile_height][(self.x + self.mxsx) // tile_width]

            if (th1 not in ' ' or th2 not in ' ' or th3 not in '123 ' or th4 not in '123 ' or
                    th5 not in ' ' or th6 not in ' '):
                if (th3 in ' ' or th4 in ' ') and (th1 in ' ' or th2 in ' '):
                    self.inwall = True
                    self.jumpCount = -1
                    self.jump = False
                    self.rect = self.rect.move(0, 3)
                    self.y += 3
                    if self.duration:
                        self.rect = self.rect.move(-self.speedx, 0)
                        self.x -= self.speedx
                    else:
                        self.rect = self.rect.move(self.speedx, 0)
                        self.x += self.speedx
                if th3 not in ' ' and th4 not in ' ':
                    self.inwall = False
                    self.duration = not self.duration
            else:
                if self.inwall is True:
                    self.duration = not self.duration
                self.inwall = False

            if th3 not in ' ' and th4 not in ' ' and th5 not in ' ' and th6 not in ' ':
                self.rect = self.rect.move(0, -1)
                self.y -= 1
                self.error = True
            else:
                self.error = False

            if self.error is True:
                self.duration = not self.duration

            if th3 in ' ' and th4 in ' ' and self.jump is False:
                self.rect = self.rect.move(0, self.speedy)
                self.y += self.speedy
                self.fall = True
            else:
                self.fall = False

            if th3 in '123' or th4 in '123':
                self.jumpCount = 0

            if self.jump is True:
                if self.jumpN - (self.y + self.mxsy) <= self.jumpMx * 50 and th1 in ' ' and th2 in ' ':
                    self.rect = self.rect.move(0, -self.speedy)
                    self.y -= self.speedy
                else:
                    self.jump = False

            if args and args[0].type == pygame.KEYDOWN:
                if args[0].key == pygame.K_SPACE:
                    if (self.jump is False and (th3 in '123' or th4 in '123')) or self.jumpCount < 1:
                        if self.inwall is True:
                            self.duration = not self.duration
                            self.inwall = False
                        self.jump = True
                        self.jumpCount += 1
                        self.jumpN = self.y + self.mxsy


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
        bg.update(self.dx, self.dy - 300)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x].isdigit():
                Tile(f'block{level[y][x]}', x, y)
            elif level[y][x] in 'zxcv':
                Thorn(f'thorn{level[y][x]}', x, y)
            elif level[y][x] in 'qwe':
                Decor(f'decor{level[y][x]}', x, y)
                level[y] = level[y].replace(level[y][x], ' ', 1)
            elif level[y][x] == '@':
                level[y] = level[y].replace('@', ' ')
                new_player = Player(bunny_animations['run'], 4, 1, x, y)
    return new_player, x, y


if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT = width, height = 700, 500

    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Bunny Game')
    level = load_level(name_file)
    player, level_x, level_y = generate_level(level)
    camera = Camera()
    bg = BackGround(0, 0)
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
        decor_group.draw(screen)
        all_sprites.draw(screen)
        player_group.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        clock.tick(FPS)
    pygame.quit()