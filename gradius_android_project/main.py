# main.py (Kivy App Structure)
import kivy
kivy.require('2.0.0') # Specify Kivy version compatibility

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import pygame # Pygame will be used by the imported game logic

# Import the Pygame game logic
import actual_game_logic as gradius_game

# Constants from the original Pygame game, might be needed for Kivy side
SCREEN_WIDTH = gradius_game.SCREEN_WIDTH
SCREEN_HEIGHT = gradius_game.SCREEN_HEIGHT

class PygameGameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.size is now determined by the layout, remove fixed size

        # Initialize the Pygame game instance
        # We need to pass a dummy screen to the Pygame game,
        # as Kivy will handle the actual screen drawing.
        # However, the Game class initializes pygame.display itself.
        # This needs careful handling. For now, let the Game class init display,
        # but we'll capture its surface.

        gradius_game.screen = pygame.Surface((gradius_game.SCREEN_WIDTH, gradius_game.SCREEN_HEIGHT)) # Pygame logic draws on this
        self.game = gradius_game.Game() # Game class from actual_game_logic.py

        # Kivy texture to display the Pygame surface. Initialized with game's native size.
        # It will be updated with scaled surface data.
        self.texture = Texture.create(size=(gradius_game.SCREEN_WIDTH, gradius_game.SCREEN_HEIGHT), colorfmt='rgb')

        # Schedule the game loop
        self.game_update_event = Clock.schedule_interval(self.update_pygame, 1.0 / 60.0) # Target 60 FPS

        # Touch input state for player
        self.touch_move_up = False
        self.touch_move_down = False
        self.touch_move_left = False
        self.touch_move_right = False
        self.touch_shoot = False

    def update_pygame(self, dt):
        # Process Pygame events (minimal, as Kivy handles main events)
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         App.get_running_app().stop()

        # Pass touch input state to the Pygame player
        # This requires modifying the Player class in actual_game_logic.py
        # to accept these states instead of direct pygame.key.get_pressed()
        player_input_state = {
            'up': self.touch_move_up,
            'down': self.touch_move_down,
            'left': self.touch_move_left,
            'right': self.touch_move_right,
            'shoot': self.touch_shoot
        }
        self.game.player.update_input_from_kivy(player_input_state) # New method needed in Pygame Player
        if self.touch_shoot:
             # Handle shooting based on Kivy input - might need a cooldown in Player
            self.game.player_shoot_from_kivy() # New method or logic in Game/Player
            self.touch_shoot = False # Reset after one shot, or manage cooldown

        # Run the Pygame game's update logic
        self.game.update_game_state() # This should NOT include event handling or display.flip

        # Draw the Pygame game's screen to our Kivy texture
        self.game.draw_elements_to_surface(gradius_game.screen) # New method to draw to a given surface

        # Flip the Pygame surface pixels (if necessary, depends on surface format)
        # For RGB, Pygame surfaces are typically top-to-bottom, Kivy textures bottom-to-top.
        # pygame.transform.flip(surface, flip_x, flip_y)
        flipped_surface = pygame.transform.flip(gradius_game.screen, False, True)

        # --- Screen Scaling Logic ---
        scale_w = self.width / gradius_game.SCREEN_WIDTH
        scale_h = self.height / gradius_game.SCREEN_HEIGHT
        scale = min(scale_w, scale_h)

        scaled_width = int(gradius_game.SCREEN_WIDTH * scale)
        scaled_height = int(gradius_game.SCREEN_HEIGHT * scale)

        scaled_surface = pygame.transform.smoothscale(flipped_surface, (scaled_width, scaled_height))

        buf = scaled_surface.get_view('3') # Get a 3-byte view (RGB)

        # Update self.texture. Recreate if size mismatches (not optimal but functional for now)
        if self.texture.size[0] != scaled_width or self.texture.size[1] != scaled_height:
            self.texture = Texture.create(size=(scaled_width, scaled_height), colorfmt='rgb')

        self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

        # Calculate centered position *within the widget's own coordinate system*
        centered_pos_x = (self.width - scaled_width) / 2
        centered_pos_y = (self.height - scaled_height) / 2

        # Redraw this Kivy widget
        self.canvas.clear()
        with self.canvas:
            kivy.graphics.Rectangle(texture=self.texture, pos=(centered_pos_x, centered_pos_y), size=(scaled_width, scaled_height))

    def on_touch_down(self, touch):
        # Example: Check if touch is on a conceptual 'shoot' button area
        # This will be replaced by actual Kivy buttons later
        if touch.x > self.width * 0.8 and touch.y < self.height * 0.2: # Bottom-right corner for shoot
            self.touch_shoot = True
        # Pass touch to children if any (e.g. Kivy buttons)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        # if touch.x > self.width * 0.8 and touch.y < self.height * 0.2:
        # self.touch_shoot = False # Reset continuous shooting if needed
        return super().on_touch_up(touch)

    def pause_game(self):
        """Pauses the Pygame game update loop and sets the game's internal pause state."""
        self.game.game_paused = True # Set internal game pause state
        if self.game_update_event:
            self.game_update_event.cancel() # Unschedules self.update_pygame
            # Alternatively, Clock.unschedule(self.update_pygame) could be used if event not stored

    def resume_game(self):
        """Resumes the Pygame game update loop and unsets the game's internal pause state."""
        self.game.game_paused = False # Unset internal game pause state
        # Re-schedule the game update loop if it's not already scheduled
        # (Ensure not to double-schedule if Clock.unschedule wasn't effective or called multiple times)
        Clock.unschedule(self.update_pygame) # Ensure it's not scheduled before rescheduling
        self.game_update_event = Clock.schedule_interval(self.update_pygame, 1.0 / 60.0)


class GradiusKivyApp(App):
    def build(self):
        layout = FloatLayout()

        # PygameGameWidget now uses size_hint=(1,1) to fill the layout
        self.game_widget = PygameGameWidget(size_hint=(1, 1))
        layout.add_widget(self.game_widget)

        # --- Add Kivy On-Screen Buttons ---
        # Movement Buttons (D-pad like)
        # UP
        btn_up = Button(text='UP', size_hint=(None, None), size=(100, 70), pos_hint={'x': 0.1, 'y': 0.2})
        btn_up.bind(on_press=self.press_up, on_release=self.release_up)
        layout.add_widget(btn_up)

        # DOWN
        btn_down = Button(text='DN', size_hint=(None, None), size=(100, 70), pos_hint={'x': 0.1, 'y': 0.05})
        btn_down.bind(on_press=self.press_down, on_release=self.release_down)
        layout.add_widget(btn_down)

        # LEFT
        btn_left = Button(text='LT', size_hint=(None, None), size=(100, 70), pos_hint={'x': 0.01, 'y': 0.125})
        btn_left.bind(on_press=self.press_left, on_release=self.release_left)
        layout.add_widget(btn_left)

        # RIGHT
        btn_right = Button(text='RT', size_hint=(None, None), size=(100, 70), pos_hint={'x': 0.19, 'y': 0.125}) # x adjusted
        btn_right.bind(on_press=self.press_right, on_release=self.release_right)
        layout.add_widget(btn_right)

        # SHOOT Button
        btn_shoot = Button(text='SHOOT', size_hint=(None, None), size=(120, 90), pos_hint={'right': 0.99, 'y': 0.05})
        btn_shoot.bind(on_press=self.press_shoot) # For shoot, on_press is enough, it's not continuous
        layout.add_widget(btn_shoot)

        return layout

    # Callbacks for button presses/releases
    def press_up(self, instance): self.game_widget.touch_move_up = True
    def release_up(self, instance): self.game_widget.touch_move_up = False
    def press_down(self, instance): self.game_widget.touch_move_down = True
    def release_down(self, instance): self.game_widget.touch_move_down = False
    def press_left(self, instance): self.game_widget.touch_move_left = True
    def release_left(self, instance): self.game_widget.touch_move_left = False
    def press_right(self, instance): self.game_widget.touch_move_right = True
    def release_right(self, instance): self.game_widget.touch_move_right = False
    def press_shoot(self, instance): self.game_widget.touch_shoot = True

    def on_pause(self):
        """Handle the Kivy app pausing (e.g., when app goes to background on Android)."""
        if self.game_widget:
            self.game_widget.pause_game()
        return True # Important to return True to indicate pause is handled

    def on_resume(self):
        """Handle the Kivy app resuming (e.g., when app comes to foreground on Android)."""
        if self.game_widget:
            self.game_widget.resume_game()
        # No return True needed for on_resume by default


if __name__ == '__main__':
    # Critical: Ensure Pygame display is not initialized by the game logic directly
    # in a way that conflicts with Kivy. The Game class in actual_game_logic.py
    # might need its pygame.display.set_mode and pygame.font.init() calls adjusted or removed.
    # For this subtask, assume actual_game_logic.py's Game.__init__ is adjusted.

    # We also need to adjust actual_game_logic.py:
    # 1. Game class:
    #    - __init__ should not call pygame.display.set_mode(). It should expect a screen surface.
    #    - Remove pygame.quit() from its run() method or main game loop. Kivy handles app exit.
    #    - draw_elements() should be renamed/refactored to draw_elements_to_surface(self, surface)
    #    - handle_input() should be removed or adapted if Kivy takes over all input.
    #    - update_game_state() should remain largely the same but without event polling.
    #    - run() method needs to be broken down: Kivy will call an update/draw tick.
    # 2. Player class:
    #    - update() method needs to change from using pygame.key.get_pressed() to
    #      using passed-in state from Kivy (e.g., self.update_input_from_kivy(state_dict)).
    #    - A new method like player_shoot_from_kivy() might be needed in Player or Game.
    #
    # These changes to actual_game_logic.py are complex and will be handled in a *separate* subtask.
    # This current subtask focuses on creating main.py with the Kivy structure.

    GradiusKivyApp().run()
