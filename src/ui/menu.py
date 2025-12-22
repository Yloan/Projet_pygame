import pygame
import button

pygame.init()

#Taille de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Main Menu")

#game variables
game_started = False
menu_state = "main"
number_players = 0

#define front
font = pygame.font.SysFont("arialblack", 40)

#define colors
TEXT_COL = (255, 255, 255)
TEXT_COL2 = (255, 0, 0)

wallpaper = pygame.image.load("assets/wallpapers/wallpaper.png").convert_alpha()

#load button mages
play_img = pygame.image.load("assets/buttons/button_play.png").convert_alpha()
settings_img = pygame.image.load("assets/buttons/button_settings.png").convert_alpha()
exit_img = pygame.image.load("assets/buttons/button_exit.png").convert_alpha()
video_img = pygame.image.load("assets/buttons/button_video.png").convert_alpha()
audio_img = pygame.image.load("assets/buttons/button_audio.png").convert_alpha()
keys_img = pygame.image.load("assets/buttons/button_keys.png").convert_alpha()
back_img = pygame.image.load("assets/buttons/button_back.png").convert_alpha()
one_player_img = pygame.image.load("assets/buttons/button_one_player.png").convert_alpha()
two_players_img = pygame.image.load("assets/buttons/button_two_players.png").convert_alpha()
three_players_img = pygame.image.load("assets/buttons/button_trhee_players.png").convert_alpha()
four_players_img = pygame.image.load("assets/buttons/button_four_players.png").convert_alpha()


#create button instances
play_button = button.Button(300, 100, play_img, 1)
settings_button = button.Button(300, 225, settings_img, 1)
exit_button = button.Button(300, 350, exit_img, 1)
video_button = button.Button(226, 75, video_img, 1)
audio_button = button.Button(225, 200, audio_img, 1)
keys_button = button.Button(246, 325, keys_img, 1)
back_button = button.Button(332, 450, back_img, 1)
one_player_button = button.Button(250, 125, one_player_img, 1)
two_players_button = button.Button(450, 125, two_players_img, 1)
three_players_button = button.Button(250, 300, three_players_img, 1)
four_players_button = button.Button(450, 300, four_players_img, 1)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#game loop
run = True
while run :
    screen.blit(wallpaper, (0, 0))

    if game_started == True:
        #check menu states
        if menu_state == "main":
            #draw pause screen buttons
            if play_button.draw(screen):
                menu_state = "play"
            if settings_button.draw(screen):
                menu_state = "settings"
            if exit_button.draw(screen):
                run = False
            #check settings menu
        if menu_state == "settings":
            #draw options menu
            if video_button.draw(screen):
                print("Video Settings")
            if audio_button.draw(screen):
                print("Audio Settings")
            if keys_button.draw(screen):
                print("Keys Settings")
            if back_button.draw(screen):
                menu_state = "main"
        if menu_state == "play":
            draw_text("Select the number of players", font, TEXT_COL2, 100, 50)
            if one_player_button.draw(screen):
                menu_state == "one_player"
                number_players = 1
            if two_players_button.draw(screen):
                menu_state == "two_player"
                number_players = 2
            if three_players_button.draw(screen):
                menu_state == "three_player"
                number_players = 3
            if four_players_button.draw(screen):
                menu_state == "four_player"
                number_players = 4
            if back_button.draw(screen):
                menu_state = "main"
    else:
        draw_text("Press Space to start", font, TEXT_COL, 160, 250)

#event handler
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_started = True
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()