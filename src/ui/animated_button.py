import pygame


DEFAULT_SCALE = 1
DEFAULT_ANIMATION_SPEED = 1  # frames per second


class AnimatedButton:
    
    def __init__(self, x, y, frames, scale=DEFAULT_SCALE, animation_speed=DEFAULT_ANIMATION_SPEED):
        self.frames = []
        self.scale = scale
        for frame in frames:
            width = frame.get_width()
            height = frame.get_height()
            scaled_frame = pygame.transform.scale(
                frame, 
                (int(width * scale), int(height * scale))
            )
            self.frames.append(scaled_frame)
        self.current_frame = 0
        self.animation_speed = max(1, animation_speed)
        self.animation_counter = 0
        if self.frames:
            self.rect = self.frames[0].get_rect(topleft=(x, y))
        else:
            self.rect = pygame.Rect(x, y, 0, 0)
        self.clicked = False

    def update(self):
        if not self.frames:
            return
        self.animation_counter += 1
        if self.animation_counter >= 60 // self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, surface):
        action = False
        
        # UPDATE ANIMATION
        self.update()
        if not self.frames:
            return False
        pos = pygame.mouse.get_pos()
        # DRAW BUTTON
        current_image = self.frames[self.current_frame]
        surface.blit(current_image, (self.rect.x, self.rect.y))
        # CLICK DETECTION LOGIC
        # Check if mouse is over button
        if self.rect.collidepoint(pos):
            # Get current mouse button state
            if pygame.mouse.get_pressed()[0] == 1:  # Left mouse button pressed
                if not self.clicked:
                    self.clicked = True
            else:
                # Mouse button released
                if self.clicked:
                    action = True  # Register click
                    self.clicked = False
        else:
            # Mouse left button area
            self.clicked = False

        return action

    def presse(self):
        pass