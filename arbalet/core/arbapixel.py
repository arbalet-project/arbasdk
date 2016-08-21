"""
    Arbalet - ARduino-BAsed LEd Table
    Pixel - Arbalet Pixel

    Represents a rgb-colored pixel in an Arbalet table

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from pygame.color import Color

__all__ = ['Pixel', 'hsv']

def hsv(h, s, v, a=100):
    # ranges H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100]
    c = Color(0, 0, 0)
    c.hsva = list(map(int, (h, s, v, a)))
    return (c.r, c.g, c.b, c.a)

class Pixel(object):
    """
    Pixel represents a single pixel at a h, w coordinate with a RGB color.
    pygame.Color is used for hsv conversion as well as init from string
    """

    def __init__(self, args):
        """
        This constructor squeezes a lot of runtime checks to speed up execution.
        This might cause less easily understandable runtime exceptions (color components are strings, have >3 elements, ...)
        :param args: A string representing the color, another Pixel that will be copied or a 3-tuple [r, g, b]
        """
        self.__set__(type(args), args)

    @property
    def hsva(self):
        """
        :return: The HSVA representation of this color
        """
        return Color(self.r, self.g, self.b).hsva

    def __add__(self, other):
        return Pixel((min(255, self.r+other.r),
                          min(255, self.g+other.g),
                          min(255, self.b+other.b)))

    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b

    def __sub__(self, other):
        return Pixel((max(0, self.r-other.r),
                          max(0, self.g-other.g),
                          max(0, self.b-other.b)))
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '['+str(self.r)+', '+str(self.g)+', '+str(self.b)+']'

    def __mul__(self, m):
        def limit(v):
            return max(0, min(255, int(v)))
        return Pixel((limit(self.r*m),
                          limit(self.g*m),
                          limit(self.b*m)))

    def __set__(self, instance, value):
        if instance==tuple or instance==list:
            self.r, self.g, self.b = value[0], value[1], value[2]
        elif instance==Pixel:
            self.r, self.g, self.b = value.r, value.g,  value.b
        else:
            # If we receive something else, pray that pygame.Color will recognize this color (including strings)
            color = Color(value)
            self.r, self.g, self.b = color.r, color.g,  color.b

    def to_json(self):
        return [self.r, self.g, self.b]

