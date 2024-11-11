from engine import Engine, Animation
import pygame
from pygame.locals import *
from .constants import *

# Font
FONT = pygame.font.SysFont(None, 40)


# Cell Manager to handle cell states
class CellManager:
    def __init__(self, rows, cols, default_color=DEFAULT_CELL_COLOR):
        self.engine = None
        self.rows = rows
        self.cols = cols
        # Initialize a 2D list for cell colors
        self.cell_colors = [[default_color for _ in range(cols)] for _ in range(rows)]
        # Initialize a 2D list for cell texts
        self.cell_texts = [["" for _ in range(cols)] for _ in range(rows)]

    def set_engine(self, engine):
        self.engine = engine

    def set_cell_color(self, row, col, color):
        self.cell_colors[row][col] = color

    def get_cell_color(self, row, col):
        return self.cell_colors[row][col]

    def set_cell_text(self, row, col, text):
        self.cell_texts[row][col] = text

    def get_cell_text(self, row, col):
        return self.cell_texts[row][col]

    def draw(self, surface, font=FONT):

        for row in range(self.rows):
            for col in range(self.cols):
                # Draw cell background
                rect = pygame.Rect(
                    col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(surface, self.cell_colors[row][col], rect)

                # Draw cell text if any
                text = self.cell_texts[row][col]
                if text:
                    text_image = font.render(text, True, TEXT_COLOR)
                    text_rect = text_image.get_rect(
                        center=(
                            col * CELL_SIZE + CELL_SIZE / 2,
                            row * CELL_SIZE + CELL_SIZE / 2,
                        )
                    )
                    surface.blit(text_image, text_rect)
        self.draw_grid()  # Draw grid lines

    # Draw the grid lines
    def draw_grid(self):
        # Horizontal lines
        for row in range(1, BOARD_ROWS):
            pygame.draw.line(
                self.engine.screen,
                LINE_COLOR,
                (0, row * CELL_SIZE),
                (WIDTH, row * CELL_SIZE),
                LINE_WIDTH,
            )
            # Vertical lines
        for col in range(1, BOARD_COLS):
            pygame.draw.line(
                self.engine.screen,
                LINE_COLOR,
                (col * CELL_SIZE, 0),
                (col * CELL_SIZE, HEIGHT),
                LINE_WIDTH,
            )
