import pygame
import dataclasses
from pygame.locals import *
import json
import time
import sys


# Animation Engine
class Animation:
    def __init__(self):
        self.finished = False

    def done(self):
        self.finished = True

    def update(self, engine, delta_time):
        pass

    def draw(self, engine, surface):
        pass


class AnimationEngine:
    def __init__(self, engine):
        self.animations = []
        self.engine = engine

    def schedule(self, animation):
        self.animations.append(animation)

    def update(self, delta_time):
        for animation in self.animations[:]:
            animation.update(self.engine, delta_time)
            if animation.finished:
                self.animations.remove(animation)

    def draw(self, surface):
        for animation in self.animations:
            animation.draw(self.engine, surface)


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
        self.engine.game_rules_module.functions.print(action)

    def on_invalid_action(self, action):
        print("INVALID: ", end="")
        sys.stdout.flush()
        self.engine.game_rules_module.functions.print(action)


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
                if not isinstance(action, self.engine.game_rules_module.AnyGameAction):
                    real = self.engine.game_rules_module.AnyGameAction()
                    self.engine.game_rules_module.functions.assign(real, action)
                    action = real
                if self.engine.game_rules_module.functions.can_apply(
                    action, self.engine.state
                ):
                    self.engine.on_valid_action(action)
                    self.engine.game_rules_module.functions.apply(
                        action, self.engine.state
                    )
                else:
                    self.engine.on_invalid_action(action)


class Engine:
    def __init__(self, game_rules_module, gui_manager):
        gui_manager.set_engine(self)
        self.game_rules_module = game_rules_module
        self.event_handler = GameEventHandler(self)
        self.input_handler = InputHandler(self)
        self.state = game_rules_module.functions.play()
        self.clock = pygame.time.Clock()
        self.running = True
        self.animation_engine = AnimationEngine(self)
        self.gui_manager = gui_manager
        self.bg_color = (28, 170, 156)
        self.width, self.height = 600, 600

        pygame.display.set_caption("Tic Tac Toe with Animation Engine")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill(self.bg_color)

    def schedule(self, animation):
        self.animation_engine.schedule(animation)

    def next_frame(self):
        delta_time = self.clock.tick(60) / 1000.0  # Delta time in seconds

        for event in pygame.event.get():
            self.input_handler.on_input(event)

        # Update animations
        self.animation_engine.update(delta_time)

        # Redraw the screen
        self.screen.fill(self.bg_color)
        self.gui_manager.draw(self.screen)  # Draw cell backgrounds and texts
        self.animation_engine.draw(self.screen)  # Draw active animations

        pygame.display.flip()

    def main_loop(self):
        while self.running:
            self.next_frame()

    def on_valid_action(self, action):
        self.event_handler.on_valid_action(action)

    def on_invalid_action(self, action):
        self.event_handler.on_invalid_action(action)
