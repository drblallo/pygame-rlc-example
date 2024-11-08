import pygame
import sys
import dataclasses
from pygame.locals import *
import time
import wrapper

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15
BOARD_ROWS = 3
BOARD_COLS = 3
CELL_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = CELL_SIZE//3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = CELL_SIZE//4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
DEFAULT_CELL_COLOR = BG_COLOR
TEXT_COLOR = (0, 0, 0)

# Setup the screen
screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption('Tic Tac Toe with Animation Engine')
screen.fill(BG_COLOR)

# Font
FONT = pygame.font.SysFont(None, 40)

# Animation Engine
class Animation:
    def __init__(self):
        self.finished = False

    def update(self, delta_time):
        pass

    def draw(self, surface):
        pass

class ChangeColor(Animation):
    def __init__(self, row, col, start_color, end_color, duration, cell_manager):
        super().__init__()
        self.row = row
        self.col = col
        self.start_color = start_color
        self.end_color = end_color
        self.duration = duration
        self.elapsed = 0
        self.cell_manager = cell_manager  # Reference to cell manager to update cell color

    def update(self, delta_time):
        self.elapsed += delta_time
        if self.elapsed >= self.duration:
            self.elapsed = self.duration
            self.finished = True
            # Update the cell's color to the end color
            self.cell_manager.set_cell_color(self.row, self.col, self.end_color)

    def draw(self, surface):
        # Only draw during the animation
        if not self.finished:
            # Linear interpolation of colors
            ratio = self.elapsed / self.duration
            current_color = (
                int(self.start_color[0] + (self.end_color[0] - self.start_color[0]) * ratio),
                int(self.start_color[1] + (self.end_color[1] - self.start_color[1]) * ratio),
                int(self.start_color[2] + (self.end_color[2] - self.start_color[2]) * ratio),
            )
            rect = pygame.Rect(self.col * CELL_SIZE, self.row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, current_color, rect)

class PrintText(Animation):
    def __init__(self, text, position, color, duration, font=FONT):
        super().__init__()
        self.text = text
        self.position = position
        self.color = color
        self.duration = duration
        self.elapsed = 0
        self.font = font
        self.image = self.font.render(self.text, True, self.color)

    def update(self, delta_time):
        self.elapsed += delta_time
        if self.elapsed >= self.duration:
            self.finished = True

    def draw(self, surface):
        # Only draw during the animation
        if not self.finished:
            surface.blit(self.image, self.position)

class AnimationEngine:
    def __init__(self):
        self.animations = []

    def schedule(self, animation):
        self.animations.append(animation)

    def update(self, delta_time):
        for animation in self.animations[:]:
            animation.update(delta_time)
            if animation.finished:
                self.animations.remove(animation)

    def draw(self, surface):
        for animation in self.animations:
            animation.draw(surface)

# Cell Manager to handle cell states
class CellManager:
    def __init__(self, rows, cols, default_color=DEFAULT_CELL_COLOR):
        self.rows = rows
        self.cols = cols
        # Initialize a 2D list for cell colors
        self.cell_colors = [[default_color for _ in range(cols)] for _ in range(rows)]
        # Initialize a 2D list for cell texts
        self.cell_texts = [["" for _ in range(cols)] for _ in range(rows)]

    def set_cell_color(self, row, col, color):
        self.cell_colors[row][col] = color

    def get_cell_color(self, row, col):
        return self.cell_colors[row][col]

    def set_cell_text(self, row, col, text):
        self.cell_texts[row][col] = text

    def get_cell_text(self, row, col):
        return self.cell_texts[row][col]

    def draw_cells(self, surface, font=FONT):
        for row in range(self.rows):
            for col in range(self.cols):
                # Draw cell background
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, self.cell_colors[row][col], rect)

                # Draw cell text if any
                text = self.cell_texts[row][col]
                if text:
                    text_image = font.render(text, True, TEXT_COLOR)
                    text_rect = text_image.get_rect(center=(col * CELL_SIZE + CELL_SIZE/2, row * CELL_SIZE + CELL_SIZE/2))
                    surface.blit(text_image, text_rect)


# Fill function (to be implemented by the user)
def fill(row, col, player, animation_engine, cell_manager):
    """
    This function is called when a cell is clicked.
    Implement your own logic here.
    For demonstration, we'll schedule a ChangeColor and PrintText animation.
    """
    # Prevent filling an already filled cell
    if cell_manager.get_cell_text(row, col):
        print("Cell already filled!")
        return

    # Define the cell's rectangle
    rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

    # Schedule a color change animation
    start_color = cell_manager.get_cell_color(row, col)
    end_color = (255, 0, 0) if player == 1 else (0, 255, 0)  # Change to red
    change_color = ChangeColor(row, col, start_color, end_color, 1.0, cell_manager)  # 1 second duration
    animation_engine.schedule(change_color)

    # Schedule a text print animation
    text_position = (col * CELL_SIZE + SPACE, row * CELL_SIZE + SPACE)
    print_text = PrintText("X" if player == 1 else "O", text_position, TEXT_COLOR, 2)
    animation_engine.schedule(print_text)

    # Set the cell text after the text animation completes
    # This ensures the text is persistent after animation
    # We'll use a simple approach by scheduling another animation to set the text
    class SetTextAfterAnimation(Animation):
        def __init__(self, row, col, text, delay):
            super().__init__()
            self.row = row
            self.col = col
            self.text = text
            self.delay = delay
            self.elapsed = 0

        def update(self, delta_time):
            self.elapsed += delta_time
            if self.elapsed >= self.delay:
                self.finished = True
                cell_manager.set_cell_text(self.row, self.col, self.text)

    set_text = SetTextAfterAnimation(row, col, "X" if player == 1 else "O", 2.0)  # Set text after 2 seconds
    animation_engine.schedule(set_text)

# Draw the grid lines
def draw_grid():
    # Horizontal lines
    for row in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, row * CELL_SIZE), (WIDTH, row * CELL_SIZE), LINE_WIDTH)
    # Vertical lines
    for col in range(1, BOARD_COLS):
        pygame.draw.line(screen, LINE_COLOR, (col * CELL_SIZE, 0), (col * CELL_SIZE, HEIGHT), LINE_WIDTH)

# Determine which cell was clicked
def get_cell(pos):
    x, y = pos
    row = y // CELL_SIZE
    col = x // CELL_SIZE
    if row >= BOARD_ROWS or col >= BOARD_COLS:
        return None
    x = wrapper.BIntT0T3T()
    x.value = row
    y = wrapper.BIntT0T3T()
    y.value = col
    return (x, y)

class GameEventHandler:
    def __init__(self, engine):
        self.handlers = {}
        self.engine = engine

    def __getattr__(self, attribute):
        if attribute in self.__dict__:
            return self.__dict__[attribute]
        if attribute in self.handlers:
            return self.handlers[attribute]
        return super().__getattribute__(attribute)

    def __setattr__(self, attribute, value):
        if attribute != "engine" and attribute != "handlers":
            self.handlers[attribute] = lambda *args: value(self.engine, *args)
            return value
        else:
            super().__setattr__(attribute, value)


    def on_valid_action(self, action):
        wrapper.functions.print(action)

    def on_invalid_action(self, action):
        print("INVALID: ", end="")
        sys.stdout.flush()
        wrapper.functions.print(action)


class InputHandler:
    def __init__(self, engine):
        self.special_handlers = {}
        self.engine = engine

    def register_handler(self, event_type: pygame.event.EventType, event_to_action):
        self.special_handlers[event_type] = event_to_action

    def on_input(self, input: pygame.event):
        if input.type == QUIT:
            self.engine.running = False
            return

        for event_type, handler in self.special_handlers.items():
            if input.type == event_type:
                action = handler(input)
                if not isinstance(action, wrapper.AnyGameAction):
                    real = wrapper.AnyGameAction()
                    wrapper.functions.assign(real, action)
                    action = real
                if wrapper.functions.can_apply(action, self.engine.game_state):
                    self.engine.on_valid_action(action)
                    wrapper.functions.apply(action, self.engine.game_state)
                else:
                    self.engine.on_invalid_action(action)

class Engine:
    def __init__(self, game_state):
        self.event_handler = GameEventHandler(self)
        self.input_handler = InputHandler(self)
        self.game_state = game_state
        self.clock = pygame.time.Clock()
        self.running = True
        self.animation_engine = AnimationEngine()
        self.cell_manager = CellManager(BOARD_ROWS, BOARD_COLS)

    def next_frame(self):
        delta_time = self.clock.tick(60) / 1000.0  # Delta time in seconds

        for event in pygame.event.get():
            self.input_handler.on_input(event)

        # Update animations
        self.animation_engine.update(delta_time)

        # Redraw the screen
        screen.fill(BG_COLOR)
        self.cell_manager.draw_cells(screen)  # Draw cell backgrounds and texts
        draw_grid()  # Draw grid lines
        self.animation_engine.draw(screen)  # Draw active animations

        pygame.display.flip()

    def main_loop(self):
        while self.running:
            self.next_frame()

    def on_valid_action(self, action):
        self.event_handler.on_valid_action(action)

    def on_invalid_action(self, action):
        self.event_handler.on_invalid_action(action)


def on_slot_change(engine, x: int, y: int, player: int):
    fill(x, y, player, engine.animation_engine, engine.cell_manager)


def click_to_mark(event: pygame.event) -> wrapper.GameMark:
    action = wrapper.GameMark()
    (x, y) = get_cell(event.pos)
    wrapper.functions.assign(action.x, x)
    wrapper.functions.assign(action.y, y)
    return action

# Main loop
def main():
    state = wrapper.functions.play()
    engine = Engine(state)

    engine.input_handler.register_handler(MOUSEBUTTONDOWN, click_to_mark)
    engine.event_handler.on_slot_change = on_slot_change
    wrapper.functions.set_handler(state.board, engine.event_handler)

    engine.main_loop()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

