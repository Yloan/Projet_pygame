import pygame
import button
from src.main import *
import src.main as game

pygame.init()


screen = pygame.display.set_mode((game.width, game.height))
pygame.display.set_caption("Main Menu")

# game variables
game_started = False
menu_state = "main"
number_players = 0
number_bot = 0

# define font
font = pygame.font.SysFont("arialblack", 40)

# define colors
TEXT_COL = (255, 255, 255)
TEXT_COL2 = (255, 0, 0)

wallpaper = pygame.image.load("assets/wallpapers/wallpaper.png").convert_alpha()
choice_chracters = pygame.image.load("assets/wallpapers/choice_chracters.png").convert_alpha()

# load button images
play_img = pygame.image.load("assets/buttons/button_play.png").convert_alpha()
settings_img = pygame.image.load("assets/buttons/button_settings.png").convert_alpha()
exit_img = pygame.image.load("assets/buttons/button_exit.png").convert_alpha()
video_img = pygame.image.load("assets/buttons/button_video.png").convert_alpha()
audio_img = pygame.image.load("assets/buttons/button_audio.png").convert_alpha()
keys_img = pygame.image.load("assets/buttons/button_keys.png").convert_alpha()
back_img = pygame.image.load("assets/buttons/button_back.png").convert_alpha()
zero_player_img = pygame.image.load("assets/buttons/button_zero_player.png").convert_alpha()
one_player_img = pygame.image.load("assets/buttons/button_one_player.png").convert_alpha()
two_players_img = pygame.image.load("assets/buttons/button_two_players.png").convert_alpha()
three_players_img = pygame.image.load("assets/buttons/button_trhee_players.png").convert_alpha()
four_players_img = pygame.image.load("assets/buttons/button_four_players.png").convert_alpha()


# create button instances
play_button = button.Button(300, 100, play_img, 1)
settings_button = button.Button(300, 225, settings_img, 1)
exit_button = button.Button(300, 350, exit_img, 1)
video_button = button.Button(226, 75, video_img, 1)
audio_button = button.Button(225, 200, audio_img, 1)
keys_button = button.Button(246, 325, keys_img, 1)
back_button = button.Button(332, 450, back_img, 1)
zero_player_button = button.Button(450, 300, zero_player_img, 0.3)
one_player_button = button.Button(250, 125, one_player_img, 1)
two_players_button = button.Button(450, 125, two_players_img, 1)
three_players_button = button.Button(250, 300, three_players_img, 1)
four_players_button = button.Button(450, 300, four_players_img, 1)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# game loop
run = True
while run:
    screen.blit(wallpaper, (0, 0))

    if game_started:
        # main menu
        if menu_state == "main":
            if play_button.draw(screen):
                menu_state = "play"
            if settings_button.draw(screen):
                menu_state = "settings"
            if exit_button.draw(screen):
                run = False

        # settings menu
        elif menu_state == "settings":
            if video_button.draw(screen):
                print("Video Settings")
            if audio_button.draw(screen):
                print("Audio Settings")
            if keys_button.draw(screen):
                print("Keys Settings")
            if back_button.draw(screen):
                menu_state = "main"

        # play -> choose number of players
        elif menu_state == "play":
            draw_text("Select the number of players", font, TEXT_COL2, 100, 50)
            if one_player_button.draw(screen):
                menu_state = "one_player"
                number_players = 1
            if two_players_button.draw(screen):
                menu_state = "two_players"
                number_players = 2
            if three_players_button.draw(screen):
                menu_state = "three_players"
                number_players = 3
            if four_players_button.draw(screen):
                menu_state = "choice_characters"
                number_players = 4
            if back_button.draw(screen):
                menu_state = "main"

        # one player -> choose number of bots
        elif menu_state == "one_player":
            draw_text("Select the number of bots", font, TEXT_COL2, 100, 50)
            if zero_player_button.draw(screen):
                menu_state = "choice_characters"
                number_bot = 0
            if one_player_button.draw(screen):
                menu_state = "choice_characters"
                number_bot = 1
            if two_players_button.draw(screen):
                menu_state = "choice_characters"
                number_bot = 2
            if three_players_button.draw(screen):
                menu_state = "choice_characters"
                number_bot = 3
            if back_button.draw(screen):
                menu_state = "play"

        # two players -> choose number of bots (example)
        elif menu_state == "two_players":
            draw_text("Select the number of bots", font, TEXT_COL2, 100, 50)
            if zero_player_button.draw(screen):
                menu_state = "choice_characters"
                number_bot = 0
            if one_player_button.draw(screen):
                menu_state = "choice_characters"
                number_bot = 1
            if two_players_button.draw(screen):
                menu_state = "choice_characters"
                number_bot = 2
            if back_button.draw(screen):
                menu_state = "play"

        # three_players / four_players can be handled similarly if needed
        elif menu_state == "three_players":
            draw_text("Select the number of bots", font, TEXT_COL2, 100, 50)
            if zero_player_button.draw(screen):
                menu_state = "choice_characters"
                number_bot = 0
            if one_player_button.draw(screen):
                menu_state = "choice_characters"
                number_bot = 1
            if back_button.draw(screen):
                menu_state = "play"

        elif menu_state == "choice_characters":
            screen.blit(choice_chracters, (0, 0))
            draw_text("Choice characters", font, TEXT_COL, 200, 0)
            if back_button.draw(screen):
                menu_state = "play"

    else:
        draw_text("Press Space to start", font, TEXT_COL, 160, 250)

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_started = True
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()