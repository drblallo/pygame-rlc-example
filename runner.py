import sys
import wrapper
import pygame
from pygame.locals import *

pygame.init()
from engine import Engine, Animation
from gui import *


def get_player_color(player_id):
    return (255, 0, 0) if player_id == 1 else (0, 255, 0)


def on_slot_change(engine, x: int, y: int, player: int):
    engine.schedule(
        ChangeColor(
            row=x,
            col=y,
            start_color=engine.gui_manager.get_cell_color(x, y),
            end_color=get_player_color(player),
            duration=1.0,
        )
    )
    engine.gui_manager.set_cell_text(x, y, "X" if player == 0 else "O")


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


def click_to_mark(event: pygame.event) -> wrapper.GameMark:
    action = wrapper.GameMark()
    (x, y) = get_cell(event.pos)
    wrapper.functions.assign(action.x, x)
    wrapper.functions.assign(action.y, y)
    return action


# Main loop
def main():
    engine = Engine(wrapper, CellManager(BOARD_ROWS, BOARD_COLS))
    engine.input_handler.register_handler(MOUSEBUTTONDOWN, click_to_mark)
    engine.event_handler.on_slot_change = on_slot_change
    wrapper.functions.set_handler(engine.state.board, engine.event_handler)
    engine.main_loop()
    pygame.quit()


if __name__ == "__main__":
    main()
