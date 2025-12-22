# exemple d'implémentation dans button.py
import pygame

class Button:
    def __init__(self, x, y, image, scale=1):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        # dessine le bouton
        surface.blit(self.image, (self.rect.x, self.rect.y))

        # si souris sur le bouton
        if self.rect.collidepoint(pos):
            # si on appuie et que ce n'était pas déjà en "clicked", on mémorise l'appui
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
            # si on relâche et que self.clicked était True -> click effectif
            if not pygame.mouse.get_pressed()[0] and self.clicked:
                self.clicked = False
                action = True
        else:
            # si on sort du bouton sans relâcher, on réinitialise l'état
            if not pygame.mouse.get_pressed()[0]:
                self.clicked = False

        return action