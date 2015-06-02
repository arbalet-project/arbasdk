"""
    Arbalet - ARduino-BAsed LEd Table
    Arbapixel - Arbalet Pixel

    Represents a rgb-colored pixel in an Arbalet table

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from pygame.color import Color

__all__ = ['Arbapixel', 'hsv']

def hsv(h, s, v, a=100):
    # ranges H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100]
    c = Color('black')
    c.hsva = map(int, (h, s, v, a))
    return (c.r, c.g, c.b, c.a)

# This class has a hack to inherit from pygame.Color with getattr since its C
# implementation does not allow to inherit properly
class Arbapixel(object):

    def __init__(self, *args):
        self.__set_pygame_color(*args)

    def __set_pygame_color(self, *args):
        if len(args)==1 and isinstance(args[0], Arbapixel): # Simulates a copy constructor
            self.__pygame_color = args[0].get_color()
        elif len(args)==1 and (isinstance(args[0], list) or isinstance(args[0], tuple)) and (len(args[0])==3 or len(args[0])==4):
            self.__pygame_color = Color(*(args[0]))
        else:
            self.__pygame_color = Color(*args)  # Normal constructor

    def __limit(self, v):
        """
        Limitator avoiding overflows and underflows
        """
        return int(max(0, min(255, v)))

    @property
    def hsv(self):
        """
        :return: The HSVA representation of this color
        """
        return self.__pygame_color.hsva

    def __set__(self, instance, value):
        self.__set_pygame_color(value)

    def __getattr__(self, name):
        return getattr(self.__pygame_color, name)

    def __add__(self, other):
        return Arbapixel(self.__limit(self.r+other.r),
                         self.__limit(self.g+other.g),
                         self.__limit(self.b+other.b),
                         self.__limit(self.a+other.a))

    def __eq__(self, other):
        return self.__pygame_color == other.__pygame_color

    def __sub__(self, other):
        return Arbapixel(self.__limit(self.r-other.r),
                         self.__limit(self.g-other.g),
                         self.__limit(self.b-other.b),
                         self.__limit(self.a-other.a))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__pygame_color.__str__()

    def __mul__(self, m):
        return Arbapixel(self.__limit(self.r*m),
                         self.__limit(self.g*m),
                         self.__limit(self.b*m),
                         self.__limit(self.a*m))

    def get_color(self):
        return self.__pygame_color

    def set_color(self, *color):
        self.__set_pygame_color(*color)

    def to_json(self):
        return [self.r, self.g, self.b, self.a]

