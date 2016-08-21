# -*- coding: utf-8 -*-
"""
    Arbalet - ARduino-BAsed LEd Table
    Font - Arbalet font for text rendering

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from pygame.font import get_default_font, match_font, init as pygame_init, Font as pygame_Font
from pygame import Color
from struct import unpack
from numpy import array, rot90

__all__ = ['Arbatext']

class RenderedText(object):
    """
    This class represents a text rendered for specific resolution and orientation
    """
    def __init__(self, text):
        self.rendered = text

class Font(object):
    MAX_SIZE = 100

    def __init__(self, height, width, vertical=False, font=None):
        pygame_init()
        self.vertical = vertical
        self.height = height
        self.width = width

        if font is None:
            font = get_default_font()
        else:
            font_file = match_font(font)
            if font_file is None:
                raise ValueError("pygame cannot find any file for the selected font {}".format(font))
            else:
                font = font_file

        if vertical:
            self._size = self._get_ideal_font_size(height, width, font)
        else:
            self._size = self._get_ideal_font_size(width, height, font)

        if self._size==0:
            raise ValueError("The selected font {} cannot be rendered in any size".format(font))
        self._font = pygame_Font(font, self._size)
        #print("Font {} of size {}".format(font, self._size))

    def _get_ideal_font_size(self, height, width, font):
        """
        Return the ideal size of text (<MAX_SIZE) so that it fits the desired (height, width)
        :param height:
        :param width:
        :param font:
        :return:
        """
        ideal_size = 0
        for i in range(1, self.MAX_SIZE):
            if pygame_Font(font, i).get_height()<=height:
                ideal_size = i
            else:
                break
        return ideal_size

    def _render_flat(self, text):
        #  # TODO non-py2
        raw_text = self._font.render(text, False, Color('black')).get_buffer().raw
        return unpack('@{}?'.format(len(raw_text)), raw_text)

    def render(self, text):
        flat_mat = self._render_flat(text)

        matrix = []
        for h in range(0, len(flat_mat), len(flat_mat)//(self.height if self.vertical else self.width)):
            matrix.append(flat_mat[h:h+len(flat_mat)//(self.height if self.vertical else self.width)])

        matrix = array(matrix)
        return RenderedText(matrix if self.vertical else rot90(matrix))


