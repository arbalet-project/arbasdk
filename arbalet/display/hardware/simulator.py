"""
    Arbalet - ARduino-BAsed LEd Table
    Simulator - Arbalet Simulator

    Simulate an Arbalet table

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from os.path import dirname, join
from .abstract import AbstractDisplayDevice
from ...resources.img import __file__ as img_resources_path
from os import environ
from pygame import color, display, draw, Rect, error, MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, KEYUP, QUIT
from pygame.image import load_extended, get_extended
from pygame import mouse, event

__all__ = ['Simulator']


class Simulator(AbstractDisplayDevice):
    def __init__(self, host, hardware_config, diminution=1):
        super(Simulator, self).__init__(host, hardware_config, diminution)
        factor_sim = 40   # TODO autosize
        self.sim_width = self.config['width']*factor_sim
        self.sim_height = self.config['height']*factor_sim
        self.border_thickness = 1
        self.cell_height = self.sim_width/self.config['width']
        self.cell_width = self.sim_height/self.config['height']
        self.display = None
        self.previous_mouse_button_down = None

    def get_touch_events(self):
        events = []
        for e in event.get():
            if e.type in [MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
                if e.type == MOUSEBUTTONDOWN:
                    pos = mouse.get_pos()
                    pixel = int(pos[1] / self.cell_height), int(pos[0] / self.cell_width)
                    self.previous_mouse_button_down = pixel
                else:
                    if self.previous_mouse_button_down is None:
                        continue
                    else:
                        pixel = self.previous_mouse_button_down
                feedback = {'type': 'mice', 'pixel': pixel, 'pressed': e.type==MOUSEBUTTONDOWN}
                events.append(feedback)

            elif e.type in [KEYUP, KEYDOWN]:
                events.append({'key': e.key,
                               'type': 'kbd',
                               'pressed': e.type == KEYDOWN})

            elif e.type == QUIT:
                self.running = False
                print("[Arbalet Simulator] Simulator window closed, stopping server...")
                self.close()
        return events

    def connect(self):
        # Create the Window, load its title, icon
        environ['SDL_VIDEO_CENTERED'] = '1'

        self.display = display.set_mode((self.sim_width, self.sim_height), 0, 32)

        if get_extended():
            try:
                self.icon = load_extended(join(dirname(img_resources_path), 'icon.png'))
            except error:
                pass
            else:
                display.set_icon(self.icon)

        display.set_caption("Arbalet simulator", "Arbalet")

    def is_connected(self):
        return self.display is not None

    def read_touch_frame(self):
        pass

    def write_led_frame(self, end_model):
        model = self.layers.models.data_frame
        self.display.lock()
        for w in range(self.config['width']):
            for h in range(self.config['height']):
                pixel = model[h, w]
                self.display.fill(color.Color(pixel[0], pixel[1], pixel[2]),
                                  Rect(w * self.cell_width,
                                       h * self.cell_height,
                                       self.cell_width,
                                       self.cell_height))

        # Draw vertical lines
        for w in range(self.config['width']):
            draw.line(self.display, color.Color(40, 40, 40), (w * self.cell_width, 0),
                      (w * self.cell_width, self.sim_height), self.border_thickness)
        # Draw horizontal lines
        for h in range(self.config['height']):
            draw.line(self.display, color.Color(40, 40, 40), (0, h * self.cell_height),
                      (self.sim_width, h * self.cell_height), self.border_thickness)
        display.update()
        self.display.unlock()

    def close(self):
        display.quit()
