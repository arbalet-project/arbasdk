# Grid of Arbasim
import pygame

class Grid(object):
    def __init__(self, cell_height,cell_width,num_cells_wide,num_cells_tall, color):
        self.cell_height = cell_height
        self.cell_width = cell_width
        self.num_cells_wide = num_cells_wide
        self.num_cells_tall = num_cells_tall
        self.color = color
        self.height = cell_height * num_cells_tall
        self.width = cell_width  * num_cells_wide
        self.border_thickness = 1

    def render(self, screen, state):
        screen.lock()
        # Draw pixels
        if state:
            i = 0
            for w in range(state.get_width()):
                for h in range(state.get_height()):
                    i = i+1
                    pixel = state.get_pixel(h, w).get_color()
                    screen.fill(pixel, pygame.Rect(w*self.cell_width,
                                                   h*self.cell_height,
                                                   self.cell_width,
                                                   self.cell_height))
        # Draw vertical lines
        for w in range(self.num_cells_wide):
            pygame.draw.line(screen, self.color, (w*self.cell_width, 0), (w*self.cell_width, self.height), self.border_thickness)
        # Draw horizontal lines
        for h in range(self.num_cells_tall):
            pygame.draw.line(screen, self.color, (0, h*self.cell_height), (self.width, h*self.cell_height), self.border_thickness)
        screen.unlock()



