import pygame
import sys
import os
import time
import random
pygame.font.init()


def load_image(name):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    # функция возвращает Surface, на котором расположено изображение
    return image


def terminate():
    # аварийное завершение
    pygame.quit()
    sys.exit()


# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
thorns_group = pygame.sprite.Group()
decor_group = pygame.sprite.Group()
finish_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
hitbox_group = pygame.sprite.Group()
trampoline_group = pygame.sprite.Group()
carrot_group = pygame.sprite.Group()


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


# хранение изображения блоков, декора, шипов и анимаций кролика и его скинов в словарях
block_images = {
    'block0': load_image('block0.png'),
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
    'decort': load_image('wall1.png'),
    'decory': load_image('tree1.png'),
    'decoru': load_image('tree2.png')
}
bunny_animations = [{
    'stand': load_image('bunnyStand.png'),
    'run': load_image('bunnyRun.png'),
    'jump': load_image('bunnyJump.png'),
    'fall': load_image('bunnyFall.png'),
    'slide': load_image('bunnySlide.png'),
    'lose': load_image('bunnyLose.png'),
}, {
    'stand': load_image('bunnyStand2.png'),
    'run': load_image('bunnyRun2.png'),
    'jump': load_image('bunnyJump2.png'),
    'fall': load_image('bunnyFall2.png'),
    'slide': load_image('bunnySlide2.png'),
    'lose': load_image('bunnyLose2.png'),
}]

# переменная для скина
skin = 0

# загрузка изображений
carrot = load_image('carrot_game.png')
carrot_1 = load_image('carrot_1.png')
backgrounds = load_image('background.png')
background = pygame.transform.scale(backgrounds, (950, 650))
finish = load_image('finish.png')
finish_flag = load_image('finish_flag.png')
trampoline = load_image('trampoline.png')

# иницилизация и загрузка звука
pygame.mixer.init()
button_sound = pygame.mixer.Sound('data/button_sound.mp3')
jump_sound = pygame.mixer.Sound('data/jump_sound.mp3')
loss_sound = pygame.mixer.Sound('data/loss_sound.mp3')
win_sound = pygame.mixer.Sound('data/win_sound.mp3')
minijump_sound = pygame.mixer.Sound('data/minijump_sound.mp3')
trampoline_sound = pygame.mixer.Sound('data/trampoline_sound.mp3')
music, sound = True, True
isclicked, begin_time = False, None

# количество кадров в секунду
FPS = 30

tile_width = tile_height = 50
thorn_width = thorn_height = 50
decor_width = decor_height = 50

# длина, ширина экрана
size = WIDTH, HEIGHT = width, height = 700, 500

# сколько уровней в данный момент
maps = 3


class Block(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        # класс иницилизирует и распологает блок в определенных координатах
        super().__init__(tiles_group, all_sprites)
        self.image = block_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Trampoline(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        # класс иницилизирует и распологает трамплин в определенных координатах
        super().__init__(trampoline_group, all_sprites)
        self.image = trampoline
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 2, tile_height * pos_y + 38)


class Finish(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, columns=4, rows=1):
        # класс иницилизирует и распологает финиш в определенных координатах
        super().__init__(finish_group, all_sprites)
        self.frames = []
        self.cut_sheet(finish_flag, columns, rows)
        self.i, self.counter = 0, 0
        self.image1 = self.frames[self.i]
        self.image = finish
        self.rect = self.image.get_rect().move(
            decor_width * pos_x, decor_height * pos_y - 150)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        # если игрок соприкоснулся финиша, начинается анимация поднятия флага
        if pygame.sprite.spritecollideany(self, player_group):
            if self.counter % 2 == 0:
                self.image = self.image1
                if self.i < len(self.frames):
                    self.image1 = self.frames[self.i]
                    self.i += 1
            self.counter += 1


class BackGround(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(decor_group)
        self.image = background
        self.rect = self.image.get_rect()
        self.rect.move(x, y)

    def update(self, target):
        # позиционировать задний фон на объекте target
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
        self.rect.move(self.dx, self.dy)


class Decor(pygame.sprite.Sprite):
    def __init__(self, decor_type, pos_x, pos_y, level):
        # класс иницилизирует и распологает декор в определенных координатах
        super().__init__(decor_group, all_sprites)
        self.image = decor_images[decor_type]
        if decor_type == 'decore':
            self.rect = self.image.get_rect().move(
                decor_width * pos_x, decor_height * pos_y - 50)
        elif decor_type == 'decort':
            self.rect = self.image.get_rect().move(
                decor_width * pos_x, decor_height * pos_y - 250)
        elif decor_type == 'decory':
            self.rect = self.image.get_rect().move(
                decor_width * pos_x, decor_height * pos_y - 300)
        elif decor_type == 'decoru':
            if level[pos_y + 1][pos_x] == 'v':
                self.rect = self.image.get_rect().move(
                    decor_width * pos_x, decor_height * pos_y - 250)
            else:
                self.rect = self.image.get_rect().move(
                    decor_width * pos_x, decor_height * pos_y - 300)
        else:
            self.rect = self.image.get_rect().move(
                decor_width * pos_x, decor_height * pos_y)


class Thorn(pygame.sprite.Sprite):
    def __init__(self, thorn_type, pos_x, pos_y, level):
        # класс иницилизирует и распологает шипы в определенных координатах
        super().__init__(thorns_group, all_sprites)
        self.image = thorn_images[thorn_type]
        d = {'z': 15, 'x': -15, 'c': 0, 'v': 0}
        if level[pos_y][pos_x - 1] != thorn_type[-1]:
            if thorn_type[-1] != 'v':
                self.rect = self.image.get_rect().move(
                    thorn_width * pos_x + d[thorn_type[-1]], thorn_height * pos_y)
            else:
                self.rect = self.image.get_rect().move(
                    thorn_width * pos_x, thorn_height * pos_y + 15)
        else:
            if thorn_type[-1] != 'v':
                self.rect = self.image.get_rect().move(
                    thorn_width * pos_x + 25 + + d[thorn_type[-1]], thorn_height * pos_y)
            else:
                self.rect = self.image.get_rect().move(
                    thorn_width * pos_x + 25, thorn_height * pos_y + 15)


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y, level):
        # класс иницилизирует и распологает игрока в определенных координатах
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
        # определение направления, True - направо, False - налево
        self.duration = True
        # определение состояния игрока (скольжение по стене, падение, проигрыш, стояние на месте
        # убиство врага, мини прыжок после убийства врага, победа
        self.inwall, self.fall, self.lose, self.stand = False, False, False, True
        self.kill, self.minijump, self.win, self.trampolinejump = False, False, False, False
        # определение скорости игрока по x и y
        self.speedx, self.speedy, self.speedup = 9, 10, 13
        self.acceleration = 1
        # прыгает ли персонаж, сколько прыжков еще может сделать, максимальная высота прыжка, растояние от земли
        self.jump, self.jumpCount, self.jumpMx, self.jumpN = False, 0, 1.6, None
        self.mxsx, self.mxsy = self.rect.size
        self.flag = False, False

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        if self.jumpCount >= 1 and args and self.stand is False:
            return
        self.animation()
        # если игрок стоит, и пользователь нажимает на любую кнопку, то он перестает стоять
        if self.stand is True:
            if args and args[0].type == pygame.KEYDOWN:
                self.stand = False
        # если игрок не соприкоснулся с шипами и врагом, а также он не проиграл, то условие проходит
        elif (not pygame.sprite.spritecollideany(self, thorns_group) and
                not pygame.sprite.spritecollideany(self, hitbox_group) and self.lose is False):
            # Если направление True, то он идет направо, иначе налево
            if self.inwall is False:
                if self.duration is True:
                    self.rect = self.rect.move(self.speedx, 0)
                    self.x += self.speedx
                else:
                    self.rect = self.rect.move(-self.speedx, 0)
                    self.x -= self.speedx

            # получение высокой и низкой точки координаты игрока
            th1 = self.level[int(self.y // tile_height)][self.x // tile_width]
            th2 = self.level[int(self.y // tile_height)][(self.x + self.mxsx) // tile_width]
            th3 = self.level[int((self.y + self.mxsy)) // tile_height][self.x // tile_width]
            th4 = self.level[int((self.y + self.mxsy)) // tile_height][(self.x + self.mxsx) // tile_width]
            th5 = self.level[int(self.y + self.mxsy - 3) // tile_height][self.x // tile_width]
            th6 = self.level[int(self.y + self.mxsy - 3) // tile_height][(self.x + self.mxsx) // tile_width]
            th7 = self.level[int(self.y + self.mxsy // 2) // tile_height][self.x // tile_width]
            th8 = self.level[int(self.y + self.mxsy // 2) // tile_height][(self.x + self.mxsx) // tile_width]

            # если высокая или низкая точка не находятся в воздухе
            if th7 not in ' zxcv' or th8 not in ' zxcv':
                if (th3 in '123' and th4 in '456') or (th4 in '123' and th3 in '456'):
                    self.duration = not self.duration
                    self.inwall = False
                else:
                    self.jumpCount = -1
                    self.inwall = True
            if self.inwall is True:
                self.y += 5
                self.rect = self.rect.move(0, 5)

            # если нижняя точка находится в воздухе и игрок не находится в состоянии прыжка, то он падает
            if th3 in ' zxcv' and th4 in ' zxcv' and self.jump is False and self.minijump is False:
                self.rect = self.rect.move(0, self.speedy + self.acceleration)
                self.y += self.speedy + self.acceleration
                self.fall = True
                if self.counter % 3 == 0:
                    self.acceleration += 1
                if self.inwall is True:
                    self.duration = not self.duration
                    self.inwall = False
            else:
                self.fall = False
                self.acceleration = 1

            # если игрок на земле, то количество прыжков обнуляется
            if th3 in '123' or th4 in '123':
                self.jumpCount = 0

            # если игрок находится в состоянии мини прыжка, он ни с чем не столкнулся и он не преодолел 1 блок,
            # то персонаж летит вверх
            if self.minijump is True:
                if self.jumpN - (self.y + self.mxsy) <= 50 and th1 in ' ' and th2 in ' ':
                    if sound is True:
                        minijump_sound.play()
                    self.rect = self.rect.move(0, -self.speedy)
                    self.y -= self.speedy
                else:
                    self.minijump = False
            if pygame.sprite.spritecollideany(self, trampoline_group) and self.fall is True:
                trampoline_sound.play()
                self.trampolinejump = True
                self.jump = True
                self.jumpCount = 3

            # если игрок находится в состоянии прыжка, он ни с чем не столкнулся и он не преодолел 1 блок,
            # то персонаж летит вверх
            if self.jump is True:
                c = 0
                if self.trampolinejump is True:
                    c = 5
                    self.speedup = 21
                if self.jumpN - (self.y + self.mxsy) <= (self.jumpMx + c) * 50 and th1 in ' ' and th2 in ' ':
                    self.rect = self.rect.move(0, -self.speedup - self.acceleration)
                    self.y -= self.speedup + self.acceleration
                    if self.counter % 3 == 0:
                        self.acceleration += 1
                else:
                    self.speedup = 13
                    self.jump = False
                    self.trampolinejump = False
                    self.acceleration = 1

            # если игрок нажал клавишу space, и если он не находится в состоянии прыжка и персонаж
            # находится на земле, или он делает второй прыжок, то он переходит в состояние прыжка
            if args and args[0].type == pygame.KEYDOWN:
                if args[0].key == pygame.K_SPACE:
                    if (self.jump is False and (th3 in '123' or th4 in '123')) or self.jumpCount < 1:
                        if self.inwall is True:
                            self.duration = not self.duration
                            self.inwall = False
                        self.jump = True
                        self.trampolinejump = False
                        self.jumpCount += 1
                        self.jumpN = self.y + self.mxsy
                        if sound is True:
                            jump_sound.play()
        # если игрок соприкоснулся с врагом не во время падения или соприкоснулся с шипами, то начинается анимация
        # проигрыша
        else:
            if self.lose is False:
                self.lose = True
                self.jumpN = self.y + self.mxsy
                self.jump = True
            if self.jump is True:
                if self.jumpN - (self.y + self.mxsy) <= 120:
                    self.rect = self.rect.move(0, -10)
                    self.y -= 10
                else:
                    self.jump = False
            if self.jump is False:
                self.rect = self.rect.move(0, 15)
                self.y += 15

        # если персонаж соприкоснулся с врагом во время падения и он находится на расстоянии 1 блока от земли
        # то он убивает врага
        if pygame.sprite.spritecollideany(self, hitbox_group) and self.fall and self.lose is False:
            self.kill = True
        else:
            self.kill = False

        # если игрок соприкоснулся с финишом, то он побеждает
        if pygame.sprite.spritecollideany(self, finish_group):
            self.win = True

    def animation(self):
        # происходит анимация персонажа, в зависимости от его нынешнего состояния
        if (not pygame.sprite.spritecollideany(self, thorns_group) and
                not pygame.sprite.spritecollideany(self, hitbox_group) and self.lose is False):
            if self.counter % 3 == 0:
                if self.jump is True:
                    self.image = bunny_animations[skin]['jump']
                    self.i = 0
                elif self.fall is True:
                    self.image = bunny_animations[skin]['fall']
                    self.i = 0
                elif self.inwall is True:
                    self.image = bunny_animations[skin]['slide']
                    self.i = 0
                elif self.stand is True:
                    self.image = bunny_animations[skin]['stand']
                    self.i = 0
                else:
                    self.image = self.frames[self.i % 4]
                    self.i += 1
                if self.duration is False:
                    self.image = pygame.transform.flip(self.image, True, False)
            self.counter += 1
        else:
            self.image = bunny_animations[skin]['lose']

    def is_touch_pig(self):
        if self.level[int((self.y + self.mxsy + 30)) // tile_height][self.x // tile_width] == ' ':
            return True
        return False

    def is_touch_bug(self):
        if self.level[int((self.y + self.mxsy + 20)) // tile_height][self.x // tile_width] == ' ':
            return True
        return False

    def do_minijump(self):
        self.minijump, self.fall = True, False
        self.jumpCount = -1
        self.jumpN = self.y + self.mxsy

    def is_lose(self):
        # функция проверяет, проиграл ли персонаж
        if self.lose is True:
            return True
        return False

    def is_kill(self):
        # функция проверяет, убил ли персонаж врага
        if self.kill is True:
            return True
        return False

    def is_win(self):
        # функция проверяет, победил ли персонаж
        if self.win is True:
            return True
        return False

    def set_pause(self):
        # функция останавливает игрока во время паузы
        self.stand = True


# класс Carrot по задумке зайчик собирает морковки в процессе игры и может воскреснуть за использование их
# класс отправлен в доработку, в будущем планируется реализация
class Carrot(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, level):
        # класс иницилизирует и распологает морковку в определенных координатах
        super().__init__(carrot_group, all_sprites)
        self.image = carrot_1
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.x = tile_width * pos_x
        self.y = tile_height * pos_y
        self.level = level


    def update(self):
        pass

    def is_touch(self):
        # функция проверяет, прикоснулся ли игрок к морковке
        if pygame.sprite.spritecollideany(self, player_group):
            return True
        return False

    def delete_carrot(self):
        # функция удаляет морковку
        self.rect.move(0, 0)
        self.kill()


class EnemyPig(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y, level):
        # класс иницилизирует и распологает врага свинью в определенных координатах
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
        self.speed = 4
        self.level = level

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        # Если направление True, то враг свинья идет направо, иначе налево
        if self.duration:
            self.x += self.speed
            self.rect = self.rect.move(self.speed, 0)
        else:
            self.x -= self.speed
            self.rect = self.rect.move(-self.speed, 0)
        self.animation()

        # получение высокой и низкой точки координаты врага
        th1 = self.level[int(self.y // tile_height)][self.x // tile_width]
        th2 = self.level[int(self.y // tile_height)][(self.x + self.mxsx) // tile_width]
        th3 = self.level[int((self.y + self.mxsy)) // tile_height][self.x // tile_width]
        th4 = self.level[int((self.y + self.mxsy)) // tile_height][(self.x + self.mxsx) // tile_width]

        # если враг натыкается на стену или пропасть, то он меняет направление
        if th1 not in ' ' or th2 not in ' ' or th3 not in '123' or th4 not in '123':
            self.duration = not self.duration

    def animation(self):
        # анимация ходьбы врага
        if self.counter % 6 == 0:
            self.image = self.frames[self.i % 2]
            self.i += 1
            self.image = pygame.transform.flip(self.image, True, False)
            if self.duration is False:
                self.image = pygame.transform.flip(self.image, True, False)
        self.counter += 1

    def is_touch(self):
        # функция проверяет, прикоснулся ли игрок к врагу
        if pygame.sprite.spritecollideany(self, player_group):
            return True
        return False

    def get_duration(self):
        # функция возвращает направление врага
        return self.duration

    def delete_enemy(self):
        # функция удаляет врага
        self.image = self.frames[1]
        self.rect.move(0, 10)
        self.kill()


class EnemyBug(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y, duration):
        # класс иницилизирует и распологает врага жука в определенных координатах
        super().__init__(enemy_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        if duration is False:
            for i in range(len(self.frames)):
                self.frames[i] = pygame.transform.flip(self.frames[i], True, False)
        self.counter, self.i = 0, 0
        self.image = self.frames[self.i]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.angryMode = False

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.animation()

    def animation(self):
        # анимация появления шипов у врага
        self.counter += 1
        if self.counter % 100 == 0:
            self.angryMode = not self.angryMode
            if self.angryMode is True:
                self.i = 3
            else:
                self.i = 1
        if self.angryMode is False:
            if self.counter % 10 == 0:
                self.image = self.frames[self.i % 2]
                self.i += 1
        else:
            if self.counter % 5 == 0:
                self.image = self.frames[self.i]
                if self.i < 4:
                    self.i += 1

    def is_touch(self):
        # функция проверяет, прикоснулся ли игрок к врагу, если он не в злом режиме
        if pygame.sprite.spritecollideany(self, player_group) and self.angryMode is False:
            return True
        return False

    def delete_enemy(self):
        # функция удаляет врага
        self.kill()


class HitBox(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, w, h, d1, d2):
        # класс иницилизирует и распологает хитбокс врага в определенных координатах
        super().__init__(hitbox_group, all_sprites)
        self.image = pygame.Surface((w, h),
                                    pygame.SRCALPHA)
        self.image.fill('blue')
        self.image.set_alpha(0)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + d1, tile_height * pos_y + d2)
        self.x = tile_width * pos_x + d1
        self.y = tile_height * pos_y + d2
        self.duration = True
        self.speed = 4

    def update(self, *duration):
        if duration:
            if duration[0] is True:
                self.rect = self.rect.move(self.speed, 0)
            else:
                self.rect = self.rect.move(-self.speed, 0)

    def is_touch(self):
        # функция проверяет, прикоснулся ли игрок к хитбоксу врага
        if pygame.sprite.spritecollideany(self, player_group):
            return True
        return False

    def delete_hitbox(self):
        # функция удаляет хитбокс
        self.kill()


class Camera:
    def __init__(self):
        # зададим начальный сдвиг камеры
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        # сдвинуть объект obj на смещение камеры
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        # позиционировать камеру на объекте target
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


def generate_level(level):
    new_player, x, y, lst, lst2, lst3, lst4 = None, None, None, [], [], [], []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x].isdigit():
                Block(f'block{level[y][x]}', x, y)
            elif level[y][x] in 'zxcv':
                Thorn(f'thorn{level[y][x]}', x, y, level)
            elif level[y][x] in 'qwertyu':
                Decor(f'decor{level[y][x]}', x, y, level)
                level[y] = level[y].replace(level[y][x], ' ', 1)
            elif level[y][x] == 'h':
                Carrot(x, y, level)
            elif level[y][x] == 'f':
                Finish(x, y)
                level[y] = level[y].replace('f', ' ', 1)
            elif level[y][x] == 'l':
                Trampoline(x, y)
                level[y] = level[y].replace('l', ' ', 1)
            elif level[y][x] == '@':
                level[y] = level[y].replace('@', ' ', 1)
                new_player = Player(bunny_animations[skin]['run'], 4, 1, x, y, level)
            elif level[y][x] == '!':
                level[y] = level[y].replace('!', ' ', 1)
                enemy = EnemyPig(load_image('pigWalk.png'), 2, 1, x, y, level)
                hitbox = HitBox(x, y, 30, 55, 5, 5)
                lst.append(enemy)
                lst2.append(hitbox)
            elif level[y][x] in '><':
                if level[y][x] == '>':
                    enemy = EnemyBug(load_image('bug.png'), 5, 1, x, y, True)
                else:
                    enemy = EnemyBug(load_image('bug.png'), 5, 1, x, y, False)
                level[y] = level[y].replace(level[y][x], ' ', 1)
                hitbox = HitBox(x, y, 45, 30, 10, 15)
                lst3.append(enemy)
                lst4.append(hitbox)
    # вернем игрока, список врагов, и список хитбоксов врагов
    return new_player, lst, lst2, lst3, lst4


# screen — холст, на котором нужно рисовать
screen = pygame.display.set_mode((width, height))

# загрузка изображений кнопок
start_img_off = load_image('startBtnof.png')
exit_img_off = load_image('exitBtnof.png')
resume_img_off = load_image('resumeBtnof.png')
restart_img_off = load_image('restartBtnof.png')
next_img_off = load_image('nextBtnof.png')
exit2_img_off = load_image('exit2Btnof.png')
sound_img_off = load_image('sound_off.png')
music_img_off = load_image('music_off.png')

start_img_on = load_image('startBtnon.png')
exit_img_on = load_image('exitBtnon.png')
resume_img_on = load_image('resumeBtnon.png')
restart_img_on = load_image('restartBtnon.png')
next_img_on = load_image('nextBtnon.png')
exit2_img_on = load_image('exit2Btnon.png')
sound_img_on = load_image('sound_on.png')
music_img_on = load_image('music_on.png')
back_btn = load_image('backBtn.png')
info_game = load_image('info.png')

level1_img = load_image('1_level.png')
level1_s_img = load_image('1_level_s.png')
level2_img = load_image('2_level.png')
level2_s_img = load_image('2_level_s.png')
level3_img = load_image('3_level.png')
level3_s_img = load_image('3_level_s.png')
level4_img = load_image('4_level.png')
level4_s_img = load_image('4_level_s.png')
level5_img = load_image('5_level.png')
level5_s_img = load_image('5_level_s.png')

pause_img = load_image('pause.png')
loss_img = load_image('loss.png')
complete_img = load_image('complete.png')

bgb = load_image('background2.png')
bg = pygame.transform.scale(bgb, (1000, 700))
bgs = pygame.transform.scale(bgb, (1000, 700))

# загрузка заголовков игры
bunny_game1 = load_image('bunny-game1.png')
bunny_game2 = load_image('bunny-game2.png')
bunny_game3 = load_image('bunny-game3.png')


class Button:
    def __init__(self, x, y, image1, image2, scale):
        # инициализация и расположение кнопки
        width, height = image1.get_width(), image1.get_height()
        self.image = pygame.transform.scale(image1, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.imageon = pygame.transform.scale(image2, (int(width * scale), int(height * scale)))
        self.imageof = pygame.transform.scale(image1, (int(width * scale), int(height * scale)))
        self.clicked = False

    def draw(self):
        global sound, isclicked, begin_time
        # рисуем кнопку на экране
        action = False
        if isclicked is False:
            pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(pos):
                self.image = self.imageon
                if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                    if sound is True:
                        button_sound.play()
                    self.clicked = True
                    action = True
                    begin_time = time.time()
                    isclicked = True
            else:
                self.image = self.imageof
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
        else:
            if time.time() - begin_time > 0.5:
                isclicked = False
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

    def draw2(self):
        # рисуем кнопку на экране
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                action = True
                if self.image == self.imageon:
                    self.image = self.imageof
                else:
                    self.image = self.imageon
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


# функция для того чтобы сменить скин
def skin_bunny():
    global skin
    skin = (skin + 1) % 2


# функция из которой можно получить информацию
def get_info():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


# функция для вывода информации информации
def info():
    x1, x2 = 0, -1000

    clock = pygame.time.Clock()
    running = True
    while running:
        # окно будет отрисововаться до тех пор, пока пользователь не нажал на одну из кнопок
        screen.fill('lightblue')
        # отрисовка движения облаков
        screen.blit(bg, (x1, 0))
        screen.blit(bgs, (x2, 0))
        x1 += 1
        x2 += 1
        if x1 == 1000:
            x1 = 0
        if x2 == 0:
            x2 = -1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_menu()
        get_info()
        pygame.display.flip()
        clock.tick(FPS)


# создание кнопок
music_button = Button(550, 5, music_img_on, music_img_off, 0.6)
sound_button = Button(620, 0, sound_img_on, sound_img_off, 0.6)


def main_menu():
    global music, sound, skin
    pygame.display.set_caption('Bunny-game')
    pygame.display.set_icon(bunny_animations[skin]['stand'])
    # font = pygame.font.SysFont('freesansbold.ttf', 100)
    background_music1 = pygame.mixer.music.load('data/phone_music1.mp3')
    pygame.mixer.music.play()
    # Создание кнопок
    start_button = Button(80, 150, start_img_off, start_img_on, 1)
    exit_button = Button(80, 300, exit_img_off, exit_img_on, 1)
    skin_button = Button(10, 420, bunny_animations[skin]['stand'], bunny_animations[(skin + 1) % 2]['stand'], 1.4)
    info_button = Button(10, 5, info_game, info_game, 0.6)

    # выбор рандомной надписи
    bunny_game = random.choice([bunny_game1, bunny_game2, bunny_game3])
    x1, x2 = 0, -1000

    clock = pygame.time.Clock()
    running = True
    while running:
        # окно будет отрисововаться до тех пор, пока пользователь не нажал на одну из кнопок
        screen.fill('lightblue')
        # отрисовка движения облаков
        screen.blit(bg, (x1, 0))
        screen.blit(bgs, (x2, 0))
        x1 += 1
        x2 += 1
        if x1 == 1000:
            x1 = 0
        if x2 == 0:
            x2 = -1000
        if music is True:
            pygame.mixer.music.unpause()
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
        else:
            pygame.mixer.music.pause()

        # отрисовка окна и надписи
        pygame.display.set_icon(bunny_animations[skin]['stand'])
        screen.blit(bunny_game, (310, 90))
        # screen.blit(carrot, (500, 10))
        # text = font.render(open('data/carrot.txt').readline(), True, (0, 0, 0))
        # screen.blit(text, (560, 10))
        # эта часть в доработке

        # если пользователь нажал на кнопку 'play', то заканчивается цикл, и окно переходит в раздел уровней
        if start_button.draw() is True:
            running = False
        # если пользователь нажал на кнопку 'exit', то происходит завершение работы
        if exit_button.draw() is True:
            terminate()
        # включение и выключение звука
        if music_button.draw2() is True:
            music = not music
        if sound_button.draw2() is True:
            sound = not sound
        # если нажимаешь на кнопку менятся скин
        if skin_button.draw2() is True:
            skin_bunny()
        if info_button.draw2() is True:
            info()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        pygame.display.update()
        clock.tick(FPS)
    levels(x1, x2)


def levels(x1, x2):
    # Создание кнопок
    backbtn = Button(10, 430, back_btn, back_btn, 0.7)
    level1 = Button(20, 180, level1_img, level1_s_img, 1)
    level2 = Button(160, 180, level2_img, level2_s_img, 1)
    level3 = Button(300, 180, level3_img, level3_s_img, 1)
    level4 = Button(440, 180, level4_img, level4_s_img, 1)
    level5 = Button(580, 180, level5_img, level5_s_img, 1)
    file_name = ''
    clock = pygame.time.Clock()
    running = True
    while running:
        # окно будет отрисововаться до тех пор, пока пользователь не нажал на одну из кнопок
        screen.fill('lightblue')
        screen.blit(bg, (x1, 0))
        screen.blit(bgs, (x2, 0))
        x1 += 1
        x2 += 1
        if x1 == 1000:
            x1 = 0
        if x2 == 0:
            x2 = -1000
        # если пользователь нажал на кнопку '1', то заканчивается цикл, и окно переходит в игру
        if level1.draw() is True:
            file_name = 'map1.txt'
        if level2.draw() is True:
            file_name = 'map2.txt'
        if level3.draw() is True:
            file_name = 'map3.txt'
        if level4.draw() is True:
            file_name = 'map4.txt'
        if level5.draw() is True:
            pass
        if backbtn.draw() is True:
            main_menu()
        # если пользователь нажал на кнопку 'exit', то происходит завершение работы
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        if file_name:
            running = False
        pygame.display.update()
        clock.tick(FPS)

    game(file_name)


def game(name_file):
    global music, sound
    background_music2 = pygame.mixer.music.load('data/phone_music2.mp3')
    pygame.mixer.music.play()
    if music is False:
        pygame.mixer.music.pause()
    level = load_level(name_file)
    ending = ''
    start, timer, music1 = None, False, True

    # получение из функции generate_level игрока, список врагов
    player, lst_enemies_pigs, lst_hitboxes_pigs, lst_enemies_bugs, lst_hitboxes_bugs = generate_level(level)

    clock = pygame.time.Clock()
    camera = Camera()
    bg = BackGround(0, 0)
    FPS = 30
    running = True
    while running:
        if music is True and music1 is True:
            pygame.mixer.music.unpause()
            if not pygame.mixer.music.get_busy() and music1 is True:
                pygame.mixer.music.play()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                # если пользователь нажал клавишу space, то вызывается функция update в player
                if event.key == pygame.K_SPACE:
                    player.update(event)
                # если пользователь нажал на клавишу escape, то вызывается функция pause, если функция
                # возвращает 1, то цикл продолжается, 2 - цикл останавливается и игра начинается заново
                # 3 - цикл останавливается и вызывается функция main_menu, после которой открывается окно меню
                if event.key == pygame.K_ESCAPE:
                    player.set_pause()
                    p = pause()
                    if p == 1:
                        continue
                    if p == 2:
                        ending = 'restart'
                    if p == 3:
                        ending = 'exit'
        # отображаем спрайты на экране
        decor_group.draw(screen), finish_group.draw(screen), trampoline_group.draw(screen)
        all_sprites.draw(screen), enemy_group.draw(screen)
        hitbox_group.draw(screen), player_group.draw(screen)

        for i, hitbox in enumerate(lst_hitboxes_pigs):
            hitbox.update(lst_enemies_pigs[i].get_duration())

        # если пользователь проиграл или победил, то камера прекращает следить за персонажем
        if player.is_lose() is False and player.is_win() is False:
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
                bg.update(player)

        # если пользователь проиграл, создается таймер, по истечению которого цикл прекращается и вызывается
        # функция loss, открывается окно с заголовком loss
        if player.is_lose() is True:
            if timer is False:
                pygame.mixer.music.pause()
                music1 = False
                if music is True:
                    loss_sound.play()
                start = time.time()
                timer = True
            else:
                if time.time() - start > 1.5:
                    ending = 'loss'

        # если персонаж убивает кого-нибудь из врагов, то программа смотрит, кого убил игрок, и удаляет врага
        if player.is_kill() is True:
            if player.is_touch_pig():
                for i, enemy in enumerate(lst_enemies_pigs):
                    if enemy.is_touch():
                        player.do_minijump()
                        enemy.delete_enemy()
                        lst_hitboxes_pigs[i].delete_hitbox()
                        del lst_enemies_pigs[i]
                        del lst_hitboxes_pigs[i]
            if player.is_touch_bug():
                for i, enemy in enumerate(lst_enemies_bugs):
                    if enemy.is_touch():
                        player.do_minijump()
                        enemy.delete_enemy()
                        lst_hitboxes_bugs[i].delete_hitbox()
                        del lst_enemies_bugs[i]
                        del lst_hitboxes_bugs[i]

        # если пользователь победил, создается таймер, по истечению которого цикл прекращается и вызывается
        # функция win, открывается окно с заголовком celebrate
        if player.is_win() is True:
            if timer is False:
                pygame.mixer.music.pause()
                music1 = False
                if music is True:
                    win_sound.play()
                start = time.time()
                timer = True
            else:
                if time.time() - start > 1.7:
                    ending = 'win'

        # если ending больше не пустая строка то цикл прекращается
        if ending:
            running = False
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)

    # после окончания цикла все спрайты очищаются
    all_sprites.empty(), tiles_group.empty(), thorns_group.empty(), decor_group.empty()
    decor_group.empty(), finish_group.empty(), player_group.empty(), background_group.empty()
    enemy_group.empty(), hitbox_group.empty(), trampoline_group.empty()
    if ending == 'restart':
        game(name_file)
    elif ending == 'exit':
        main_menu()
    elif ending == 'loss':
        ls = loss()
        if ls == 1:
            game(name_file)
        elif ls == 2:
            main_menu()
    elif ending == 'win':
        wn = win()
        if wn == 1:
            game(name_file)
        elif wn == 2:
            main_menu()
        elif wn == 3:
            if int(name_file.split('.')[0][name_file.find('p') + 1:]) >= maps:
                main_menu()
            else:
                game(f"map{int(name_file.split('.')[0][name_file.find('p') + 1:]) + 1}.txt")


def pause():
    pygame.init()
    paused = True
    # Создание кнопок
    resume_button = Button(width // 2 - (324 // 2), 120, resume_img_off, resume_img_on, 1)
    restart_button = Button(width // 2 - (324 // 2), 235, restart_img_off, restart_img_on, 1)
    exit_button = Button(width // 2 - (324 // 2), 350, exit2_img_off, exit2_img_on, 1)

    clock = pygame.time.Clock()
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        # если пользователь нажал на кнопку resume, то цикл в функции game() прододжается
        if resume_button.draw() is True:
            return 1
        # если пользователь нажал на кнопку restart, то цикл в функции game() прекращается и опять вызывается
        if restart_button.draw() is True:
            return 2
        # если пользователь нажал на кнопку exit, то цикл в функции game() прекращается и вызывается функция
        # main_menu, и открывается окно меню
        if exit_button.draw() is True:
            return 3

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
        # если пользователь нажал на кнопку restart, то цикл в функции game() прекращается и опять вызывается
        if restart_button.draw() is True:
            return 1
        # если пользователь нажал на кнопку exit, то цикл в функции game() прекращается и вызывается функция
        # main_menu, и открывается окно меню
        if exit_button.draw() is True:
            return 2
        screen.blit(loss_img, (width // 2 - (320 // 2), 10))
        pygame.display.update()
        clock.tick(15)


def win():
    pygame.init()
    running = True
    next_button = Button(width // 2 - (324 // 2), 130, next_img_off, next_img_on, 1)
    restart_button = Button(width // 2 - (324 // 2), 245, restart_img_off, restart_img_on, 1)
    exit_button = Button(width // 2 - (324 // 2), 360, exit2_img_off, exit2_img_on, 1)
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        # если пользователь нажал на кнопку restart, то цикл в функции game() прекращается и опять вызывается
        if restart_button.draw() is True:
            return 1
        # если пользователь нажал на кнопку exit, то цикл в функции game() прекращается и вызывается функция
        # main_menu, и открывается окно меню
        if exit_button.draw() is True:
            return 2
        if next_button.draw() is True:
            return 3
        screen.blit(complete_img, (width // 2 - (400 // 2), 10))
        pygame.display.update()
        clock.tick(15)


if __name__ == '__main__':
    main_menu()