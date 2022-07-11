import pygame

from copy import deepcopy
from math import ceil

SCREEN_SIZE = 800

screen = pygame.display.set_mode((SCREEN_SIZE + 600, SCREEN_SIZE))
clock = pygame.time.Clock()
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

game_field = [
    [0, 2, 0, 2, 0, 2, 0, 2],
    [2, 0, 2, 0, 2, 0, 2, 0],
    [0, 2, 0, 2, 0, 2, 0, 2],
    [1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1],
    [3, 0, 3, 0, 3, 0, 3, 0],
    [0, 3, 0, 3, 0, 3, 0, 3],
    [3, 0, 3, 0, 3, 0, 3, 0],
]

lines_of_steps = []

future_killers = {}

kings = []

king_steps = []

last_steps = []

pygame.font.init()  # you have to call this at the start,
font1 = pygame.font.SysFont('Arial', 30)


def drawing_menu(screen):
    global font1
    pygame.draw.rect(screen, (255, 255, 255),
                     pygame.Rect((800, 0), (1400, 800)))
    # if you want to use this module.
    index = 0
    for text_element in (
            'Шашки', 'Правила:', '1. Ходить назад может только дамка', '2. Дамка не летающая',
            '3. Вы можете стать дамкой,',
            'достигнув конца поля', '4. Вы не обязаны делать кил', 'Последние ходы:'):
        textsurface = font1.render(text_element, True, (0, 0, 0))
        screen.blit(textsurface, (850, index))
        index += 50
    for text_element_ind in range(len(last_steps) - 1, -1, -1):
        textsurface = font1.render(last_steps[text_element_ind], True, (0, 0, 0))
        screen.blit(textsurface, (850, index))
        index += 50


def field_drawing(field_size, screen):
    global game_field, lines_of_steps
    screen.fill((255, 0, 0))
    ok = 0
    for i in range(field_size):
        for j in range(field_size):
            if (i + j) % 2 == 0:
                pygame.draw.rect(screen, (240, 218, 181),
                                 pygame.Rect((100 * j, 100 * i), ((100 * (j + 1)), (200 * (i + 1)))))
            else:
                pygame.draw.rect(screen, (181, 135, 99),
                                 pygame.Rect((100 * j, 100 * i), ((100 * (j + 1)), (200 * (i + 1)))))
            if game_field[i][j] == 2:
                if (i, j) not in kings:
                    pygame.draw.circle(screen, (0, 0, 0), (100 * j + 50, 100 * i + 50), 50, 0)
                    if i == 7:
                        kings.append((i, j))
                else:
                    pygame.draw.circle(screen, (60, 60, 60), (100 * j + 50, 100 * i + 50), 50, 0)
            elif game_field[i][j] == 3:
                if (i, j) not in kings:
                    pygame.draw.circle(screen, (255, 255, 255), (100 * j + 50, 100 * i + 50), 50, 0)
                    if i == 0:
                        kings.append((i, j))
                else:
                    pygame.draw.circle(screen, (166, 166, 166), (100 * j + 50, 100 * i + 50), 50, 0)

            elif game_field[i][j] == 4:
                pygame.draw.circle(screen, (245, 187, 0), (100 * j + 50, 100 * i + 50), 50, 0)
                ok = 1
    if ok:
        for line in lines_of_steps:
            pygame.draw.line(screen, (255, 78, 0), line[0], line[1], 5)
    else:
        lines_of_steps = []
    drawing_menu(screen)


def who_is_winner():
    global game_field
    player1, player2 = 0, 0
    for i in range(8):
        for j in range(8):
            if game_field[i][j] == 2:
                player1 += 1
            elif game_field[i][j] == 3:
                player2 += 1
    if not player1:
        print('Белые победили!')
        return
    if not player2:
        print('Черные победили!')
        return


# Chess by Andrey Tsvetkov
# github.com/int-64

def color_correct(x, y, color):
    global game_field
    if game_field[x][y] == 2 and color == 'blue':
        return True
    elif game_field[x][y] == 3 and color == 'red':
        return True
    return False


def move_correct(before, after, move):
    global game_field

    y1, x1 = before
    y2, x2 = after
    if color_correct(y1, x1, move):
        pass
    else:
        return False

    for i in (x1, x2, y1, y2):
        if 0 <= i < 8:
            pass
        else:
            return False

    if future_killers.get((y2, x2)):
        return True

    if (y1, x1) in kings and (y2, x2) in king_steps:
        return True

    if move == 'blue':  # проверяем корректность хода для синих (черных) пешек
        to_kill = x2 - 1
        if x1 == x2 + 2:
            to_kill = x2 + 1
        if y1 == y2 - 2 and (x1 == x2 - 2 or x1 == x2 + 2) and game_field[y2 - 1][to_kill] == 3:
            game_field[y2 - 1][to_kill] = (y2 - 1 + to_kill) % 2
            return True
        if y1 >= y2:
            return False
        if y2 == y1 + 1:
            pass
        else:
            return False
        if x2 == x1 - 1 or x2 == x1 + 1:
            pass
        else:
            return False
    else:  # проверяем корректность хода для красных (белых) пешек
        to_kill = x2 - 1
        if x1 == x2 + 2:
            to_kill = x2 + 1
        can_kill = 1
        for i in (y2 + 2, y2 + 1, to_kill):
            if 0 <= i < 8:
                pass
            else:
                can_kill = 0
                break
        if can_kill and y1 == y2 + 2 and (x1 == x2 - 2 or x1 == x2 + 2) and game_field[y2 + 1][to_kill] == 2:
            game_field[y2 + 1][to_kill] = (y2 + 1 + to_kill) % 2
            return True
        if y1 <= y2:
            return False
        if y2 == y1 - 1:
            pass
        else:
            return False
        if x2 == x1 - 1 or x2 == x1 + 1:
            pass
        else:
            return False
    return True


def change_move():  # просто меняем ход для другого языка
    global move

    player_1 = 'red'
    player_2 = 'blue'
    if move == player_1:
        move = player_2
    else:
        move = player_1


def backlight_king(x, y, move):  # генерируем ходы для дамки
    print(f'Обнаружен новый король! {x, y}')
    i, j = x + 1, y + 1
    while 0 <= i < 8 and 0 <= j < 8 and game_field[i][j] == 1:
        king_steps.append((i, j))
        game_field[i][j] = 4
        i += 1
        j += 1
        if 0 <= i < 8 and 0 <= j < 8 and game_field[i][j] != 1:
            break
    i, j = x - 1, y + 1
    while 0 <= i < 8 and 0 <= j < 8 and game_field[i][j] == 1:
        king_steps.append((i, j))
        game_field[i][j] = 4
        i -= 1
        j += 1
        if 0 <= i < 8 and 0 <= j < 8 and game_field[i][j] != 1:
            break
    i, j = x + 1, y - 1
    while 0 <= i < 8 and 0 <= j < 8 and game_field[i][j] == 1:
        king_steps.append((i, j))
        game_field[i][j] = 4
        i += 1
        j -= 1
        if 0 <= i < 8 and 0 <= j < 8 and game_field[i][j] != 1:
            break
    i, j = x - 1, y - 1
    while 0 <= i < 8 and 0 <= j < 8 and game_field[i][j] == 1:
        king_steps.append((i, j))
        game_field[i][j] = 4
        i -= 1
        j -= 1
        if 0 <= i < 8 and 0 <= j < 8 and game_field[i][j] != 1:
            break


def backlight(x, y, move, immune=False):  # генерируем ходы и возможности убить чужую пешку
    global game_field

    coordinates = []
    x_rel = x + 1
    x_rel_kill = x + 2
    x_rel2 = x - 1
    x_rel2_kill = x - 2
    if move == 'red' or immune:
        x_rel = x - 1
        x_rel_kill = x - 2
        x_rel2 = x + 1
        x_rel2_kill = x + 2
    if 0 <= x_rel < 8:
        pass
    else:
        if (x, y) in kings:  # в любом случае для дамки (короля) ищем ходы
            print('Начинаю цикл поиска ходов для короля...')
            if move == 'red':
                backlight_king(x, y, 'red')
            else:
                backlight_king(x, y, 'blue')
        else:
            print('Проекция ходов невозможна: 1')
            return

    for y_rel in (y - 1, y + 1):
        if 0 <= y_rel < 8:
            if 0 <= x_rel < 8:
                if game_field[x_rel][y_rel] not in (2, 3):
                    coordinates.append((x_rel, y_rel))
                elif game_field[x_rel][y_rel] != game_field[x][y]:
                    nxt = y_rel
                    if y_rel < y:
                        nxt -= 1
                    else:
                        nxt += 1
                    if 0 <= nxt < 8 and 0 <= x_rel_kill < 8:
                        if game_field[x_rel_kill][nxt] not in (2, 3):
                            path_finder(game_field, x_rel_kill, nxt, move, game_field[x_rel][y_rel], None,
                                        (x_rel, y_rel),
                                        [(x_rel, y_rel)])
                            coordinates.append((x_rel_kill, nxt))
            if 0 <= x_rel2 < 8:
                if game_field[x_rel2][y_rel] not in (game_field[x][y], 1):
                    nxt = y_rel
                    if y_rel < y:
                        nxt -= 1
                    else:
                        nxt += 1

                    if 0 <= nxt < 8 and 0 <= x_rel2_kill < 8:
                        if game_field[x_rel2_kill][nxt] not in (2, 3):
                            path_finder(game_field, x_rel2_kill, nxt, move, game_field[x_rel2][y_rel], None,
                                        (x_rel2, y_rel),
                                        [(x_rel2, y_rel)])
                            coordinates.append((x_rel2_kill, nxt))
            # проверка на "убийство" шашки
        else:
            continue
    if (x, y) in kings and not immune:  # для дамки (короля) ищем ходы
        print('Начинаю цикл поиска ходов для короля...')
        if move == 'red':
            backlight_king(x, y, 'blue')
        else:
            backlight_king(x, y, 'red')

    for coordinate in coordinates:  # отмечаем координаты
        xc, yc = coordinate
        game_field[xc][yc] = 4


def remove_backlight():
    global game_field

    for i in range(len(game_field)):
        for j in range(len(game_field[0])):
            if game_field[i][j] == 4:
                game_field[i][j] = (i + j) % 2


def path_finder(gm, x, y, move, last, direction, last_coords, last_path):
    gm = deepcopy(gm)

    change_to_green = 0
    zn = gm[x][y]

    was_move = 0
    can_switch = 0

    zn_z = 3
    if move == 'blue':
        zn_z = 2
    print(x, y, last, last_coords, zn, zn_z, move, was_move)

    if last == zn or (last == 4 and zn == 1) or (last == 1 and zn == 4):
        if lines_of_steps and (zn != 1):
            lines_of_steps.pop(-1)

        print('Помер')
        return
    can_cont = 0
    if zn == 1 or zn == 4:
        if future_killers.get((x, y)):
            if len(future_killers[(x, y)]) < len(last_path):
                can_switch = 1
        else:
            can_switch = 1
        if can_switch:
            future_killers[(x, y)] = last_path
            lines_of_steps.append(((100 * last_coords[1] + 50, 100 * last_coords[0] + 50),
                                   (100 * y + 50, 100 * x + 50)))
        if zn == 1:
            print(f'ПОменяем потом {x, y}')
            change_to_green = 1
        can_cont = 1

    if zn != 1 and zn != 4:
        if move == 'red' and zn != 3:
            lines_of_steps.append(((100 * last_coords[1] + 50, 100 * last_coords[0] + 50),
                                   (100 * y + 50, 100 * x + 50)))
            last_path.append((x, y))

        if move == 'blue' and zn != 2:
            lines_of_steps.append(((100 * last_coords[1] + 50, 100 * last_coords[0] + 50),
                                   (100 * y + 50, 100 * x + 50)))
            last_path.append((x, y))

    if move == 'red':
        if zn == 3:
            print('Сдох')
            if last != 1 and lines_of_steps:
                lines_of_steps.pop(-1)
            return
        if 0 <= x - 1 < 8:
            if 0 <= y - 1 < 8 and (can_cont or direction == 1) and direction != 4:
                path_finder(gm, x - 1, y - 1, move, gm[x][y], 1, (x, y), last_path[:])
                print("Dvig1")
                was_move = 1
            if 0 <= y + 1 < 8 and (can_cont or direction == 2) and direction != 3:
                path_finder(gm, x - 1, y + 1, move, gm[x][y], 2, (x, y), last_path[:])
                print("Dvig2")
                was_move = 1
        if 0 <= x + 1 < 8:
            if 0 <= y - 1 < 8 and (can_cont or direction == 3) and direction != 2:
                path_finder(gm, x + 1, y - 1, move, gm[x][y], 3, (x, y), last_path[:])
                print("Dvig3")
                was_move = 1
            if 0 <= y + 1 < 8 and (can_cont or direction == 4) and direction != 1:
                path_finder(gm, x + 1, y + 1, move, gm[x][y], 4, (x, y), last_path[:])
                print("Dvig4")
                was_move = 1
    else:
        if zn == 2:
            return
        if 0 <= x - 1 < 8:
            if 0 <= y - 1 < 8 and (can_cont or direction == 1) and direction != 4:
                path_finder(gm, x - 1, y - 1, move, gm[x][y], 1, (x, y), last_path[:])
                was_move = 1
            if 0 <= y + 1 < 8 and (can_cont or direction == 2) and direction != 3:
                path_finder(gm, x - 1, y + 1, move, gm[x][y], 2, (x, y), last_path[:])
                was_move = 1
        if 0 <= x + 1 < 8:
            if 0 <= y - 1 < 8 and (can_cont or direction == 3) and direction != 2:
                path_finder(gm, x + 1, y - 1, move, gm[x][y], 3, (x, y), last_path[:])
                was_move = 1
            if 0 <= y + 1 < 8 and (can_cont or direction == 4) and direction != 1:
                path_finder(gm, x + 1, y + 1, move, gm[x][y], 4, (x, y), last_path[:])
                was_move = 1

    if (zn == zn_z) and last != 1:
        if lines_of_steps:
            lines_of_steps.pop(-1)
        if lines_of_steps:
            lines_of_steps.pop(-1)
    elif not was_move and last != zn_z:
        if lines_of_steps:
            lines_of_steps.pop(-1)

    if change_to_green:
        game_field[x][y] = 4
    # pygame.display.flip()


hold_left = False
last_pressed_coords = (0, 0)
move = 'blue'

while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print('Выход')
            quit()

        click = pygame.mouse.get_pressed()

        if click[0] and not hold_left:  # зажатие на пешук
            future_killers = {}
            coordinates = pygame.mouse.get_pos()
            x, y = ceil(coordinates[1] / 100) - 1, ceil(coordinates[0] / 100) - 1
            last_pressed_coords = (x, y)
            if color_correct(x, y, move):
                if (x, y) in kings:
                    print('Запускаю цикл для короля...', move)
                    if move == 'blue':
                        backlight(x, y, "blue")
                        backlight(x, y, "blue", immune=True)
                    else:
                        backlight(x, y, "red")
                        backlight(x, y, "red", immune=True)
                else:
                    backlight(x, y, move)
                print('Проверку цвета прошло')
            else:
                print("Ошибка")
            hold_left = True

        if hold_left and not click[0]:  # отжатие мешыки от пешки
            remove_backlight()
            coordinates = pygame.mouse.get_pos()
            x0, y0 = last_pressed_coords[0], last_pressed_coords[1]
            x, y = ceil(coordinates[1] / 100) - 1, ceil(coordinates[0] / 100) - 1
            if game_field[x][y] not in (2, 3):
                pressed_coords = (x, y)
                if move_correct(last_pressed_coords, pressed_coords, move):
                    if future_killers.get((x, y)):
                        for coordinated2 in future_killers[(x, y)]:
                            x2, y2 = coordinated2
                            print(f'Съедена шашка на координате {x2, y2}')
                            if move == 'red' and x2 == 1:
                                print("На поле появляется новый король")
                                kings.append((x, y))
                            elif move == 'blue' and x2 == 6:
                                print("На поле появляется новый король")
                                kings.append((x, y))
                            if (x2, y2) in kings:
                                kings.remove((x2, y2))
                            game_field[x2][y2] = 1
                    if (x0, y0) in kings:
                        kings.remove((x0, y0))
                        kings.append((x, y))
                    game_field[x][y], game_field[x0][y0] = game_field[x0][y0], game_field[x][y]
                    last_steps.append(f'{8 - x0}{chr(ord("A") + y0)} => {8 - x}{chr(ord("A") + y)}')
                    if len(last_steps) > 8:
                        last_steps.pop(0)
                    print("Съел, прошел ход", move)

                    change_move()
            hold_left = False
    screen.fill((55, 55, 0))
    field_drawing(8, screen)
    who_is_winner()
    pygame.display.update()  # Or pygame.display.flip()
