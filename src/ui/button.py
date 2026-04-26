import pygame

DEFAULT_SCALE = 1


class Button:
    blocked_rect = None

    def __init__(
        self, x, y, image, scale=DEFAULT_SCALE, hitbox_ratio=0.6, bypass_block=False
    ):
        self.bypass_block = bypass_block

        if image is not None:
            w = image.get_width()
            h = image.get_height()
            self.image = pygame.transform.scale(image, (int(w * scale), int(h * scale)))
        else:
            self.image = None

        if self.image is not None:
            iw = self.image.get_width()
            ih = self.image.get_height()
            self._inset_x = int(iw * (1 - hitbox_ratio) / 2)
            self._inset_y = int(ih * (1 - hitbox_ratio) / 2)
            self.rect = pygame.Rect(
                x + self._inset_x,
                y + self._inset_y,
                iw - self._inset_x * 2,
                ih - self._inset_y * 2,
            )
        else:
            self._inset_x = 0
            self._inset_y = 0
            self.rect = pygame.Rect(x, y, 0, 0)

        self.clicked = False

    def draw(self, surface):
        if self.image is None:
            return False

        draw_x = self.rect.x - self._inset_x
        draw_y = self.rect.y - self._inset_y
        surface.blit(self.image, (draw_x, draw_y))

        action = False
        pos = pygame.mouse.get_pos()

        if (
            not self.bypass_block
            and Button.blocked_rect is not None
            and Button.blocked_rect.collidepoint(pos)
        ):
            self.clicked = False
            return False

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]:
                if not self.clicked:
                    self.clicked = True
            else:
                if self.clicked:
                    self.clicked = False
                    action = True
        else:
            if not pygame.mouse.get_pressed()[0]:
                self.clicked = False

        return action
