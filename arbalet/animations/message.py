"""
    Arbalet - ARduino-BAsed LEd Table
    text writing on LEDs

    Copyright 2017 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import numpy as np
from ..config import ConfigReader
from ..tools import Rate
from pygame.font import get_default_font, match_font, init as pygame_init, Font as pygame_Font
from pygame import Color
from struct import unpack
from numpy import array, rot90

__all__ = ['Message']


class Message(object):
    def __init__(self, model):
        self.model = model

        config_reader = ConfigReader()
        self.font_config = config_reader.font
        self.hardware_config = config_reader.hardware
        self.set_font(self.font_config['font'], self.font_config['vertical'])


    def set_font(self, font=None, vertical=True):
        """
        Instantiate the selected (or the default) font to write on this model
        :param font: Font name (list: pygame.font.get_fonts()
        :param vertical: True if the text must be displayed in portrait mode, false for landscape mode
        """
        self.font = Font(self.hardware_config['height'], self.hardware_config['width'], vertical, font)


    def write(self, text, foreground, background='black', speed=10):
        """
        Blocking call writing text to the model until scrolling is complete
        :param text: an UTF-8 string representing the text to display
        :param foreground: foreground color
        :param background: background color
        :param speed: frequency of update (Hertz)
        """
        if self.font is None:
            self.set_font()

        rendered = self.font.render(text)
        rate = Rate(speed)
        if self.font.vertical:
            scrolling_range = range(len(rendered.rendered[0]))
        else:
            scrolling_range = range(len(rendered.rendered), 0, -1)

        for start in scrolling_range:
            with self.model:
                for h in range(self.hardware_config['height']):
                    for w in range(self.hardware_config['width']):
                        try:
                            illuminated = rendered.rendered[h if self.font.vertical else h + start][
                                w + start if self.font.vertical else w]
                        except IndexError:
                            illuminated = False
                        self.model.set_pixel(h, w, foreground if illuminated else background)
            rate.sleep()


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


