"""
    Arbalet - ARduino-BAsed LEd Table
    Arbasim - Arbalet Simulator

    Simulate an Arbalet table

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import pygame
import logging
from threading import Thread
from os import environ
from pygame import display, draw, quit, font, color, init as pygame_init, Rect, QUIT
from . rate import Rate

__all__ = ['Arbasim']

class Arbasim(Thread):
    def __init__(self, arbalet_height, arbalet_width, sim_height, sim_width, rate=30, interactive=True, autorun=True):
        """
        Arbasim constructor: launches the simulation
        Simulate a "arbalet_width x arbalet_height px" table rendered in a "sim_width x sim_height" window
        :param arbalet_width: Number of pixels of Arbalet in width
        :param arbalet_height: Number of pixels of Arbalet in height
        :param sim_width:
        :param sim_height:
        :param rate: Refresh rate in Hertz
        :param interactive: True if the simulator is run in an interactive python console or if it's used without Arbapp inheritance
        :return:
        """
        Thread.__init__(self)
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%I:%M:%S')
        self.sim_state = "idle"
        self.running = True
        self.rate = Rate(rate)
        self.interactive = interactive

        # Current table model storing all pixels
        self.arbamodel = None

        self.sim_width = sim_width
        self.sim_height = sim_height
        self.arbalet_width = arbalet_width
        self.arbalet_height = arbalet_height
        self.grid = Grid(sim_width/arbalet_width, sim_height/arbalet_height, arbalet_width, arbalet_height, (40, 40, 40))

        # Init Pygame
        if self.interactive:
            pygame_init()
        environ['SDL_VIDEO_CENTERED'] = '1'
        logging.info("Pygame initialized")
        self.screen = pygame.display.set_mode((self.sim_width, self.sim_height), 0, 32)
        self.sim_state = "idle"
        self.font = pygame.font.SysFont('sans', 14)

        # Autorun
        if autorun:
            self.start()

    def close(self, reason='unknown'):
        pygame.display.quit()
        self.sim_state = "exiting"
        logging.info("Simulator exiting, reason: "+reason)
        self.running = False

    def set_model(self, arbamodel):
        """
        Updates the current model of the simulator
        :param arbamodel:
        :return:
        """
        self.arbamodel = arbamodel
        self.sim_state = "running" if arbamodel!=None else "idle"

    def run(self):
        # Main Simulation loop
        while self.running:
            if pygame.event.peek(QUIT): # Shouldn't .get() to avoid emptying the event queue, warning: might fill up the queue if it's never emptied with .get() in the app
                self.close("User request")
                break

            # Render background and title
            pygame.draw.rect(self.screen,(0, 0, 0), pygame.Rect(0, 0, self.sim_width+2, self.sim_height+2))
            pygame.display.set_caption("Arbasim [{}]".format(self.sim_state))

            # Render grid and pixels
            self.grid.render(self.screen, self.arbamodel)

            #caption = "[{}] Caption...".format(self.sim_state)
            #rendered_caption = self.font.render(caption, 1, (255, 255, 255))
            #location_caption = pygame.Rect((10,10), (300,20))
            #self.screen.blit(rendered_caption, location_caption)

            pygame.display.update()
            self.rate.sleep()
        if self.interactive:
            pygame.quit()

class Grid(object):
    """
    This is the grid of Arbasim, drawn with squares for pixels and lines for the separating grid
    :param cell_height: Number of pixels of a single celle in height
    :param cell_width: Number of pixels of a single cell in width
    :param num_cells_wide: number of cells in width
    :param num_cells_tall: number of cells in height
    :param color: color of background
    :return:
    """
    def __init__(self, cell_height, cell_width, num_cells_wide, num_cells_tall, color):
        self.cell_height = cell_height
        self.cell_width = cell_width
        self.num_cells_wide = num_cells_wide
        self.num_cells_tall = num_cells_tall
        self.color = color
        self.height = cell_height * num_cells_tall
        self.width = cell_width  * num_cells_wide
        self.border_thickness = 1

    def render(self, screen, model):
        screen.lock()
        # Draw pixels
        if model:
            model.lock()
            for w in range(model.get_width()):
                for h in range(model.get_height()):
                    pixel = model.get_pixel(h, w)
                    screen.fill(color.Color(pixel.r, pixel.g, pixel.b),
                                pygame.Rect(w*self.cell_width,
                                h*self.cell_height,
                                self.cell_width,
                                self.cell_height))
            model.unlock()
        # Draw vertical lines
        for w in range(self.num_cells_wide):
            pygame.draw.line(screen, self.color, (w*self.cell_width, 0), (w*self.cell_width, self.height), self.border_thickness)
        # Draw horizontal lines
        for h in range(self.num_cells_tall):
            pygame.draw.line(screen, self.color, (0, h*self.cell_height), (self.width, h*self.cell_height), self.border_thickness)
        screen.unlock()
