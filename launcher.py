import os
import sys
import shutil
import threading
import urllib.request
import zipfile

GITHUB_ZIP = "https://github.com/Yloan/Projet_pygame/archive/refs/heads/main.zip"
REPO_FOLDER = "Projet_pygame-main"

if sys.platform == "darwin":
    BASE_DIR = os.path.expanduser("~/Library/Application Support/BLITZKRIEG")
elif sys.platform == "win32":
    BASE_DIR = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "BLITZKRIEG"
    )
else:
    BASE_DIR = os.path.expanduser("~/.blitzkrieg")

INSTALL_DIR = os.path.join(BASE_DIR, REPO_FOLDER)
SRC_DIR = os.path.join(INSTALL_DIR, "src")


def is_installed():
    return os.path.isdir(os.path.join(INSTALL_DIR, "assets")) and \
           os.path.isfile(os.path.join(SRC_DIR, "main.py"))


def download_game(progress_cb=None):
    os.makedirs(BASE_DIR, exist_ok=True)
    zip_path = os.path.join(BASE_DIR, "_blitzkrieg.zip")

    def reporthook(block_num, block_size, total_size):
        if progress_cb and total_size > 0:
            progress_cb(min(block_num * block_size, total_size), total_size)

    urllib.request.urlretrieve(GITHUB_ZIP, zip_path, reporthook=reporthook)

    if progress_cb:
        progress_cb(-1, -1)

    if os.path.exists(INSTALL_DIR):
        shutil.rmtree(INSTALL_DIR)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(BASE_DIR)

    os.remove(zip_path)


def launch_game():
    import runpy
    sys._MEIPASS = INSTALL_DIR
    if SRC_DIR not in sys.path:
        sys.path.insert(0, SRC_DIR)
    runpy.run_path(os.path.join(SRC_DIR, "main.py"), run_name="__main__")


def run_with_splash():
    import pygame

    pygame.init()

    W, H = 500, 220
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("BLITZKRIEG — Installation")

    font_title = pygame.font.SysFont("Arial", 26, bold=True)
    font_info = pygame.font.SysFont("Arial", 15)

    progress = [0.0]
    status = ["Connexion au serveur..."]
    done = [False]
    error = [None]

    BG      = (18, 18, 28)
    BAR_BG  = (45, 45, 65)
    BAR_FG  = (72, 199, 142)
    WHITE   = (240, 240, 255)
    GRAY    = (160, 160, 180)
    RED     = (255, 90, 90)

    def progress_cb(downloaded, total):
        if downloaded == -1:
            status[0] = "Extraction des fichiers..."
            progress[0] = 0.98
        elif total > 0:
            ratio = downloaded / total
            progress[0] = min(ratio, 1.0)
            status[0] = (
                f"Téléchargement...  "
                f"{downloaded / 1048576:.1f} Mo / {total / 1048576:.1f} Mo"
            )

    def worker():
        try:
            download_game(progress_cb)
            progress[0] = 1.0
            status[0] = "Lancement du jeu..."
            done[0] = True
        except Exception as exc:
            error[0] = str(exc)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BG)

        title_surf = font_title.render("BLITZKRIEG", True, WHITE)
        screen.blit(title_surf, ((W - title_surf.get_width()) // 2, 32))

        if error[0]:
            err_surf = font_info.render(f"Erreur : {error[0]}", True, RED)
            screen.blit(err_surf, ((W - err_surf.get_width()) // 2, 100))
            note = font_info.render("Ferme cette fenêtre et réessaie.", True, GRAY)
            screen.blit(note, ((W - note.get_width()) // 2, 125))
        else:
            info_surf = font_info.render(status[0], True, GRAY)
            screen.blit(info_surf, ((W - info_surf.get_width()) // 2, 100))

            bx, by, bw, bh = 40, 145, W - 80, 18
            pygame.draw.rect(screen, BAR_BG, (bx, by, bw, bh), border_radius=5)
            fill = int(bw * progress[0])
            if fill > 0:
                pygame.draw.rect(screen, BAR_FG, (bx, by, fill, bh), border_radius=5)

            pct = font_info.render(f"{int(progress[0] * 100)} %", True, GRAY)
            screen.blit(pct, ((W - pct.get_width()) // 2, 172))

        pygame.display.flip()
        clock.tick(30)

        if done[0]:
            thread.join()
            pygame.quit()
            return

        if error[0]:
            pygame.time.wait(4000)
            pygame.quit()
            sys.exit(1)


if __name__ == "__main__":
    if not is_installed():
        run_with_splash()
    launch_game()
