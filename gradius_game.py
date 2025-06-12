import pygame
import random

# Initialize Pygame
pygame.init()
pygame.font.init() # Explicitly initialize font module for text rendering

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gradius Clone - Procedural")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREY = (128, 128, 128)

# Game clock (for controlling FPS)
clock = pygame.time.Clock()

# Game constants
PLAYER_SPEED = 5  # Speed of the player ship
BULLET_SPEED = 10 # Speed of player bullets
OBSTACLE_SCROLL_SPEED_BASE = 2 # Initial speed for obstacles scrolling

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    """Represents the player's ship."""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 30]) # Player: A white rectangle
        self.image.fill(WHITE)
        self.rect = self.image.get_rect() # Gets the rectangle area of the image
        self.rect.x = 50 # Initial X position
        self.rect.centery = SCREEN_HEIGHT // 2 # Initial Y position (centered vertically)

    def update(self):
        """Updates the player's position based on key presses."""
        keys = pygame.key.get_pressed() # Get the state of all keyboard keys
        current_speed_x = 0
        current_speed_y = 0
        if keys[pygame.K_LEFT]:
            current_speed_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            current_speed_x = PLAYER_SPEED
        if keys[pygame.K_UP]:
            current_speed_y = -PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            current_speed_y = PLAYER_SPEED

        self.rect.x += current_speed_x
        self.rect.y += current_speed_y

        # Keep player on screen (boundary checks)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def shoot(self):
        """Creates and returns a new Bullet object."""
        # Bullet spawns from the front-right of the player
        bullet = Bullet(self.rect.right, self.rect.centery)
        return bullet

# --- Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    """Represents an enemy ship."""
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface([40, 20]) # Enemies: Red rectangles
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        # Spawn off-screen to the right at a random y position
        self.rect.x = SCREEN_WIDTH + random.randint(20, 100) # Start off-screen
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height) # Random vertical position
        self.speed = speed # Speed is determined by the current stage

    def update(self):
        """Moves the enemy to the left and removes it if it goes off-screen."""
        self.rect.x -= self.speed
        # Remove enemy if it goes off screen to the left
        if self.rect.right < 0:
            self.kill() # Pygame sprite method to remove from all groups

# --- Bullet Class ---
class Bullet(pygame.sprite.Sprite):
    """Represents a bullet fired by the player."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([10, 5]) # Bullets: Small yellow rectangles
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x # Initial X position (from player's ship)
        self.rect.centery = y # Initial Y position (from player's ship)

    def update(self):
        """Moves the bullet to the right and removes it if it goes off-screen."""
        self.rect.x += BULLET_SPEED
        # Remove bullet if it goes off screen to the right
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

# --- Obstacle Class ---
class Obstacle(pygame.sprite.Sprite):
    """Represents a stationary or slowly moving obstacle."""
    def __init__(self, x, y, width, height):
        super().__init__()
        # Obstacles: Grey rectangles
        # Ensure positive integer dimensions for the surface
        self.image = pygame.Surface([max(1, int(width)), max(1, int(height))])
        self.image.fill(GREY)
        self.rect = self.image.get_rect()
        self.rect.x = x # Initial X position
        self.rect.y = y # Initial Y position
        self.scroll_speed = OBSTACLE_SCROLL_SPEED_BASE # Initial scroll speed, can be updated per stage

    def update(self):
        """Moves the obstacle to the left based on its scroll speed."""
        self.rect.x -= self.scroll_speed
        # Remove obstacle if it goes off screen to the left
        if self.rect.right < 0:
            self.kill()

    def set_scroll_speed(self, speed):
        """Allows dynamic adjustment of the obstacle's scroll speed."""
        self.scroll_speed = speed

# --- Game Class ---
class Game:
    """Manages the overall game state, logic, and events."""
    def __init__(self):
        """Initializes the game environment, player, and sprite groups."""
        self.screen = screen # Reference to the main display surface
        self.clock = clock   # Reference to the Pygame clock for FPS control

        # Attempt to load a specific system font, fall back to default if not found
        try:
            self.font = pygame.font.SysFont("arial", 28) # Slightly larger font for HUD
        except pygame.error:
            self.font = pygame.font.Font(None, 34) # Default font if Arial is not available

        # Initialize player and sprite groups
        # Sprite groups are containers for managing multiple sprite objects.
        # - self.all_sprites: Contains all game objects to be updated and drawn.
        # - self.enemies: Specifically for enemy objects, used for collision detection.
        # - self.bullets: Specifically for bullet objects, used for collision detection.
        # - self.obstacles: Specifically for obstacle objects, used for collision detection.
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        self.all_sprites.add(self.player) # Add player to the group of all sprites

        # Game state variables
        self.score = 0
        self.stage_number = 0 # Tracks the current stage
        self.game_over = False
        self.game_paused = False

        self.current_scroll_speed = OBSTACLE_SCROLL_SPEED_BASE # Scroll speed for current stage

        self.start_new_stage() # Begin the first stage

    def start_new_stage(self):
        """
        Initializes a new stage. This method handles procedural generation elements
        and difficulty scaling.
        """
        self.stage_number += 1 # Increment stage number

        # Clear out old sprites from previous stage
        for enemy in self.enemies: enemy.kill()
        for bullet in self.bullets: bullet.kill()
        for obs in self.obstacles: obs.kill()

        # Reset player position and ensure it's in the all_sprites group
        self.player.rect.x = 50
        self.player.rect.centery = SCREEN_HEIGHT // 2
        if not self.all_sprites.has(self.player): # Add player back if removed (e.g. after game over)
            self.all_sprites.add(self.player)

        # Procedural generation for stage duration:
        # Stage duration is randomized between 45 and 90 seconds.
        self.stage_duration_seconds = random.randint(45, 90)
        self.stage_end_time_ticks = pygame.time.get_ticks() + self.stage_duration_seconds * 1000

        # Difficulty scaling for enemy spawn rate:
        # Enemy spawn delay decreases as stage number increases, making spawns more frequent.
        # Minimum delay is capped at 200ms.
        self.enemy_spawn_delay_ms = max(200, 2000 - self.stage_number * 150)
        self.last_enemy_spawn_time_ticks = pygame.time.get_ticks() # Timer for enemy spawning

        # Difficulty scaling for enemy speed:
        # Enemy speed increases with each stage.
        self.current_enemy_speed = 2 + self.stage_number * 0.5

        # Difficulty scaling for obstacle scroll speed:
        # Obstacles scroll faster in later stages. Minimum speed is 1.
        self.current_scroll_speed = OBSTACLE_SCROLL_SPEED_BASE + (self.stage_number -1) * 0.25
        self.current_scroll_speed = max(1, self.current_scroll_speed)

        # Procedural generation for obstacles:
        # Number of obstacles increases with stage number.
        num_obstacles = 1 + self.stage_number
        for i in range(num_obstacles):
            # Obstacle dimensions are randomized.
            obs_width = random.randint(30, 120)
            obs_height = random.randint(30, SCREEN_HEIGHT * 0.6) # Height up to 60% of screen
            # Obstacle X position is staggered off-screen to the right.
            obs_x = SCREEN_WIDTH + i * (SCREEN_WIDTH / num_obstacles) + random.randint(50, 300)
            max_y = SCREEN_HEIGHT - obs_height # Ensure obstacle is fully within screen vertically
            obs_y = random.randint(0, int(max_y)) # Random Y position

            obstacle = Obstacle(obs_x, obs_y, obs_width, obs_height)
            obstacle.set_scroll_speed(self.current_scroll_speed) # Set its speed for this stage
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

    def spawn_enemy(self):
        """Spawns a new enemy with the current stage's difficulty settings."""
        enemy = Enemy(speed=self.current_enemy_speed)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

    def handle_input(self):
        """
        Processes all game inputs (keyboard events).
        Handles quitting, restarting, shooting, and pausing.
        """
        for event in pygame.event.get(): # Iterate through all pending events
            if event.type == pygame.QUIT: # If the window close button is clicked
                return False # Signal to exit the game loop

            if self.game_over:
                # If game is over, only listen for 'R' to restart
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.__init__() # Re-initialize the game object to start fresh
                    return True # Continue running the game
            else: # If game is not over
                if not self.game_paused:
                    # Handle shooting only if game is not paused
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            bullet = self.player.shoot()
                            self.all_sprites.add(bullet) # Add to all_sprites for drawing/updating
                            self.bullets.add(bullet)     # Add to bullets group for collision checks
                # Handle pausing/unpausing
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    self.game_paused = not self.game_paused
        return True # Signal to continue the game loop

    def update_game_state(self):
        """
        Updates all game logic, including sprite movements, enemy spawning,
        collision detection, and stage progression.
        This method is skipped if the game is over or paused.
        """
        if self.game_over or self.game_paused:
            return # Do nothing if game is over or paused

        current_ticks = pygame.time.get_ticks() # Get current time for timing events

        # Update obstacle scroll speed (in case it changes mid-stage, though currently set at stage start)
        for obs in self.obstacles:
            obs.set_scroll_speed(self.current_scroll_speed)

        # Update all sprites in the all_sprites group (calls their respective update() methods)
        self.all_sprites.update()

        # Enemy spawning logic based on time delay
        if current_ticks - self.last_enemy_spawn_time_ticks > self.enemy_spawn_delay_ms:
            self.spawn_enemy()
            self.last_enemy_spawn_time_ticks = current_ticks # Reset spawn timer

        # Collision detection: Player vs. Enemies
        # pygame.sprite.spritecollide(sprite, group, dokill)
        # - sprite: The player sprite.
        # - group: The enemies sprite group.
        # - dokill (True): If True, colliding enemies are removed from their groups.
        if pygame.sprite.spritecollide(self.player, self.enemies, True):
            self.game_over = True # Player hit an enemy
            return # Exit early as game is over

        # Collision detection: Player vs. Obstacles
        # dokill (False): Obstacles are not removed on collision with player.
        if pygame.sprite.spritecollide(self.player, self.obstacles, False):
            self.game_over = True # Player hit an obstacle
            return

        # Collision detection: Bullets vs. Enemies
        # pygame.sprite.groupcollide(group1, group2, dokill1, dokill2)
        # - group1: bullets group.
        # - group2: enemies group.
        # - dokill1 (True): Bullets that hit are removed.
        # - dokill2 (True): Enemies that are hit are removed.
        # Returns a dictionary {bullet_sprite: [enemy_sprites_hit_by_it]}
        enemy_hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
        for bullet, enemies_hit_list in enemy_hits.items():
            self.score += 10 * len(enemies_hit_list) # Increase score for each enemy hit

        # Stage progression: Check if stage duration has elapsed
        if current_ticks >= self.stage_end_time_ticks:
            self.start_new_stage() # Move to the next stage

    def draw_hud(self):
        """Renders and displays Head-Up Display information (score, stage, time left)."""
        # Render score
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_surf, (10, 10)) # Position at top-left

        # Render stage number
        stage_surf = self.font.render(f"Stage: {self.stage_number}", True, WHITE)
        self.screen.blit(stage_surf, (10, 40))

        # Calculate and render time left in the current stage
        if not self.game_over:
            time_left_seconds = (self.stage_end_time_ticks - pygame.time.get_ticks()) // 1000
            time_left_seconds = max(0, time_left_seconds) # Ensure time doesn't go negative
        else:
            time_left_seconds = 0 # Show 0 if game is over

        timer_surf = self.font.render(f"Time Left: {time_left_seconds}s", True, WHITE)
        self.screen.blit(timer_surf, (10, 70))

    def draw_elements(self):
        """Handles all drawing operations for the game."""
        self.screen.fill(BLACK) # Clear the screen with black
        self.all_sprites.draw(self.screen) # Draw all sprites in the all_sprites group
        self.draw_hud() # Draw the HUD elements

        # Display "GAME OVER" message if applicable
        if self.game_over:
            game_over_font = pygame.font.Font(None, 80) # Larger font for game over
            game_over_surf = game_over_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(game_over_surf, game_over_rect)

            restart_font = pygame.font.Font(None, 40) # Font for restart message
            restart_surf = restart_font.render("Press 'R' to Restart", True, WHITE)
            restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(restart_surf, restart_rect)

        # Display "PAUSED" message if applicable
        elif self.game_paused:
            pause_font = pygame.font.Font(None, 80)
            pause_surf = pause_font.render("PAUSED", True, YELLOW)
            pause_rect = pause_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_surf, pause_rect)

        pygame.display.flip() # Update the full display surface to the screen

    def run(self):
        """Main game loop."""
        running = True
        while running:
            if not self.handle_input(): # Process inputs; if it returns False, quit
                running = False
                break

            self.update_game_state() # Update game logic
            self.draw_elements()     # Draw everything to the screen

            self.clock.tick(60) # Maintain 60 frames per second

        pygame.quit() # Uninitialize Pygame modules when the loop ends

if __name__ == '__main__':
    game = Game() # Create an instance of the Game
    game.run()    # Start the game loop
