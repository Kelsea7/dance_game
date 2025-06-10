# menu.py — wybór gracza, poprawiony SETTINGS, nie używa DIFFICULTY_SETTINGS
import pygame
import sys
import os
import json
import datetime
from dance_game import run_game, is_pressed, is_start, is_select

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont("dejavusans", 30)
small_font = pygame.font.SysFont("dejavusans", 24)
smallest_font = pygame.font.SysFont("dejavusans", 20)

HIGHLIGHT = (60, 60, 60)
DARK_GRAY = (40, 40, 40)
WHITE = (255, 255, 255)
BLUE = (0, 128, 255)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 51, 51)
ORANGE = (255, 128, 0)

emoji_images = {
    "music": pygame.image.load("assets/emojis/1f3b5.png").convert_alpha(),
    "game": pygame.image.load("assets/emojis/1f3ae.png").convert_alpha(),
    "missed": pygame.image.load("assets/emojis/274c.png").convert_alpha(),
    "gold_cup": pygame.image.load("assets/emojis/1f3c6.png").convert_alpha(),
    "timer": pygame.image.load("assets/emojis/23f0.png").convert_alpha(),
    "target": pygame.image.load("assets/emojis/1f3af.png").convert_alpha()
}

menu_options = ["CHOOSE SONG", "SETTINGS", "SCORES", "CREDITS", "EXIT"]
SETTINGS_FILE = "settings.json"
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)
        players = settings.get("players", ["PLAYER"])
        selected_player = settings.get("selected_player", 0) % len(players)
else:
    players = ["PLAYER"]
    selected_player = 0

selected_index = 0
songs = sorted([f for f in os.listdir("songs") if f.endswith(".ogg") or f.endswith(".mp3") or f.endswith(".wav")])
if not songs:
    songs = ["no_music.wav"]
difficulties = ["easy", "medium", "hard", "nightmare"]
selected_song = 0
selected_difficulty = 0

clock = pygame.time.Clock()

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

arrow_modes = ["random", "predefined"]
selected_arrow_mode = 0

def show_choose_song():
    global selected_song, selected_difficulty, selected_arrow_mode, selected_player, players
    step = 0  # 0: PLAYER, 1: SONG, 2: DIFFICULTY, 3: ARROW MODE, 4: START, 5: BACK
    running = True
    while running:
        clock.tick(30)
        screen.fill(DARK_GRAY)
        song_title = os.path.splitext(songs[selected_song])[0]
        predefined_exists = os.path.exists(os.path.join("songs", f"{song_title}_map.json"))

        # --- WYBÓR GRACZA ---
        player_y = 100
        if step == 0:
            pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(50, player_y, SCREEN_WIDTH - 100, 28))

        middle_x = SCREEN_WIDTH // 2
        prev_name = players[(selected_player - 1) % len(players)]
        curr_name = players[selected_player]
        next_name = players[(selected_player + 1) % len(players)]

        # Lewy
        text = smallest_font.render(prev_name, True, WHITE)
        screen.blit(text, (middle_x - 200 - text.get_width() // 2, player_y))
        # Aktywny
        text = smallest_font.render(curr_name, True, GREEN)
        screen.blit(text, (middle_x - text.get_width() // 2, player_y))
        pygame.draw.line(screen, GREEN,
            (middle_x - text.get_width() // 2, player_y + 22),
            (middle_x + text.get_width() // 2, player_y + 22), 2)
        # Prawy
        text = smallest_font.render(next_name, True, WHITE)
        screen.blit(text, (middle_x + 200 - text.get_width() // 2, player_y))

        # Tytuły
        song_label = small_font.render("SONG:", True, WHITE)
        diff_label = small_font.render("DIFFICULTY:", True, WHITE)
        screen.blit(song_label, (60, 150))
        screen.blit(diff_label, (60, 270))

        # Piosenka (mniejsza czcionka, zawijanie)
        song_lines = wrap_text(songs[selected_song], smallest_font, SCREEN_WIDTH - 120)
        bg_height = len(song_lines) * 22
        if step == 1:
            pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(50, 180, SCREEN_WIDTH - 100, bg_height))
        for i, line in enumerate(song_lines):
            bg_rect = pygame.Rect(50, 180 + i * 22, SCREEN_WIDTH - 100, 22)
            line_surface = smallest_font.render(line, True, GREEN if step == 1 else WHITE)
            screen.blit(line_surface, (60, 180 + i * 22))

        # Poziomy trudności poziomo (mniejsza czcionka)
        x_start = 60
        if step == 2:
            pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(50, 320, SCREEN_WIDTH - 100, 28))
        for i, diff in enumerate(difficulties):
            color = GREEN if i == selected_difficulty else WHITE
            text = smallest_font.render(diff, True, color)
            screen.blit(text, (x_start, 320))
            if i == selected_difficulty:
                pygame.draw.line(screen, color, (x_start, 320 + text.get_height()), (x_start + text.get_width(), 320 + text.get_height()), 2)
            x_start += text.get_width() + 30

        # Arrow mode
        mode_label = small_font.render("ARROWS:", True, WHITE)
        screen.blit(mode_label, (60, 390))
        if step == 3:
            pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(50, 420, SCREEN_WIDTH - 100, 28))

        x_start = 200
        for i, mode in enumerate(arrow_modes):
            if mode == "predefined" and not predefined_exists:
                continue
            color = GREEN if i == selected_arrow_mode else WHITE
            text = smallest_font.render(mode, True, color)
            screen.blit(text, (x_start, 420))
            if i == selected_arrow_mode:
                pygame.draw.line(screen, color, (x_start, 420 + text.get_height()), (x_start + text.get_width(), 420 + text.get_height()), 2)
            x_start += text.get_width() + 30

        # START
        start_color = GREEN if step == 4 else WHITE
        start_text = small_font.render(("▶ " if step == 4 else "   ") + "START", True, start_color)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 480))

        # BACK
        back_color = GREEN if step == 5 else WHITE
        back_text = small_font.render(("▶ " if step == 5 else "   ") + "BACK", True, back_color)
        screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 520))

        try:
            song_path = os.path.join("songs", songs[selected_song])
            duration = pygame.mixer.Sound(song_path).get_length()
            mins = int(duration) // 60
            secs = int(duration) % 60
            time_text = f"{mins}:{secs:02d}"
            dur_surface = smallest_font.render(f"Time: {time_text}", True, CYAN)
            screen.blit(dur_surface, (SCREEN_WIDTH - 120, 150))  # po prawej, obok SONG
        except:
            pass

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or is_select(event):
                return
            elif is_pressed(event, "up"):
                step = (step - 1) % 6
            elif is_pressed(event, "down"):
                step = (step + 1) % 6
            elif is_pressed(event, "left"):
                if step == 0:
                    selected_player = (selected_player - 1) % len(players)
                elif step == 1:
                    selected_song = (selected_song - 1) % len(songs)
                elif step == 2:
                    selected_difficulty = (selected_difficulty - 1) % len(difficulties)
                elif step == 3:
                    selected_arrow_mode = (selected_arrow_mode - 1) % len(arrow_modes)
                    if arrow_modes[selected_arrow_mode] == "predefined" and not predefined_exists:
                        selected_arrow_mode = 0
            elif is_pressed(event, "right"):
                if step == 0:
                    selected_player = (selected_player + 1) % len(players)
                elif step == 1:
                    selected_song = (selected_song + 1) % len(songs)
                elif step == 2:
                    selected_difficulty = (selected_difficulty + 1) % len(difficulties)
                elif step == 3:
                    selected_arrow_mode = (selected_arrow_mode + 1) % len(arrow_modes)
                    if arrow_modes[selected_arrow_mode] == "predefined" and not predefined_exists:
                        selected_arrow_mode = 0
            elif is_start(event):
                if step == 4:
                    try:
                        song_path = os.path.join("songs", songs[selected_song])
                        difficulty = difficulties[selected_difficulty].upper()  
                        player_name = players[selected_player]
                        arrow_mode = arrow_modes[selected_arrow_mode]
                        song_title = os.path.splitext(os.path.basename(song_path))[0]
                        map_file = f"songs/{song_title}_map.json" if arrow_mode == "predefined" else None

                        # zapisz wybranego gracza do settings
                        settings["selected_player"] = selected_player
                        with open(SETTINGS_FILE, "w") as f:
                            json.dump(settings, f, indent=2)

                        run_game(song_path=song_path, difficulty=difficulty, player_name=player_name, arrow_mode=arrow_mode, map_file=map_file)
                    except Exception as e:
                        import traceback
                        print("Błąd podczas uruchamiania gry:")
                        traceback.print_exc()
                        err_msg = small_font.render("Nie udało się uruchomić gry", True, (255, 0, 0))
                        screen.blit(err_msg, (SCREEN_WIDTH // 2 - err_msg.get_width() // 2, 500))
                        pygame.display.flip()
                        pygame.time.delay(2000)
                        return
                elif step == 5:
                    return  # BACK → powrót do MAIN MENU

def draw_menu():
    screen.fill(DARK_GRAY)
    title = font.render("MAIN MENU", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    for i, option in enumerate(menu_options):
        prefix = "▶ " if i == selected_index else "   "
        color = GREEN if i == selected_index else WHITE
        label = font.render(prefix + option, True, color)
        screen.blit(label, (SCREEN_WIDTH // 2 - 120, 200 + i * 50))

    pygame.display.flip()

def menu_loop():
    global selected_index
    while True:
        clock.tick(30)
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or is_select(event):
                pygame.quit()
                sys.exit()
            if is_pressed(event, "up"):
                selected_index = (selected_index - 1) % len(menu_options)
            elif is_pressed(event, "down"):
                selected_index = (selected_index + 1) % len(menu_options)
            elif is_start(event):
                option = menu_options[selected_index]
                if option == "CHOOSE SONG":
                    show_choose_song()
                elif option == "SETTINGS":
                    show_settings()
                elif option == "SCORES":
                    show_scores()
                elif option == "CREDITS":
                    show_credits()
                elif option == "EXIT":
                    pygame.quit()
                    sys.exit()

def show_settings():
    global players, settings
    settings_path = SETTINGS_FILE
    if os.path.exists(settings_path):
        with open(settings_path, "r") as f:
            settings = json.load(f)
    else:
        settings = {
            "auto_clean_scores": False,
            "players": ["PLAYER1", "PLAYER2", "PLAYER3", "PLAYER4", "PLAYER5"]
        }

    players = settings.get("players", ["PLAYER"])
    clean_scores = settings.get("auto_clean_scores", False)
    selected_index = 0
    editing_name = False
    char_index = 0
    max_len = 7
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789.+-_ ")
    total_options = len(players) + 2  # players + auto-clean toggle + BACK
    clock = pygame.time.Clock()

    while True:
        clock.tick(30)
        screen.fill(DARK_GRAY)
        title = font.render("SETTINGS", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))
        screen.blit(small_font.render("Player names:", True, WHITE), (60, 120))
        max_len = 7  # limit znaków
        for i, name in enumerate(players):
            y = 160 + i * 40
            is_active = selected_index == i
            if is_active:
                pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(50, y, SCREEN_WIDTH - 100, 30))

            if editing_name and is_active:
                display = list(name.ljust(max_len))
                for j, ch in enumerate(display):
                    color = GREEN
                    surf = small_font.render(ch, True, color)
                    x = 60 + j * 20
                    screen.blit(surf, (x, y))
                    if j == char_index:
                        pygame.draw.line(screen, CYAN, (x, y + 30), (x + surf.get_width(), y + 30), 2)

                # SAVE button
                save_color = GREEN if char_index == max_len else WHITE
                save_text = "SAVE"
                save_x = 60 + max_len * 20 + 30
                save_surf = small_font.render(save_text, True, save_color)
                screen.blit(save_surf, (save_x, y))
                if char_index == max_len:
                    pygame.draw.line(screen, CYAN, (save_x, y + 30), (save_x + save_surf.get_width(), y + 30), 2)
            else:
                text = ("▶ " if is_active else "   ") + name
                screen.blit(small_font.render(text, True, GREEN if is_active else WHITE), (60, y))

        # toggle auto clean
        toggle_y = 160 + len(players) * 40 + 20
        toggle_lines = [
            "[X] deletes oldest entries in Scores",
            "     (for each difficulty) if more than 18 records"
        ]
        is_active = selected_index == len(players)
        for j, line in enumerate(toggle_lines):
            y = toggle_y + j * 24
            if is_active:
                pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(50, y, SCREEN_WIDTH - 100, 28))
            screen.blit(smallest_font.render(line, True, GREEN if is_active else WHITE), (60, y))

        # BACK
        back_y = toggle_y + 60
        is_active = selected_index == len(players) + 1
        if is_active:
            pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(50, back_y, SCREEN_WIDTH - 100, 30))
        text = ("▶ " if is_active else "   ") + "BACK"
        screen.blit(small_font.render(text, True, GREEN if is_active else WHITE), (60, back_y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or is_select(event):
                return

            if editing_name:
                if is_pressed(event, "up"):
                    ch = players[selected_index][char_index] if char_index < len(players[selected_index]) else "A"
                    if ch not in alphabet:
                        ch = "A"
                    idx = (alphabet.index(ch) + 1) % len(alphabet)
                    updated = list(players[selected_index].ljust(max_len))
                    updated[char_index] = alphabet[idx]
                    players[selected_index] = "".join(updated).strip()
                elif is_pressed(event, "down"):
                    ch = players[selected_index][char_index] if char_index < len(players[selected_index]) else "A"
                    if ch not in alphabet:
                        ch = "A"
                    idx = (alphabet.index(ch) - 1) % len(alphabet)
                    updated = list(players[selected_index].ljust(max_len))
                    updated[char_index] = alphabet[idx]
                    players[selected_index] = "".join(updated).strip()
                elif is_pressed(event, "left"):
                    char_index = (char_index - 1) % (max_len + 1)
                elif is_pressed(event, "right"):
                    char_index = (char_index + 1) % (max_len + 1)
                elif is_start(event):
                    if char_index == max_len:
                        editing_name = False
                        settings["players"] = players
                        with open(SETTINGS_FILE, "w") as f:
                            json.dump(settings, f, indent=2)
            else:
                if is_pressed(event, "up"):
                    selected_index = (selected_index - 1) % total_options
                elif is_pressed(event, "down"):
                    selected_index = (selected_index + 1) % total_options
                elif is_start(event):
                    if selected_index < len(players):
                        editing_name = True
                        char_index = 0
                    elif selected_index == len(players):
                        clean_scores = not clean_scores
                        settings["auto_clean_scores"] = clean_scores
                        with open(SETTINGS_FILE, "w") as f:
                            json.dump(settings, f, indent=2)
                    elif selected_index == len(players) + 1:
                        return


##### SCORES #####
def show_scores():
    difficulties = ["BACK", "easy", "medium", "hard", "nightmare"]
    selected_difficulty = 1  # ZACZNIJ od "easy" zamiast BACK
    selected_score_index = 0
    viewing_detail = False
    VISIBLE_ENTRIES = 18
    scroll_offset = 0


    if os.path.exists("scores.json"):
        with open("scores.json", "r") as f:
            all_scores = json.load(f)
    else:
        all_scores = []

    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(30)
        screen.fill(DARK_GRAY)
        current_diff = difficulties[selected_difficulty]
        filtered = [s for s in all_scores if s.get("difficulty", "").upper() == current_diff.upper()]
        filtered = sorted(filtered, key=lambda x: x["time"], reverse=True)
        entries = [{"dummy": True}] + filtered

        # znajdź najlepszy wynik
        best_score_index = -1
        if filtered:
            best_score_value = max(s["score"] for s in filtered)
            for i, entry in enumerate(filtered):
                if entry["score"] == best_score_value:
                    best_score_index = i + 1  # +1 bo entries[0] to dummy
                    break

        if not viewing_detail:
            title = small_font.render("SCORES — Select difficulty", True, WHITE)
            screen.blit(title, (60, 60))
            
            # poziomy difficulty (bez BACK)
            x_pos = 60
            for i, diff in enumerate(difficulties[1:]):  # pomijamy "BACK"
                index = i + 1
                is_selected = selected_difficulty == index
                color = GREEN if is_selected else WHITE
                text = smallest_font.render(diff, True, color)
                if is_selected:
                    pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(x_pos - 5, 95, text.get_width() + 10, 30))
                screen.blit(text, (x_pos, 100))
                x_pos += text.get_width() + 30

            # BACK jako osobny wiersz poniżej
            is_back_selected = selected_difficulty == 0
            prefix = "▶ " if is_back_selected else "   "
            back_color = GREEN if is_back_selected else WHITE
            back_text = small_font.render(prefix + "BACK", True, back_color)
            screen.blit(back_text, (60, 150))

            # Licznik zaznaczonego wyniku (np. 2/32), tylko jeśli difficulty != BACK
            if selected_difficulty != 0 and len(entries) > 1:
                current = max(1, selected_score_index)  # nie pokazuj dummy jako 0
                total = len(entries) - 1
                counter_text = smallest_font.render(f"{current}/{total}", True, CYAN)
                screen.blit(counter_text, (SCREEN_WIDTH - counter_text.get_width() - 40, 150))

            # Lista wyników
            base_y = 230  # +1 pusta linia między BACK a wynikami
            if selected_difficulty != 0:
                visible_entries = entries[scroll_offset : scroll_offset + VISIBLE_ENTRIES]
                for draw_i, entry in enumerate(visible_entries):
                    i = scroll_offset + draw_i  # rzeczywisty indeks w entries
                    line_y = base_y + draw_i * 30
                    is_selected = (i == selected_score_index)
                    if is_selected:
                        pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(20, line_y, SCREEN_WIDTH - 40, 28))

                    if "dummy" in entry:
                        dummy_surf = smallest_font.render("...", True, WHITE)
                        screen.blit(dummy_surf, (60, line_y))
                        continue

                    date = entry["time"][:10]
                    player = entry["player"]
                    score = entry["score"]

                    left_text = f"[{date}] {player}"
                    left_surf = smallest_font.render(left_text, True, WHITE)
                    left_x = 60
                    score_x = SCREEN_WIDTH - 180

                    dots_area = score_x - (left_x + left_surf.get_width()) - 24
                    dot_width = smallest_font.size(". ")[0]
                    dots = ". " * max(0, dots_area // dot_width)

                    dots_surf = smallest_font.render(dots, True, WHITE)
                    score_surf = smallest_font.render(f"Score: {score}", True, WHITE)

                    dots_x = left_x + left_surf.get_width() + 10

                    screen.blit(left_surf, (left_x, line_y))
                    screen.blit(dots_surf, (dots_x, line_y))

                    if i == best_score_index:
                        cup_img = pygame.transform.scale(emoji_images["gold_cup"], (18, 18))
                        screen.blit(cup_img, (score_x - 24, line_y + 3))

                    screen.blit(score_surf, (score_x, line_y))


                # ▲ jeśli coś jest powyżej widoku
                if scroll_offset > 0:
                    screen.blit(smallest_font.render("▲", True, CYAN), (SCREEN_WIDTH - 40, base_y - 20))

                # ▼ jeśli coś jest poniżej widoku
                if scroll_offset + VISIBLE_ENTRIES < len(entries):
                    screen.blit(smallest_font.render("▼", True, CYAN), (SCREEN_WIDTH - 40, base_y + VISIBLE_ENTRIES * 30))

        else:
            score = entries[selected_score_index]
            if "dummy" in score:
                viewing_detail = False
            else:
                screen.blit(font.render(score["player"], True, WHITE), (60, 80))
                screen.blit(small_font.render(score["time"], True, WHITE), (60, 120))
                screen.blit(small_font.render(f"Song: {score['song']}", True, WHITE), (60, 160))
                screen.blit(small_font.render(f"Mode: {score['difficulty']} / {score.get('arrow_mode', 'random')}", True, WHITE), (60, 200))
                screen.blit(small_font.render(f"Score: {score['score']}", True, WHITE), (60, 240))
                screen.blit(small_font.render(f"Accuracy: {score['accuracy']}%", True, WHITE), (60, 280))
                counts = score.get("counts", {})
                line = f"Perfect: {counts.get('PERFECT', 0)}  Good: {counts.get('GOOD', 0)}  OK: {counts.get('OK', 0)}  MISS: {counts.get('MISS', 0)}"
                screen.blit(small_font.render(line, True, WHITE), (60, 320))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or is_select(event):
                return

            elif is_pressed(event, "left"):
                if viewing_detail:
                    viewing_detail = False
                else:
                    selected_difficulty = (selected_difficulty - 1) % len(difficulties)
                    selected_score_index = 0

            elif is_pressed(event, "right"):
                if viewing_detail:
                    viewing_detail = False
                elif entries and selected_score_index > 0:
                    viewing_detail = True
                else:
                    selected_difficulty = (selected_difficulty + 1) % len(difficulties)
                    selected_score_index = 0

            elif is_pressed(event, "up") and not viewing_detail and selected_difficulty != 0:
                selected_score_index = (selected_score_index - 1) % len(entries)
                if selected_score_index < scroll_offset:
                    scroll_offset = selected_score_index

            elif is_pressed(event, "down") and not viewing_detail and selected_difficulty != 0:
                selected_score_index = (selected_score_index + 1) % len(entries)
                if selected_score_index >= scroll_offset + VISIBLE_ENTRIES:
                    scroll_offset = selected_score_index - VISIBLE_ENTRIES + 1

            elif is_start(event):
                if current_diff == "BACK":
                    return
                elif viewing_detail:
                    viewing_detail = False
                elif entries and selected_score_index > 0:
                    viewing_detail = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    selected_score_index = max(0, selected_score_index - VISIBLE_ENTRIES)
                elif event.key == pygame.K_PAGEDOWN:
                    selected_score_index = min(len(entries) - 1, selected_score_index + VISIBLE_ENTRIES)


def show_credits():
    if os.path.exists("credits.json"):
        with open("credits.json", "r") as f:
            credits = json.load(f)
    else:
        credits = []

    clock = pygame.time.Clock()
    running = True
    offset = 0
    visible_entries = 7
    total_entries = len(credits)
    line_height = 100

    while running:
        clock.tick(30)
        screen.fill(DARK_GRAY)

        title = font.render("CREDITS", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        base_y = 100
        for i in range(offset, min(offset + visible_entries, total_entries)):
            entry = credits[i]
            y = base_y + (i - offset) * line_height

            number_text = f"{i+1}/{total_entries}"
            num_surface = smallest_font.render(number_text, True, CYAN)
            screen.blit(num_surface, (SCREEN_WIDTH - 100, y))

            screen.blit(smallest_font.render(entry["title"], True, CYAN), (60, y))
            screen.blit(smallest_font.render(f"By: {entry['author']}", True, WHITE), (60, y + 20))
            screen.blit(smallest_font.render(entry["url"], True, BLUE), (60, y + 40))
            screen.blit(smallest_font.render(f"License: {entry['license']}", True, ORANGE), (60, y + 60))
            eq_width = smallest_font.size("=")[0]
            num_eq = (SCREEN_WIDTH - 120) // eq_width  # 60px padding (po 60 z każdej strony)
            eq_line = "=" * num_eq
            eq_surface = smallest_font.render(eq_line, True, HIGHLIGHT)
            screen.blit(eq_surface, (60, y + 80))

        back_msg = small_font.render("Press Start or Escape to go back", True, GREEN)
        screen.blit(back_msg, (SCREEN_WIDTH // 2 - back_msg.get_width() // 2, SCREEN_HEIGHT - 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or is_select(event) or is_start(event):
                return
            elif is_pressed(event, "up"):
                if offset > 0:
                    offset -= 1
            elif is_pressed(event, "down"):
                if offset + visible_entries < total_entries:
                    offset += 1


if __name__ == "__main__":
    menu_loop()