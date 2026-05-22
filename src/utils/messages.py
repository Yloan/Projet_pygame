import pygame as pyg


class Message:
    def __init__(self, message, surface, speed, max_width, max_height):
        self.message = message
        self.surface = surface
        self.speed = speed
        self.max_width = max_width

        self.dimensions_bg_rec = [0, max_height]
        self.display_text = False

        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

    def get_dim_center_xy(self):
        return (
            self.width // 2 - self.dimensions_bg_rec[0] // 2,
            self.height // 2 - self.dimensions_bg_rec[1] // 2,
        )

    def draw_text_center(self):
        font = pyg.font.Font(None, 25)
        text = font.render(self.message, True, (0, 0, 0))
        text_rect = text.get_rect()

        text_rect.center = (self.width // 2, self.height // 2)
        self.surface.blit(text, text_rect)

    def draw(self):
        x, y = self.get_dim_center_xy()
        pyg.draw.rect(
            self.surface,
            (128, 128, 128),
            (x, y, self.dimensions_bg_rec[0], self.dimensions_bg_rec[1]),
        )

        if self.display_text:
            self.draw_text_center()

    def update_animation(self):
        if (
            self.dimensions_bg_rec[0] >= self.max_width
        ):  # Ca peut le depasser si speed est > 1
            self.dimensions_bg_rec[0] = self.max_width
            self.display_text = True
        else:
            self.dimensions_bg_rec[0] += self.speed
