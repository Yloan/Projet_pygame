import pygame as pyg

from ui import Buttons as ObjButton
from ui import animated_button


class InGameMenu:
    """Pause overlay shown when the player presses Escape.

    Instead of a full-screen dark overlay (which turns black on dark maps),
    only the area around the buttons gets a dark panel so the game remains
    clearly visible in the background.

    Returns from draw():
        'resume'  — player clicked Resume
        'quit'    — player clicked Quit (caller should call _reset_to_menu)
        None      — still paused, no action yet
    """

    def __init__(self, screen_w: int, screen_h: int):
        self._w = screen_w
        self._h = screen_h

        # Load button frame sets
        play_obj  = ObjButton.PlayButton()
        exit_obj  = ObjButton.ExitButton()

        scale = 2

        frame_w = play_obj.play_button_frames[0].get_width() * scale
        cx = screen_w // 2
        btn_x = cx - frame_w // 2

        y_resume = 290
        y_quit   = 430

        self._btn_resume = animated_button.AnimatedButton(
            btn_x, y_resume,
            frames_idle=play_obj.play_button_frames,
            frames_pressed=play_obj.play_button_frames_pressed,
            frames_unpressed=play_obj.play_button_frames_unpressed,
            scale=scale,
        )
        self._btn_quit = animated_button.AnimatedButton(
            btn_x, y_quit,
            frames_idle=exit_obj.exit_button_frames,
            frames_pressed=exit_obj.exit_button_frames_pressed,
            frames_unpressed=[],  # EXIT fires immediately on mouse-up
            scale=scale,
        )

        # Dark panel only around the buttons — keeps game visible in background
        frame_h = play_obj.play_button_frames[0].get_height() * scale
        pad_x, pad_y = 60, 40
        panel_w = frame_w + pad_x * 2
        panel_h = (y_quit - y_resume) + frame_h + pad_y * 2
        panel_x = cx - panel_w // 2
        panel_y = y_resume - pad_y

        self._panel = pyg.Surface((panel_w, panel_h), pyg.SRCALPHA)
        self._panel.fill((0, 0, 0, 180))
        self._panel_pos = (panel_x, panel_y)

    def draw(self, screen: pyg.Surface):
        """Draw the panel + buttons.  Returns 'resume', 'quit', or None."""
        screen.blit(self._panel, self._panel_pos)

        if self._btn_resume.draw(screen):
            return "resume"

        if self._btn_quit.draw(screen):
            return "quit"

        return None
