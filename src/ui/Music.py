import pygame

class MusicPlayer:
    def __init__(self, file):
        pygame.mixer.init()
        self.file = file
        pygame.mixer.music.load(self.file)

    def play(self, loop=-1):
        pygame.mixer.music.play(loop)

    def stop(self):
        pygame.mixer.music.stop()

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()
