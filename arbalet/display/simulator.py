"""
    Arbalet - ARduino-BAsed LEd Table
    Simulator - Arbalet Simulator

    Simulate an Arbalet table

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from os.path import dirname, join
from ..tools import Rate
from ..resources.img import __file__ as img_resources_path
from threading import Thread
from os import environ
from pygame import color, display, draw, Rect, error, MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, KEYUP, QUIT
from pygame.image import load_extended, get_extended
from pygame import mouse, event

__all__ = ['Simulator']


class Simulator(Thread):
    def __init__(self, arbalet, sim_height, sim_width):
        Thread.__init__(self)
        self.arbalet = arbalet
        self.sim_width = sim_width
        self.sim_height = sim_height
        self.border_thickness = 1
        self.cell_height = sim_width/arbalet.width
        self.cell_width = sim_height/arbalet.height
        self.rate = Rate(arbalet.config['refresh_rate'])
        self.running = False
        self.previous_mouse_button_down = None

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

        self.start()

    def get_touch_events(self):
        events = []
        if self.running:
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
                    print("[Arbalet Simulator] Simulator window closed, stopping thread...")
                    break
        return events

    def close(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            model = self.arbalet.model.data_frame
            self.display.lock()
            for w in range(self.arbalet.width):
                for h in range(self.arbalet.height):
                    pixel = model[h, w]
                    self.display.fill(color.Color(pixel[0], pixel[1], pixel[2]),
                                     Rect(w*self.cell_width,
                                     h*self.cell_height,
                                     self.cell_width,
                                     self.cell_height))

            # Draw vertical lines
            for w in range(self.arbalet.width):
                draw.line(self.display, color.Color(40, 40, 40), (w*self.cell_width, 0), (w*self.cell_width, self.sim_height), self.border_thickness)
            # Draw horizontal lines
            for h in range(self.arbalet.height):
                draw.line(self.display, color.Color(40, 40, 40), (0, h*self.cell_height), (self.sim_width, h*self.cell_height), self.border_thickness)
            display.update()
            self.display.unlock()
            self.rate.sleep()

        display.quit()
