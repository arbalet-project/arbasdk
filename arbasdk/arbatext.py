# -*- coding: utf-8 -*-
"""
    Arbalet - ARduino-BAsed LEd Table
    Arbatext - Arbalet text representation

    Represents a sequel of Unicode characters to be displayed onto Arbalet

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from pygame.font import Font, get_default_font, init as pygame_init
from pygame import Color
from struct import unpack

__all__ = ['Arbatext']

class Arbatext(object):
    MAX_SIZE = 100

    def __init__(self, height, width, vertical=False, font=None, scrolling=True):
        pygame_init()
        self._vertical = vertical
        self.height = height
        self.width = width

        if font is None:
            font = get_default_font()

        if vertical:
            self._size = self.get_ideal_font_size(height, width, font)
        else:
            self._size = self.get_ideal_font_size(width, height, font)

        if self._size==0:
            raise ValueError("The selected font {} cannot be rendered in any size".format(font))
        self._font = Font(font, self._size)
        print "Font {} of size {}".format(font, self._size)

    def get_ideal_font_size(self, height, width, font):
        """
        Return the ideal size of text (<MAX_SIZE) so that it fits the desired (height, width)
        :param height:
        :param width:
        :param font:
        :return:
        """
        ideal_size = 0
        for i in range(1, self.MAX_SIZE):
            if Font(font, i).get_height()<=height:
                ideal_size = i
            else:
                break
        return ideal_size

    def render_flat(self, text):
        def to_bool(character):
            return unpack('@?', character)[0]

        return map(to_bool, self._font.render(text, False, Color('black')).get_buffer().raw)

    def render(self, text):
        flat_mat = self.render_flat(text)

        matrix = []
        for h in range(0, len(flat_mat), len(flat_mat)/self.height):
            matrix.append(flat_mat[h:h+len(flat_mat)/self.height])

        return matrix

    def print_mat(self, text):
        flat_mat = self.render_flat(text.decode('utf-8'))
        index = 0
        for h in range(0, len(flat_mat), len(flat_mat)/self.height):
            for w in range(len(flat_mat)/self.height):
                #print w+(len(flat_mat)/self.height)*h
                if flat_mat[index]:
                    print '■',
                else:
                    print ' ',
                index += 1
            print '|'

if __name__=='__main__':
    Arbatext(15, 10, True).print_mat('#8€')