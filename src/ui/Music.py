import pygame


class MusicPlayer:
    def __init__(self, file):
        self.file = file

    def play(self, loop=-1):
        pygame.mixer.music.load(self.file)
        pygame.mixer.music.play(loop)

    def volume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def stop(self):
        pygame.mixer.music.stop()

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()
