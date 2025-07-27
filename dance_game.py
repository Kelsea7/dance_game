# dance_game.py (pauza zatrzymuje muzykę) – WERSJA Z JEDNYM OKNEM I DYNAMICZNYMI WYMIARAMI
import pygame
import random
import sys
import json
import os
import datetime

pygame.init()
pygame.mixer.init()
pygame.joystick.init()

CONFIG_FILE = "config_pad.json"
SETTINGS_FILE = "settings.json"
SCORES_FILE = "scores.json"
if not os.path.exists(SCORES_FILE):
    with open(SCORES_FILE, "w") as f:
        json.dump([], f)

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        BUTTON_MAP = json.load(f)
else:
    BUTTON_MAP = {"left": 0, "down": 1, "up": 2, "right": 3, "start": 9, "pause": 8, "back": 7}

if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)
    DIFFICULTY_SETTINGS = settings["difficulties"]
else:
    DIFFICULTY_SETTINGS = {
        "EASY": {"speed": 5, "double_chance": 0.1},
        "MEDIUM": {"speed": 7, "double_chance": 0.15},
        "HARD": {"speed": 9, "double_chance": 0.2},
        "NIGHTMARE": {"speed": 12, "double_chance": 0.3}
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"difficulties": DIFFICULTY_SETTINGS}, f, indent=2)

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

font = pygame.font.SysFont("dejavusans", 30)
small_font = pygame.font.SysFont("dejavusans", 24)
smallest_font = pygame.font.SysFont("dejavusans", 20)

DARK_GRAY = (40, 40, 40)
WHITE = (255, 255, 255)
BLUE = (0, 128, 255)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 51, 51)
ORANGE = (255, 128, 0)

arrow_size = 60
arrow_types = ['left', 'down', 'up', 'right']
clock = pygame.time.Clock()

def get_arrow_positions(SCREEN_WIDTH):
    # Ustaw pozycje proporcjonalnie do szerokości okna
    return {
        'left': int(SCREEN_WIDTH * 0.15),
        'down': int(SCREEN_WIDTH * 0.4),
        'up': int(SCREEN_WIDTH * 0.6),
        'right': int(SCREEN_WIDTH * 0.8)
    }

def get_hit_zone_y(SCREEN_HEIGHT):
    return SCREEN_HEIGHT - SCREEN_HEIGHT // 3

def draw_arrow(surface, direction, x, center_y, size, color):
    shaft_width = size // 5
    shaft_length = int(size * 0.6)
    head_size = size // 2

    if direction == 'up':
        top_y = center_y - (shaft_length + head_size) // 2
        shaft_rect = pygame.Rect(x - shaft_width // 2, top_y + head_size, shaft_width, shaft_length)
        head_points = [(x, top_y), (x - head_size, top_y + head_size), (x + head_size, top_y + head_size)]
    elif direction == 'down':
        top_y = center_y - (shaft_length + head_size) // 2
        shaft_rect = pygame.Rect(x - shaft_width // 2, top_y, shaft_width, shaft_length)
        head_points = [(x, top_y + shaft_length + head_size), (x - head_size, top_y + shaft_length), (x + head_size, top_y + shaft_length)]
    elif direction == 'left':
        top_y = center_y
        shaft_rect = pygame.Rect(x + head_size, top_y - shaft_width // 2, shaft_length, shaft_width)
        head_points = [(x, top_y), (x + head_size, top_y - head_size), (x + head_size, top_y + head_size)]
    elif direction == 'right':
        top_y = center_y
        shaft_rect = pygame.Rect(x, top_y - shaft_width // 2, shaft_length, shaft_width)
        head_points = [(x + shaft_length + head_size, top_y), (x + shaft_length, top_y - head_size), (x + shaft_length, top_y + head_size)]

    pygame.draw.rect(surface, color, shaft_rect)
    pygame.draw.polygon(surface, color, head_points)

def is_pressed(event, direction):
    key_map = {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}
    return event.type == pygame.KEYDOWN and event.key == key_map[direction] or event.type == pygame.JOYBUTTONDOWN and event.button == BUTTON_MAP[direction]

def is_released(event, direction):
    key_map = {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}
    return event.type == pygame.KEYUP and event.key == key_map[direction] or event.type == pygame.JOYBUTTONUP and event.button == BUTTON_MAP[direction]

def is_start(event):
    return event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN or event.type == pygame.JOYBUTTONDOWN and event.button == BUTTON_MAP["start"]

def is_pause(event):
    return (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
           (event.type == pygame.JOYBUTTONDOWN and event.button == BUTTON_MAP["pause"])

def is_select(event):
    return event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or event.type == pygame.JOYBUTTONDOWN and event.button == BUTTON_MAP["back"]

def run_game(song_path="songs/test.ogg", difficulty="EASY", player_name="PLAYER", arrow_mode="random", map_file=None, screen=None, SCREEN_WIDTH=600, SCREEN_HEIGHT=900):
    emoji_images = {
        "music": pygame.image.load("assets/emojis/1f3b5.png").convert_alpha(),
        "game": pygame.image.load("assets/emojis/1f3ae.png").convert_alpha(),
        "missed": pygame.image.load("assets/emojis/274c.png").convert_alpha(),
        "gold_cup": pygame.image.load("assets/emojis/1f3c6.png").convert_alpha(),
        "timer": pygame.image.load("assets/emojis/23f0.png").convert_alpha(),
        "target": pygame.image.load("assets/emojis/1f3af.png").convert_alpha()
    }
    arrow_positions = get_arrow_positions(SCREEN_WIDTH)
    hit_zone_height = 80
    hit_zone_y = get_hit_zone_y(SCREEN_HEIGHT)

    arrow_speed = DIFFICULTY_SETTINGS[difficulty]["speed"]
    double_spawn_chance = DIFFICULTY_SETTINGS[difficulty]["double_chance"]
    score_saved = False

    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

    score = 0
    missed = 0
    total_paused_time = 0
    display_elapsed_time = 0
    paused = False
    pause_start = 0
    start_time = pygame.time.get_ticks()
    last_spawn_time = 0
    max_arrows_on_screen = 7

    arrows = []
    active_arrows = {key: False for key in arrow_types}
    hit_this_frame = []

    # DEMO: cztery pokazowe strzałki — nie do trafienia
    uniform_y = -arrow_size * 2
    for d in arrow_types:
        arrows.append({
            'type': d,
            'x': arrow_positions[d],
            'y': uniform_y,
            'hit': True
        })
    demo_mode = True

    feedback_text = ""
    feedback_timer = 0
    rating_counts = {"PERFECT": 0, "GOOD": 0, "OK": 0, "MISS": 0}

    game_over = False
    song_ended = False
    summary_visible = False
    selected_button = 0
    select_press_time = 0
    select_press_count = 0
    spawned_idx = 0

    song_length_sec = pygame.mixer.Sound(song_path).get_length()
    song_title = os.path.basename(song_path).split(".")[0]

    if arrow_mode == "predefined" and map_file and os.path.exists(map_file):
        with open(map_file, "r") as f:
            map_data = json.load(f)
            arrow_map = map_data["arrows"]
    else:
        arrow_map = []

    spawned_from_map = set()
    y_offsets = {key: 0 for key in arrow_types}  # Dodane dla zgodności z kodem

    running = True
    while running:
        select_press_times = []
        dt = clock.tick(60)
        current_time = pygame.time.get_ticks()
        hit_this_frame = []
        if feedback_timer > 0:
            feedback_timer -= dt
        else:
            feedback_text = ""

        events = pygame.event.get()
        for event in events:
            # OBSŁUGA ZMIANY ROZMIARU OKNA
            if event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                arrow_positions = get_arrow_positions(SCREEN_WIDTH)
                hit_zone_y = get_hit_zone_y(SCREEN_HEIGHT)

            if event.type == pygame.QUIT:
                if summary_visible:
                    return
                pygame.mixer.music.stop()
                game_over = True

            elif event.type == pygame.JOYBUTTONDOWN and event.button == BUTTON_MAP["pause"]:
                now = pygame.time.get_ticks()
                if now - select_press_time < 800:
                    select_press_count += 1
                else:
                    select_press_count = 1
                select_press_time = now

                if select_press_count >= 2:
                    pygame.mixer.music.stop()
                    return
                else:
                    paused = not paused
                    if paused:
                        pause_start = pygame.time.get_ticks()
                        pygame.mixer.music.pause()
                    else:
                        total_paused_time += pygame.time.get_ticks() - pause_start
                        pygame.mixer.music.unpause()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                return

            elif is_pause(event):
                paused = not paused
                if paused:
                    pause_start = pygame.time.get_ticks()
                    pygame.mixer.music.pause()
                else:
                    total_paused_time += pygame.time.get_ticks() - pause_start
                    pygame.mixer.music.unpause()
            for direction in arrow_types:
                if is_pressed(event, direction):
                    active_arrows[direction] = True
                elif is_released(event, direction):
                    active_arrows[direction] = False

        if demo_mode:
            for arrow in arrows[:]:
                arrow['y'] += arrow_speed
                if arrow['y'] > SCREEN_HEIGHT:
                    arrows.remove(arrow)
            if not arrows:
                demo_mode = False
            screen.fill(DARK_GRAY)
            pygame.draw.rect(screen, CYAN, (0, hit_zone_y, SCREEN_WIDTH, hit_zone_height), 2)
            for arrow in arrows:
                draw_arrow(screen, arrow['type'], arrow['x'], arrow['y'], arrow_size, GREEN)
            pygame.display.flip()
            continue

        if not paused and not game_over:
            if not song_ended and not pygame.mixer.music.get_busy():
                song_ended = True
            if not song_ended:
                if arrow_mode == "predefined":
                    while spawned_idx < len(arrow_map) and arrow_map[spawned_idx]["time"] <= current_time - start_time:
                        entry = arrow_map[spawned_idx]
                        arrow_type = entry["type"]
                        offset_y = y_offsets.get(arrow_type, 0)
                        arrows.append({
                            'type': arrow_type,
                            'x': arrow_positions[arrow_type],
                            'y': -arrow_size + offset_y,
                            'hit': False
                        })
                        spawned_idx += 1

                else:
                    if current_time - last_spawn_time > 1000 and len(arrows) < max_arrows_on_screen:
                        types_to_spawn = random.sample(arrow_types, 2) if random.random() < double_spawn_chance else [random.choice(arrow_types)]
                        for new_type in types_to_spawn:
                            same_type = [a for a in arrows if a['type'] == new_type and not a['hit']]
                            if len(same_type) == 0:
                                arrows.append({
                                    'type': new_type,
                                    'x': arrow_positions[new_type],
                                    'y': -arrow_size,
                                    'hit': False})
                        last_spawn_time = current_time

            if song_ended and not arrows:
                game_over = True
            for arrow in arrows[:]:
                arrow['y'] += arrow_speed
                center_y = arrow['y'] + arrow_size // 2
                if song_ended and not arrows:
                    game_over = True
                if arrow['y'] > SCREEN_HEIGHT:
                    if not arrow['hit']:
                        missed += 1
                        rating_counts["MISS"] += 1
                        feedback_text = "MISS"
                        feedback_timer = 1000
                    arrows.remove(arrow)
                    continue

                if active_arrows[arrow['type']] and not arrow['hit'] and hit_zone_y < center_y < hit_zone_y + hit_zone_height:
                    arrow['hit'] = True
                    hit_this_frame.append(arrow)

            if hit_this_frame:
                is_double = len(hit_this_frame) >= 2
                offsets = [abs(a['y'] + arrow_size//2 - (hit_zone_y + hit_zone_height//2)) for a in hit_this_frame]
                avg_offset = sum(offsets) / len(offsets)
                if avg_offset <= 10:
                    feedback_text = "PERFECT"
                    rating_counts["PERFECT"] += 1
                    score += int(3 * (1 + (0.25 if difficulty == 'EASY' else 0.5 if difficulty == 'MEDIUM' else 0.75 if difficulty == 'HARD' else 1.0)))
                elif avg_offset <= 25:
                    feedback_text = "GOOD"
                    rating_counts["GOOD"] += 1
                    score += int(2 * (1 + (0.25 if difficulty == 'EASY' else 0.5 if difficulty == 'MEDIUM' else 0.75 if difficulty == 'HARD' else 1.0)))
                else:
                    feedback_text = "OK"
                    rating_counts["OK"] += 1
                    score += int(1 * (1 + (0.25 if difficulty == 'EASY' else 0.5 if difficulty == 'MEDIUM' else 0.75 if difficulty == 'HARD' else 1.0)))
                feedback_timer = 1000

        screen.fill(DARK_GRAY)
        pygame.draw.rect(screen, CYAN, (0, hit_zone_y, SCREEN_WIDTH, hit_zone_height), 2)
        for arrow in arrows:
            color = GREEN if arrow['hit'] else BLUE
            center_y = arrow['y'] + arrow_size // 2
            draw_arrow(screen, arrow['type'], arrow['x'], center_y, arrow_size, color)

        base_y = SCREEN_HEIGHT - 80
        spacing = 25

        # Wyniki
        screen.blit(pygame.transform.scale(emoji_images["gold_cup"], (24, 24)), (20, base_y))
        score_text = smallest_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (50, base_y))

        screen.blit(pygame.transform.scale(emoji_images["missed"], (24, 24)), (20, base_y + spacing))
        missed_text = smallest_font.render(f"Missed: {missed}", True, ORANGE)
        screen.blit(missed_text, (50, base_y + spacing))

        if not paused and not game_over:
            display_elapsed_time = pygame.time.get_ticks() - start_time - total_paused_time

        minutes = display_elapsed_time // 1000 // 60
        seconds = display_elapsed_time // 1000 % 60
        screen.blit(pygame.transform.scale(emoji_images["timer"], (24, 24)), (SCREEN_WIDTH - 180, base_y + spacing))
        time_text = smallest_font.render(f"Timer: {minutes:02d}:{seconds:02d}", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH - 150, base_y + spacing))

        progress = display_elapsed_time / (song_length_sec * 1000)
        progress = max(0, min(progress, 1))
        bar_width = int(SCREEN_WIDTH * progress)
        pygame.draw.rect(screen, CYAN, (0, SCREEN_HEIGHT - 10, bar_width, 10))

        pause_text = small_font.render("PAUZA" if paused else "PLAY", True, RED if paused else WHITE)
        screen.blit(pause_text, (20, 20))

        if feedback_text:
            fb_color = GREEN if feedback_text == "PERFECT" else ORANGE if feedback_text == "GOOD" else RED if feedback_text == "MISS" else WHITE
            fb_size = 48 if feedback_text == "PERFECT" else 36
            fb_font = pygame.font.SysFont(None, fb_size)
            fb = fb_font.render(feedback_text, True, fb_color)
            fb_rect = fb.get_rect(center=(SCREEN_WIDTH//2, hit_zone_y + hit_zone_height + 100))
            screen.blit(fb, fb_rect)

        if not game_over:
            if not paused:
                display_elapsed_time = (pygame.time.get_ticks() - start_time - total_paused_time)
            progress = display_elapsed_time / (song_length_sec * 1000)
            progress = max(0, min(progress, 1))
            bar_width = int(SCREEN_WIDTH * progress)
            pygame.draw.rect(screen, CYAN, (0, SCREEN_HEIGHT - 10, bar_width, 10))

        if game_over:
            screen.fill(DARK_GRAY)
            summary_visible = True
            total_hits = sum(rating_counts[r] for r in ["PERFECT", "GOOD", "OK"])
            total_arrows = total_hits + rating_counts["MISS"]
            accuracy = (total_hits / total_arrows) * 100 if total_arrows > 0 else 0
            song_mins = int(song_length_sec) // 60
            song_secs = int(song_length_sec) % 60

            lines = [
                f"{player_name}",
                "",
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"Song: {song_title} ({song_mins}:{song_secs:02d})",
                f"Mode: {difficulty.upper()} / {arrow_mode}",
                f"Accuracy: {accuracy:.1f}%",
                "",
                f"Score: {score}",
                f"Perfect: {rating_counts['PERFECT']}   Good: {rating_counts['GOOD']}   OK: {rating_counts['OK']}   MISS: {rating_counts['MISS']}",
                "",
                "RETRY",
                "EXIT"
            ]

            retry_index = len(lines) - 2
            exit_index = len(lines) - 1
            score_index = 7
            gold_icon = pygame.transform.scale(emoji_images["gold_cup"], (24, 24))

            for i, line in enumerate(lines):
                is_selected = (i == retry_index and selected_button == 0) or (i == exit_index and selected_button == 1)
                color = GREEN if is_selected else WHITE
                prefix = "▶ " if is_selected else "   "

                if i in [retry_index, exit_index]:
                    used_font = font
                elif i in [1, 2]:
                    used_font = smallest_font
                elif i == 8:
                    used_font = small_font
                elif i in [3, 4, 5]:
                    used_font = small_font
                else:
                    used_font = font

                text = prefix + line if i in [retry_index, exit_index] else line
                if i == score_index:
                    screen.blit(gold_icon, (SCREEN_WIDTH // 2 - 120, 200 + i * 40))
                    label = used_font.render(line, True, color)
                    screen.blit(label, (SCREEN_WIDTH // 2 - 90, 200 + i * 40 - 5))
                else:
                    label = used_font.render(text, True, color)
                    screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, 200 + i * 40))

            keys = pygame.key.get_pressed()
            for event in events:
                if is_pressed(event, "up"):
                    selected_button = 0
                elif is_pressed(event, "down"):
                    selected_button = 1
                elif is_start(event):
                    if selected_button == 0:
                        run_game(song_path, difficulty, player_name, arrow_mode, map_file, screen, SCREEN_WIDTH, SCREEN_HEIGHT)
                        return
                    elif selected_button == 1:
                        return

            if game_over and not score_saved:
                result = {
                    "time": datetime.datetime.now().isoformat(),
                    "song": song_title,
                    "difficulty": difficulty.lower(),
                    "score": score,
                    "accuracy": round(accuracy, 1),
                    "player": player_name,
                    "counts": rating_counts
                }

                try:
                    if os.path.exists(SCORES_FILE):
                        with open(SCORES_FILE, "r") as f:
                            scores = json.load(f)
                    else:
                        scores = []

                    scores.append(result)

                    with open(SCORES_FILE, "w") as f:
                        json.dump(scores, f, indent=2)

                    score_saved = True

                except Exception as e:
                    print("Błąd zapisu scores.json:", e)

        pygame.display.flip()

if __name__ == '__main__':
    import menu
    menu.menu_loop()