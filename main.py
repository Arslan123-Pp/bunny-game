import random

import pygame
import sys
import os
import time
from random import choice


def load_image(name):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    # функция возвращает Surface, на котором расположеноизображение
    return image


def terminate():
    pygame.quit()
    sys.exit()
    # аварийное завершение


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
thorns_group = pygame.sprite.Group()
decor_group = pygame.sprite.Group()
finish_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
# группы спрайтов


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
    except FileNotFoundError:
        print('Такого файла не существует')
        sys.exit()
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками (' ')
    return list(map(lambda x: x.ljust(max_width, ' '), level_map))


block_images = {
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
    'decore': load_image('bush1.png'),
    'decorr': load_image('carrot.png'),
}
bunny_animations = {
    'stand': load_image('bunnyStand.png'),
    'run': load_image('bunnyRun.png'),
    'jump': load_image('bunnyJump.png'),
    'fall': load_image('bunnyFall.png'),
    'slide': load_image('bunnySlide.png'),
    'lose': load_image('bunnyLose.png')
}
# хранение изображения блоков, декора, шипов и анимаций кролика в словарях

background = load_image('background.png')
finish = load_image('finish.png')
finish_flag = load_image('finish_flag.png')

tile_width = tile_height = 50
thorn_width = thorn_height = 50
decor_width = decor_height = 50

size = WIDTH, HEIGHT = width, height = 700, 500
# длина, ширина экрана


class Block(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = block_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        # класс иницилизирует и распологает блоки в определенных координатах


class Finish(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, columns=4, rows=1):
        super().__init__(finish_group, all_sprites)
        self.frames = []
        self.cut_sheet(finish_flag, columns, rows)
        self.i, self.counter = 0, 0
        self.image1 = self.frames[self.i]
        self.image = finish
        self.rect = self.image.get_rect().move(
            decor_width * pos_x, decor_height * pos_y - 150)
        # класс иницилизирует и распологает финиш в определенных координатах

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if pygame.sprite.spritecollideany(self, player_group):
            if self.counter % 5 == 0:
                self.image = self.image1
                if self.i < len(self.frames):
                    self.image1 = self.frames[self.i]
                    self.i += 1
            self.counter += 1
        # если игрок соприкоснулся с финишом, начинается анимация поднятия флага


class BackGround(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(decor_group)
        self.image = background
        self.rect = self.image.get_rect()
        self.rect.move(x, y)

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
        self.rect.move(self.dx, self.dy)
        # позиционировать задний фон на объекте target


class Decor(pygame.sprite.Sprite):
    def __init__(self, decor_type, pos_x, pos_y):
        super().__init__(decor_group, all_sprites)
        self.image = decor_images[decor_type]
        if decor_type == 'decore':
            self.rect = self.image.get_rect().move(
                decor_width * pos_x, decor_height * pos_y - 50)
        else:
            self.rect = self.image.get_rect().move(
                decor_width * pos_x, decor_height * pos_y)
        # класс иницилизирует и распологает декор в определенных координатах


class Thorn(pygame.sprite.Sprite):
    def __init__(self, thorn_type, pos_x, pos_y, level):
        super().__init__(thorns_group, all_sprites)
        self.image = thorn_images[thorn_type]
        if level[pos_y][pos_x - 1] != thorn_type[-1]:
            self.rect = self.image.get_rect().move(
                thorn_width * pos_x, thorn_height * pos_y)
        else:
            self.rect = self.image.get_rect().move(
                thorn_width * pos_x + 25, thorn_height * pos_y)
        # класс иницилизирует и распологает шипы в определенных координатах


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y, level):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.i = 0
        self.image = self.frames[self.i]
        self.counter = 0
        self.level = level
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.x = tile_width * pos_x
        self.y = tile_height * pos_y
        self.duration = True
        # определение направления, True - направо, False - налево
        self.inwall, self.fall, self.lose, self.stand = False, False, False, True
        self.kill, self.minijump, self.win = False, False, False
        # определение состояния игрока (скольжение по стене, падение, проигрыш, стояние на месте
        # убиство врага, мини прыжок после убийства врага, победа
        self.speedx, self.speedy = 4, 5
        # определение скорости игрока по x и y
        self.jump, self.jumpCount, self.jumpMx, self.jumpN = False, 0, 1.5, None
        # прыгает ли персонаж, сколько прыжков еще может сделать, максимальная высота прыжка, растояние от земли
        self.mxsx, self.mxsy = self.rect.size
        self.flag = False, False
        # класс иницилизирует и распологает игрока в определенных координатах

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        self.animation()
        if self.stand is True:
            if args and args[0].type == pygame.KEYDOWN:
                self.stand = False
            # если игрок стоит, и пользователь нажимает на любую кнопку, то он перестает стоять
        elif (not pygame.sprite.spritecollideany(self, thorns_group) and
                not pygame.sprite.spritecollideany(self, enemy_group) and self.lose is False):
            # если игрок не соприкоснулся с шипами и врагом, а также он не проиграл, то условие проходит
            if self.duration is True:
                self.rect = self.rect.move(self.speedx, 0)
                self.x += self.speedx
            else:
                self.rect = self.rect.move(-self.speedx, 0)
                self.x -= self.speedx
            # Если направление True, то он идет направо, иначе налево

            th1 = self.level[int(self.y // tile_height)][self.x // tile_width]
            th2 = self.level[int(self.y // tile_height)][(self.x + self.mxsx) // tile_width]
            th3 = self.level[int((self.y + self.mxsy)) // tile_height][self.x // tile_width]
            th4 = self.level[int((self.y + self.mxsy)) // tile_height][(self.x + self.mxsx) // tile_width]
            th5 = self.level[int(self.y + self.mxsy - 5) // tile_height][self.x // tile_width]
            th6 = self.level[int(self.y + self.mxsy - 5) // tile_height][(self.x + self.mxsx) // tile_width]
            # получение высокой и низкой точки координаты игрока

            if (th1 not in ' zxcv' or th2 not in ' zxcv' or th3 not in '123zxcv ' or th4 not in '123zxcv ' or
                    th5 not in ' zxcv' or th6 not in ' zxcv'):
                # если высокая или низкая точка не находятся в воздухе
                if (th3 in ' zxcv' or th4 in ' zxcv') and (th1 in ' zxcv' or th2 in ' zxcv'):
                    # если нижняя точка находится в воздухе, то начинается процесс скольжения по стене
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
                    self.inwall = True
                if th3 not in ' ' and th4 not in ' ':
                    # если нижняя точка не находится в воздухе, то меняется направление игрока
                    self.inwall = False
                    self.duration = not self.duration
            else:
                # если высокая и низкая точка находятся в воздухе, он перестает скользить по стене
                if self.inwall is True:
                    # если он скользил по стене, то меняется направление
                    self.duration = not self.duration
                self.inwall = False

            if th3 not in ' ' and th4 not in ' ' and th5 not in ' ' and th6 not in ' ':
                self.rect = self.rect.move(0, -1)
                self.y -= 1
                self.duration = not self.duration
                # если игрок проваливается под блоки, то он начинает подниматься и менять направление

            if th3 in ' zxcv' and th4 in ' zxcv' and self.jump is False and self.minijump is False:
                self.rect = self.rect.move(0, self.speedy)
                self.y += self.speedy
                self.fall = True
                # если нижняя точка находится в воздухе и игрок не находится в состоянии прыжка, то он падает
            else:
                self.fall = False

            if th3 in '123' or th4 in '123':
                self.jumpCount = 0
                # если игрок на земле, то количество прыжков обнуляется

            if self.minijump is True:
                if self.jumpN - (self.y + self.mxsy) <= 50 and th1 in ' ' and th2 in ' ':
                    self.rect = self.rect.move(0, -self.speedy)
                    self.y -= self.speedy
                    # если игрок находится в состоянии мини прыжка, он ни с чем не столкнулся и он не преодолел 1 блок,
                    # то персонаж летит вверх
                else:
                    self.minijump = False

            if self.jump is True:
                if self.jumpN - (self.y + self.mxsy) <= self.jumpMx * 50 and th1 in ' ' and th2 in ' ':
                    self.rect = self.rect.move(0, -self.speedy)
                    self.y -= self.speedy
                    # если игрок находится в состоянии прыжка, он ни с чем не столкнулся и он не преодолел 1 блок,
                    # то персонаж летит вверх
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
                        # если игрок нажал клавишу space, и если он не находится в состоянии прыжка и персонаж
                        # находится на земле, или он делает второй прыжок, то он переходит в состояние прыжка
        else:
            if self.lose is False:
                self.lose = True
                self.jumpN = self.y + self.mxsy
                self.jump = True
            if self.jump is True:
                if self.jumpN - (self.y + self.mxsy) <= 120:
                    self.rect = self.rect.move(0, -5)
                    self.y -= 5
                else:
                    self.jump = False
            if self.jump is False:
                self.rect = self.rect.move(0, 7)
                self.y += 7
            # если игрок соприкоснулся с врагом не во время падения или соприкоснулся с шипами, то начинается анимация
            # проигрыша

        if pygame.sprite.spritecollideany(self, enemy_group) and self.fall and self.lose is False:
            if self.level[int((self.y + self.mxsy + 40)) // tile_height][self.x // tile_width] == ' ':
                self.kill = True
                self.minijump = True
                self.fall = False
                self.jumpCount = -1
                self.jumpN = self.y + self.mxsy
            # если персонаж соприкоснулся с врагом во время падения и он находится на расстоянии 1 блока от земли
            # то он убивает врага
        else:
            self.kill = False
        if pygame.sprite.spritecollideany(self, finish_group):
            self.win = True
            # если игрок соприкоснулся с финишом, то он побеждает

    def animation(self):
        if (not pygame.sprite.spritecollideany(self, thorns_group) and
                not pygame.sprite.spritecollideany(self, enemy_group) and self.lose is False):
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
                elif self.stand is True:
                    self.image = bunny_animations['stand']
                    self.i = 0
                else:
                    self.image = self.frames[self.i % 4]
                    self.i += 1
                if self.duration is False:
                    self.image = pygame.transform.flip(self.image, True, False)
            self.counter += 1
        else:
            self.image = bunny_animations['lose']
        # происходит анимация персонажа, в зависимости от его нынешнего состояния

    def is_lose(self):
        if self.lose is True:
            return True
        return False
        # функция проверяет, проиграл ли персонаж

    def is_kill(self):
        if self.kill is True:
            return True
        return False
        # функция проверяет, убил ли персонаж врага

    def is_win(self):
        if self.win is True:
            return True
        return False
        # функция проверяет, победил ли персонаж

    def set_pause(self):
        self.stand = True
        # функция останавливает игрока во время паузы


class Enemy(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y, level):
        super().__init__(enemy_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.i = 0
        self.image = self.frames[self.i]
        self.counter = 0
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.x = tile_width * pos_x
        self.y = tile_height * pos_y
        self.mxsx, self.mxsy = self.rect.size
        self.nx, self.ny = pos_x, pos_y
        self.duration = True
        self.speed = 1
        self.level = level
        # класс иницилизирует и распологает игрока в определенных координатах

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.duration:
            self.x += self.speed
            self.rect = self.rect.move(self.speed, 0)
        else:
            self.x -= self.speed
            self.rect = self.rect.move(-self.speed, 0)
        # Если направление True, то враг идет направо, иначе налево
        self.animation()
        th1 = self.level[int(self.y // tile_height)][self.x // tile_width]
        th2 = self.level[int(self.y // tile_height)][(self.x + self.mxsx) // tile_width]
        th3 = self.level[int((self.y + self.mxsy)) // tile_height][self.x // tile_width]
        th4 = self.level[int((self.y + self.mxsy)) // tile_height][(self.x + self.mxsx) // tile_width]
        # получение высокой и низкой точки координаты игрока
        if th1 not in ' ' or th2 not in ' ' or th3 not in '123' or th4 not in '123':
            self.duration = not self.duration
            # если враг натыкается на стену или пропасть, то он меняет направление

    def animation(self):
        if self.counter % 15 == 0:
                self.image = self.frames[self.i % 2]
                self.image = pygame.transform.flip(self.image, True, False)
                self.i += 1
                if self.duration is False:
                    self.image = pygame.transform.flip(self.image, True, False)
        self.counter += 1
        # анимация врага

    def is_touch(self):
        if pygame.sprite.spritecollideany(self, player_group):
            return True
        return False
        # функция проверяет, прикоснулся ли игрок к врагу

    def delete_enemy(self):
        self.kill()
        # функция удаляет врага


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        # зададим начальный сдвиг камеры

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        # сдвинуть объект obj на смещение камеры

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
        # позиционировать камеру на объекте target


def generate_level(level):
    new_player, x, y, lst = None, None, None, []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x].isdigit():
                Block(f'block{level[y][x]}', x, y)
            elif level[y][x] in 'zxcv':
                Thorn(f'thorn{level[y][x]}', x, y, level)
            elif level[y][x] in 'qwert':
                Decor(f'decor{level[y][x]}', x, y)
                level[y] = level[y].replace(level[y][x], ' ', 1)
            elif level[y][x] == 'f':
                Finish(x, y)
                level[y] = level[y].replace('f', ' ', 1)
            elif level[y][x] == '@':
                level[y] = level[y].replace('@', ' ', 1)
                new_player = Player(bunny_animations['run'], 4, 1, x, y, level)
            elif level[y][x] == '!':
                level[y] = level[y].replace('!', ' ', 1)
                enemy = Enemy(load_image('pigWalk.png'), 2, 1, x, y, level)
                lst.append(enemy)
    # вернем игрока, список врагов
    return new_player, lst


screen = pygame.display.set_mode((width, height))
# screen — холст, на котором нужно рисовать

start_img_off = load_image('startBtnof.png')
exit_img_off = load_image('exitBtnof.png')
resume_img_off = load_image('resumeBtnof.png')
restart_img_off = load_image('restartBtnof.png')
exit2_img_off = load_image('exit2Btnof.png')

start_img_on = load_image('startBtnon.png')
exit_img_on = load_image('exitBtnon.png')
resume_img_on = load_image('resumeBtnon.png')
restart_img_on = load_image('restartBtnon.png')
exit2_img_on = load_image('exit2Btnon.png')

pause_img = load_image('pause.png')
loss_img = load_image('loss.png')
complete_img = load_image('complete.png')
# загрузка изображений кнопок

bunny_game1 = load_image('bunny-game1.png')
bunny_game2 = load_image('bunny-game2.png')
bunny_game3 = load_image('bunny-game3.png')
# загрузка изображения названия игры


class Button:
    def __init__(self, x, y, image1, image2, scale):
        width, height = image1.get_width(), image1.get_height()
        self.image = pygame.transform.scale(image1, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.imageon = image2
        self.imageof = image1
        self.clicked = False
        # инициализация и расположение кнопки

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.image = self.imageon
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                action = True
        else:
            self.image = self.imageof
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action
        # рисуем кнопку на экране


def main_menu():
    pygame.display.set_caption('Bunny Game')
    start_button = Button(80, 150, start_img_off, start_img_on, 1)
    exit_button = Button(80, 300, exit_img_off, exit_img_on, 1)
    # Создание кнопок
    bunny_game = random.choice([bunny_game1, bunny_game2, bunny_game3])
    # рандомный выбор надписи
    clock = pygame.time.Clock()
    FPS = 60
    running = True
    while running:
        screen.fill('lightblue')
        screen.blit(bunny_game, (310, 90))
        # отрисовка окна и надписи
        if start_button.draw() is True:
            running = False
            # если пользователь нажал на кнопку 'play', то заканчивается цикл, и окно переходит в раздел уровней
        if exit_button.draw() is True:
            terminate()
            # если пользователь нажал на кнопку 'exit', то происходит завершение работы
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        # окно будет отрисововаться до тех пор, пока пользователь не нажал на одну из кнопок
        pygame.display.update()
        clock.tick(FPS)
    game('map.txt')


def game(name_file):
    level = load_level(name_file)
    ending = ''
    start, timer = None, False
    player, lst_enemies = generate_level(level)
    # получение из функции generate_level игрока, список врагов
    clock = pygame.time.Clock()
    camera = Camera()
    bg = BackGround(0, 0)
    FPS = 60
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.update(event)
                    # если пользователь нажал клавишу space, то вызывается функция update в player
                if event.key == pygame.K_ESCAPE:
                    player.set_pause()
                    if pause() == 1:
                        continue
                    if pause() == 2:
                        ending = 'restart'
                    if pause() == 3:
                        ending = 'exit'
                    # если пользователь нажал на клавишу escape, то вызывается функция pause, если функция
                    # возвращает 1, то цикл продолжается, 2 - цикл останавливается и игра начинается заново
                    # 3 - цикл останавливается и вызывается функция main_menu, после которой открывается окно меню
        screen.fill(pygame.Color('lightblue'))
        decor_group.draw(screen)
        finish_group.draw(screen)
        all_sprites.draw(screen)
        player_group.draw(screen)
        enemy_group.draw(screen)
        if player.is_lose() is False and player.is_win() is False:
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
                bg.update(player)
            # если пользователь проиграл или победил, то камера прекращает следить за персонажем
        if player.is_lose() is True:
            if timer is False:
                start = time.time()
                timer = True
            else:
                if time.time() - start > 1.5:
                    ending = 'loss'
            # если пользователь проиграл, создается таймер, по истечению которого цикл прекращается и вызывается
            # функция loss, открывается окно с заголовком loss
        if player.is_kill() is True:
            for i, enemy in enumerate(lst_enemies):
                if enemy.is_touch():
                    enemy.delete_enemy()
                    del lst_enemies[i]
            # если персонаж убивает кого-нибудь из врагов, то программа смотрит, кого убил игрок, и удаляет врага
        if player.is_win() is True:
            if timer is False:
                start = time.time()
                timer = True
            else:
                if time.time() - start > 1.7:
                    ending = 'win'
            # если пользователь победил, создается таймер, по истечению которого цикл прекращается и вызывается
            # функция win, открывается окно с заголовком celebrate
        if ending:
            running = False
            # если ending больше не пустая строка то цикл прекращается
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)
    all_sprites.empty()
    tiles_group.empty()
    thorns_group.empty()
    decor_group.empty()
    finish_group.empty()
    player_group.empty()
    background_group.empty()
    enemy_group.empty()
    # после окончания цикла все спрайты очищаются
    if ending == 'restart':
        game(name_file)
    elif ending == 'exit':
        main_menu()
    elif ending == 'loss':
        if loss() == 1:
            game(name_file)
        elif loss() == 2:
            main_menu()
    elif ending == 'win':
        if win() == 1:
            game(name_file)
        elif win() == 2:
            main_menu()


def pause():
    pygame.init()
    paused = True
    resume_button = Button(width // 2 - (324 // 2), 120, resume_img_off, resume_img_on, 1)
    restart_button = Button(width // 2 - (324 // 2), 235, restart_img_off, restart_img_on, 1)
    exit_button = Button(width // 2 - (324 // 2), 350, exit2_img_off, exit2_img_on, 1)
    # Создание кнопок
    clock = pygame.time.Clock()
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        if resume_button.draw() is True:
            return 1
            # если пользователь нажал на кнопку resume, то цикл в функции game() прододжается
        if restart_button.draw() is True:
            return 2
            # если пользователь нажал на кнопку restart, то цикл в функции game() прекращается и опять вызывается
        if exit_button.draw() is True:
            return 3
            # если пользователь нажал на кнопку exit, то цикл в функции game() прекращается и вызывается функция
            # main_menu, и открывается окно меню
        screen.blit(pause_img, (width // 2 - (270 // 2), 10))
        pygame.display.update()
        clock.tick(15)


def loss():
    pygame.init()
    running = True
    restart_button = Button(width // 2 - (324 // 2), 130, restart_img_off, restart_img_on, 1)
    exit_button = Button(width // 2 - (324 // 2), 245, exit2_img_off, exit2_img_on, 1)
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        if restart_button.draw() is True:
            return 1
            # если пользователь нажал на кнопку restart, то цикл в функции game() прекращается и опять вызывается
        if exit_button.draw() is True:
            return 2
            # если пользователь нажал на кнопку exit, то цикл в функции game() прекращается и вызывается функция
            # main_menu, и открывается окно меню
        screen.blit(loss_img, (width // 2 - (320 // 2), 10))
        pygame.display.update()
        clock.tick(15)


def win():
    pygame.init()
    running = True
    restart_button = Button(width // 2 - (324 // 2), 130, restart_img_off, restart_img_on, 1)
    exit_button = Button(width // 2 - (324 // 2), 245, exit2_img_off, exit2_img_on, 1)
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        if restart_button.draw() is True:
            return 1
            # если пользователь нажал на кнопку restart, то цикл в функции game() прекращается и опять вызывается
        if exit_button.draw() is True:
            return 2
            # если пользователь нажал на кнопку exit, то цикл в функции game() прекращается и вызывается функция
            # main_menu, и открывается окно меню
        screen.blit(complete_img, (width // 2 - (400 // 2), 10))
        pygame.display.update()
        clock.tick(15)


if __name__ == '__main__':
    main_menu()