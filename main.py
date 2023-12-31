# Copyright 2023 - 2024 Ars_Mond
# License AGPL-3.0

import os
import sys
import time
import random as r
from enum import Enum
from ctypes import *

STD_OUTPUT_HANDLE = -11

class COORD(Structure):
    pass


COORD._fields_ = [("X", c_short), ("Y", c_short)]

class Color(Enum):
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'


class CharVector2:
    x: int = 0
    y: int = 0
    __char: str = ''
    __color: Color = Color.RESET
    __clear_color: Color = Color.RESET

    @property
    def char(self):
        return self.__color.value + self.__char + self.__clear_color.value

    @char.setter
    def char(self, value):
        if isinstance(value, str):
            self.__char = value
        else:
            raise ValueError("The name should be a string!")


    def __init__(self, x: int, y: int, char: str, color: Color = Color.RESET):
        self.x = x
        self.y = y
        self.__char = char
        self.__char_prime = char
        self.__color = color

    def get_list(self):
        return [self.x, self.y, self.__char]

    def get_vector(self):
        return [self.x, self.y]

    def set_color(self, color: Color):
        self.__color = color
        return self.char

    def clear_color(self):
        self.__color = self.__clear_color
        return self.char

    def __add__(self, other):
        if isinstance(other, CharVector2):
            return CharVector2(self.x + other.x, self.y + other.y, self.__char, self.__color)
        elif isinstance(other, list):
            return CharVector2(self.x + other[0], self.y + other[1], self.__char, self.__color)
        else:
            raise TypeError()

    def __sub__(self, other):
        if isinstance(other, CharVector2):
            return CharVector2(self.x - other.x, self.y - other.y, self.__char, self.__color)
        elif isinstance(other, list):
            return CharVector2(self.x - other[0], self.y - other[1], self.__char, self.__color)
        else:
            raise TypeError()

    def __str__(self):
        return str(self.get_list())

    def __repr__(self):
        return str(self.get_list())

    def __copy__(self):
        return CharVector2(self.x, self.y, self.__char, self.__color)


def print_at(x: int, y: int, s: str, size: list | tuple = None, *, lang: str = 'ru'):
    x = int(x)
    y = int(y)
    if sys.platform == 'win32':
        if size is not None:
            x = x % size[0]
            y = y % size[1]

        h = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        coord = COORD(c_short(x), c_short(y))
        windll.kernel32.SetConsoleCursorPosition(h, coord)

        c = None
        if lang == 'ru':
            c = s.encode("cp866", errors="ignore")
        else:
            c = s.encode("cp1252", errors="ignore")

        windll.kernel32.WriteConsoleA(h, c_char_p(c), len(c), None, None)
    else:
        print('This system is not win32 / win64')

def get_size_console():
    if sys.platform == 'win32':
        h = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            import struct
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            size_x = right - left + 1
            size_y = bottom - top + 1
        else:
            size_x = 90
            size_y = 60
        return size_x, size_y

    else:
        print('This system is not win32 / win64')

def print_clear_area(size_area: list[int, int], *, char: str = ' ', sleep: int = 0):
    if sys.platform == 'win32':
        for i in range(size_area[1]):
            if sleep > 0:
                time.sleep(sleep)
            for j in range(size_area[0]):
                print_at(j, i, char)


def tree(count: int = 7, *, center_char: str = '*', slash_char: str = '/', alt_slash_char: str = '\\', fill_char: str = '0', tree_char: str = '-', offset: list[int, int] = None):
    if count % 2 == 0:
        count += 1


    out: str = ''
    # tree_list: list[int, int, str] = []
    tree_list: list[CharVector2] = []

    out_tree: list[CharVector2] = []
    fill_tree: list[CharVector2] = []
    doo_tree: list[CharVector2] = []

    out_tree.append(CharVector2(count + 1, 0, center_char, Color.YELLOW))

    for i in range(1, count):
        out_tree.append(CharVector2(count - i + 1, i, slash_char))
        out_tree.append(CharVector2(count + i + 1, i, alt_slash_char))

    for i in range(1, count):
        for j in range(2 * (i - 1) + 1):
            fill_tree.append(CharVector2(count + 1 - (i - 1) + j, i, fill_char))

    for i in range(int(count / 3)):
        doo_tree.append(CharVector2(count - 1, i + count, '|'))
        doo_tree.append(CharVector2(count, i + count, tree_char))
        doo_tree.append(CharVector2(count + 1, i + count, tree_char))
        doo_tree.append(CharVector2(count + 2, i + count, tree_char))
        doo_tree.append(CharVector2(count + 3, i + count, '|'))

    tree_list.extend(out_tree)
    tree_list.extend(fill_tree)
    tree_list.extend(doo_tree)

    if offset is not None:
        for i in range(len(tree_list)):
            tree_list[i] += offset

        for i in range(len(out_tree)):
            out_tree[i] += offset

        for i in range(len(fill_tree)):
            fill_tree[i] += offset

        for i in range(len(doo_tree)):
            doo_tree[i] += offset

    return tree_list, out_tree, fill_tree, doo_tree, doo_tree[-1].y


def random_color():
    c = r.randint(1, 6)

    if c == 1:
        return Color.RED
    elif c == 2:
        return Color.GREEN
    elif c == 3:
        return Color.YELLOW
    elif c == 4:
        return Color.BLUE
    elif c == 5:
        return Color.MAGENTA
    elif c == 6:
        return Color.CYAN


def set_color_str(s: str, color: Color):
    return color.value + s + Color.RESET.value



if __name__ == '__main__':
    os.system('cls')

    size = get_size_console()
    print(size)

    time.sleep(0.1)
    print_clear_area(size, char=set_color_str('#', Color.MAGENTA))
    time.sleep(1)
    print_clear_area(size, char=set_color_str('%', Color.CYAN), sleep=0.05)

    count = 15
    offset = [int(size[0]/2) - count, 5]

    out = tree(count, offset=offset)
    fill_tree = out[2]

    print(out)

    time.sleep(0.2)
    os.system('cls')
    print_clear_area(size)

    g = 0
    for l in out[1]:
        if l.y > g:
            g = l.y
            time.sleep(0.1)

        print_at(l.x, l.y, l.char)

    g = 0
    for l in out[2]:
        l.set_color(Color.GREEN)

        if l.y > g:
            g = l.y
            time.sleep(0.1)

        print_at(l.x, l.y, l.char)

    g = 0
    for l in out[3]:
        if l.y > g:
            g = l.y
            time.sleep(0.1)

        print_at(l.x, l.y, l.char)

    new_year_text = 'С новым годом!'
    print_at(count + offset[0] - (len(new_year_text) / 2 - 2), out[4] + 2, set_color_str(new_year_text, Color.CYAN), size)

    for i in range(20):

        for l in fill_tree:
            l.set_color(Color.GREEN)
            l.char = '0'

        for l in fill_tree:
            n: int = r.randint(0, 100)

            if n > 20:
                continue

            l.set_color(random_color())
            l.char = '*'


        for l in fill_tree:
            print_at(l.x, l.y, l.char)

        time.sleep(0.5)



    print_at(size[0]-1, size[1]-2, ' ')
