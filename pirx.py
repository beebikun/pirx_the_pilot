#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import sys
import os

clear_console = 'clear' if os.name == 'posix' else 'CLS'

MAP_VALUES = {'0': 'red', '1': 'green', '2': 'yellow', '3': 'blue',
              '4': 'magenta', '5': 'cyan', '6': 'white', '7': 'crimson',
              '8': 'black', '9': 'red', 'A': 'green', 'B': 'black',
              'C': 'blue', 'D': 'magenta', 'E': 'cyan', 'F': 'gray'}
WIDTH = 9

COLORS = dict(
    gray=('\033[1;30m', '\033[1;m'),
    red=('\033[1;31m', '\033[1;m'),
    green=('\033[1;32m', '\033[1;m'),
    yellow=('\033[1;33m', '\033[1;m'),
    blue=('\033[1;34m', '\033[1;m'),
    magenta=('\033[1;35m', '\033[1;m'),
    cyan=('\033[1;36m', '\033[1;m'),
    white=('\033[1;37m', '\033[1;m'),
    crimson=('\033[1;38m', '\033[1;m'),
    black=('', ''),
    highlighted_red=('\033[1;41m', '\033[1;m'),
    highlighted_green=('\033[1;42m', '\033[1;m'),
    highlighted_brown=('\033[1;43m', '\033[1;m'),
    highlighted_blue=('\033[1;44m', '\033[1;m'),
    highlighted_magenta=('\033[1;45m', '\033[1;m'),
    highlighted_cyan=('\033[1;46m', '\033[1;m'),
    highlighted_gray=('\033[1;47m', '\033[1;m'),
    highlighted_crimson=('\033[1;48m', '\033[1;m')
)


def colorize(clr, s):
    color = COLORS[clr]
    return color[0] + str(s) + color[1]


def colorize_row(array):
    def _check_value(x):
        if not x:
            return ' '
        if isinstance(x, tuple):
            return colorize(*x)
        return colorize(MAP_VALUES[x], x)
    return ''.join([_check_value(x) for x in array])


list_diffs = lambda pos, dif: [a+b for a, b in zip(pos, dif)]


class Game(object):
    CONTROL = dict(
        q='move_rup',
        w='move_up',
        e='move_lup',
        a='move_r',
        d='move_l',
        z='move_ldn',
        x='move_dn',
        c='move_rdn',
        s='answer',
        p='exit',
    )

    IS_RUN = True
    GUESS = False
    INTERVAL = ' '*10

    def __init__(self, w, start=None, end=None):
        self.w = w
        if start is None:
            start = 0
        if end is None:
            end = len(MAP_VALUES)
        #значения, из которых будет генериться карта
        values = MAP_VALUES.keys()[start: end]
        #карта космоса, space - {0: [x, x, ...], 1: [...], ...}
        self.space = self._generate(values)
        #выбираем случайные координаты, в которых находится Пиркс,
        self._update_pos(
            [random.randint(1, WIDTH-1), random.randint(1, WIDTH-1)])
        #но он знает только значение  клетки, а не координаты
        self.pirx = PirxThePilot(self._get_value())
        self.redraw_sreen()
        self.next_step()

    def _generate(self, values):
        """Генерим w рядов по w клеток (столбцов)
        Аргументы:
            value - список значений, из которых будет генериться карта
        Возвращаем словарь: ключи - номера рядов, значение - содержимое ряда.
        """
        generate_row = lambda: [random.choice(values) for i in xrange(self.w)]
        return dict([(i, generate_row()) for i in xrange(self.w)])

    def _get_space_screen(self):
        #массив из строк карты космоса
        clmn_numbers = ' ' + ''.join([str(i+1) for i in xrange(self.w)])
        space = [colorize('gray', clmn_numbers)] + \
            [colorize('gray', row_num+1) + colorize_row(row)
             for row_num, row in self.space.iteritems()]
        return space

    def _get_value(self):
        #значение текущей позиции Пиркса
        x = self._pos[0]
        y = self._pos[1]
        return self.space[y-1][x-1]

    def _update_pos(self, value):
        """self._pos - координаты клетки, в которой находится Пиркс
        Так как карта цикличная, а перемещается Пиркс только на клетку за раз -
        если вылезли за пределы карты - переносимся на другую сторону карты.
        """
        self._pos = value
        for i, p in enumerate(self._pos):
            if p > self.w:
                self._pos[i] = 1
            if p < 1:
                self._pos[i] = self.w-1

    def redraw_sreen(self):
        #перерисовка экрана
        os.system(clear_console)
        space = self._get_space_screen()
        space_len = len(space)
        empty_str = ' ' * self.w
        pirx_map = self.pirx.get_known_boxes_screen()
        pirx_len = len(pirx_map)
        for i in xrange(max(space_len, pirx_len)):
            print("%s%s%s" % (space[i] if i < space_len else empty_str,
                              self.INTERVAL,
                              pirx_map[i] if i < pirx_len else ''))

    def pirx_move(self, direction=None):
        if direction is None:
            direction = 'next_step'
        dif = getattr(self.pirx, direction)()
        self._update_pos(list_diffs(self._pos, dif))
        self.pirx.update_known_boxes(self._get_value())

    def answer(self):
        def _get_pos(name):
            try:
                return int(
                    raw_input('Enter your guess for %s position: ' % name))
            except ValueError:
                print('Please, enter a number')
            return
        x = None
        y = None
        while not x:
            x = _get_pos('x')
        while not y:
            y = _get_pos('y')
        if [x, y] == self._pos:
            print 'You are win!'
            self.IS_RUN = False
        else:
            self.GUESS = (x, y)

    def exit(self):
        sys.exit()

    def next_step(self):
        if self.GUESS:
            print('Sorry, your guess %s is wrong. Try again!' % str(
                self.GUESS))
            self.GUESS = False
        clrz = lambda name: colorize(
            self.pirx.COLORS[name], self.pirx.COLORS[name])
        print
        print('%s - Pirx\'s start box' % clrz('start'))
        print('%s - Pirx\'s current box' % clrz('cur'))
        print('qweadzxc - for moving; s - give an answer; p - quit;')

        def _get_direction():
            key = raw_input('Where to move, dude?:')
            return self.CONTROL.get(key)

        direction = None
        while not direction:
            direction = _get_direction()

        if direction == 'exit':
            self.IS_RUN = False
        elif direction == 'answer':
            self.answer()
        else:
            self.pirx_move(direction)

        if self.IS_RUN:
            self.redraw_sreen()
            self.next_step()
        else:
            self.exit()


class PirxThePilot(object):
    OPTIONS = dict(
        lup=(1, -1),      # left up
        up=(0, -1),       # up
        rup=(-1, -1),     # right up
        l=(1, 0),         # left
        r=(-1, 0),        # right
        ldn=(-1, 1),      # left down
        dn=(0, 1),        # right down
        rdn=(1, 1),       # down
    )

    COLORS = dict(
        start='highlighted_red',
        cur='highlighted_green'
    )

    def __init__(self, start_box):
        #позиция - текущая позиция пиркса относительно точки старта
        self._pos = (0, 0)
        #массив всех пройденных клеток
        self.known_boxes = {self._pos: start_box}

    def _dif_pos(self, dif):
        return list_diffs(self._pos, dif)

    def update_known_boxes(self, value):
        self.known_boxes[self._pos] = value

    def get_known_boxes_screen(self):
        #возвращает массив из рядов карты, как ее видит Пиркс
        def _get_box(x, y):
            box = self.known_boxes.get((x, y))
            if x == 0 and y == 0:
                box = (self.COLORS['start'], box)
            elif (x, y) == self._pos:
                box = (self.COLORS['cur'], box)
            else:
                pass
            return box

        def _get_row(y):
            return colorize_row(
                [_get_box(x, y) for x in xrange(min_x, max_x+1)])

        min_x = min(self.known_boxes)[0]
        min_y = min(self.known_boxes, key=lambda pos: pos[1])[1]
        max_x = max(self.known_boxes)[0]
        max_y = max(self.known_boxes, key=lambda pos: pos[1])[1]
        return [' '] + \
            [_get_row(y) for y in xrange(min_y, max_y+1)]

    def _move(self, dif):
        self._pos = tuple(self._dif_pos(dif))
        return dif

    def move_rup(self):
        dif = self.OPTIONS['rup']
        return self._move(dif)

    def move_up(self):
        dif = self.OPTIONS['up']
        return self._move(dif)

    def move_lup(self):
        dif = self.OPTIONS['lup']
        return self._move(dif)

    def move_r(self):
        dif = self.OPTIONS['r']
        return self._move(dif)

    def move_l(self):
        dif = self.OPTIONS['l']
        return self._move(dif)

    def move_rdn(self):
        dif = self.OPTIONS['rdn']
        return self._move(dif)

    def move_dn(self):
        dif = self.OPTIONS['dn']
        return self._move(dif)
        return dif

    def move_ldn(self):
        dif = self.OPTIONS['ldn']
        return self._move(dif)
        return dif


Game(WIDTH)
