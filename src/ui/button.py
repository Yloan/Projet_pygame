import pygame


DEFAULT_SCALE = 1


class Button:
    def __init__(self, x, y, image, scale=DEFAULT_SCALE):
        if image is not None:
            width = image.get_width()
            height = image.get_height()
            self.image = pygame.transform.scale(
                image, 
                (int(width * scale), int(height * scale))
            )
        else:
            self.image = None

        if self.image is not None:
            self.rect = self.image.get_rect(topleft=(x, y))
        else:
            self.rect = pygame.Rect(x, y, 0, 0)
        self.clicked = False

    def draw(self, surface):
        if self.image is None:
            return False
        action = False
        pos = pygame.mouse.get_pos()
        surface.blit(self.image, (self.rect.x, self.rect.y))
        # Check if mouse is over button
        if self.rect.collidepoint(pos):
            # Check if mouse button is pressed
            if pygame.mouse.get_pressed()[0]:
                # If not already clicked, set clicked flag
                if not self.clicked:
                    self.clicked = True
            else:
                # Mouse button released
                # If was clicked before, register action on release
                if self.clicked:
                    self.clicked = False
                    action = True
        else:
            # Mouse moved outside button
            # Reset clicked state if button is released
            if not pygame.mouse.get_pressed()[0]:
                self.clicked = False

        return action
