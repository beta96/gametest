import pygame
import sys
import json
import time
import math
import random

# Inicjalizacja Pygame
pygame.init()

# Stałe gry
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Wczytaj dane z pliku JSON
with open("game_data.json", "r") as file:
    game_data = json.load(file)

# Statystyki gracza i wroga
player_stats = game_data["player"]
enemy_stats = game_data["enemy"]

# Umiejętności gracza
skills = player_stats["skills"]

# Dodanie walidacji danych wczytywanych z pliku JSON
required_keys = ["health", "mana", "speed", "skills", "money"]
for key in required_keys:
    if key not in player_stats:
        player_stats[key] = 0 if key == "money" else None

# załadowanie obrazka tła
background_image = pygame.image.load("background.png")
background_rect = background_image.get_rect()

# Załaduj obrazki dla efektów
fireball_image = pygame.image.load("fireball.png")
heal_image = pygame.image.load("heal.png")

# Utwórz okno gry
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D rpg test")

# Załaduj grafikę postaci
player_image = pygame.image.load("postac1.png")
player_rect = player_image.get_rect()
player_rect.topleft = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Wróg
enemy_image = pygame.image.load("enemy_slime.png")
enemy_rect = enemy_image.get_rect()
enemy_rect.topleft = tuple(enemy_stats["position"])

# Efekty wizualne
active_effects = []

# Zmienna do śledzenia czasu dla regeneracji many
last_mana_regen_time = pygame.time.get_ticks()

# Zmienna do śledzenia cooldownu dla umiejętności
last_skill_used = {
    "fireball": 0,
    "heal": 0
}
skill_cooldown = {
    "fireball": 1000,  # Cooldown 1 sekunda dla fireball
    "heal": 2000  # Cooldown 2 sekundy dla heal
}

# Zmienna do losowego ruchu przeciwnika
last_enemy_move_time = pygame.time.get_ticks()
enemy_speed = 5

# Funkcja do poruszania przeciwnika
def move_enemy():
    global last_enemy_move_time, enemy_rect

    # Sprawdzenie, czy minęła 1 sekunda
    current_time = pygame.time.get_ticks()
    if current_time - last_enemy_move_time >= 1000:  # Ruch co 1 sekundę
        dx = random.choice([-1, 1]) * random.randint(1, enemy_speed)
        dy = random.choice([-1, 1]) * random.randint(1, enemy_speed)

        # Przemieszczanie przeciwnika
        enemy_rect.x -= dx
        enemy_rect.y -= dy

        # Zapewniamy, że wróg nie wyjdzie poza tło (pozycja na tle)
        enemy_rect.x = max(0, min(enemy_rect.x, background_rect.width + enemy_rect.width))
        enemy_rect.y = max(0, min(enemy_rect.y, background_rect.height + enemy_rect.height))

        # Zaktualizuj czas ostatniego ruchu
        last_enemy_move_time = current_time

# Funkcja do resetowania przeciwnika
def reset_enemy():
    enemy_rect.topleft = (random.randint(0, SCREEN_WIDTH - enemy_rect.width),
                          random.randint(0, SCREEN_HEIGHT - enemy_rect.height))
    player_stats["money"] += 10
    enemy_stats["health"] = enemy_stats["max_health"]

# Pozycja tła (to jest przesuwane)
background_x = 0
background_y = 0

# Główna pętla gry
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Ruch postaci
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player_rect.top > 0:
        player_rect.y -= player_stats["speed"]
        background_y += player_stats["speed"]  # Przesuwamy tło w dół
        enemy_rect.y += player_stats["speed"]
    if keys[pygame.K_s] and player_rect.bottom < SCREEN_HEIGHT:
        player_rect.y += player_stats["speed"]
        background_y -= player_stats["speed"]  # Przesuwamy tło w górę
        enemy_rect.y -= player_stats["speed"]
    if keys[pygame.K_a] and player_rect.left > 0:
        player_rect.x -= player_stats["speed"]
        background_x += player_stats["speed"]  # Przesuwamy tło w prawo
        enemy_rect.x += player_stats["speed"]
    if keys[pygame.K_d] and player_rect.right < SCREEN_WIDTH:
        player_rect.x += player_stats["speed"]
        background_x -= player_stats["speed"]  # Przesuwamy tło w lewo
        enemy_rect.x -= player_stats["speed"]

    # Ograniczanie ruchu tła (aby nie wychodziło poza granice)
    background_x = max(min(background_x, 0), SCREEN_WIDTH - background_rect.width)
    background_y = max(min(background_y, 0), SCREEN_HEIGHT - background_rect.height)

    # Rysowanie
    screen.fill(WHITE)

    # Rysowanie tła
    screen.blit(background_image, (background_x, background_y))

    # Rysowanie gracza
    screen.blit(player_image, player_rect)

    # Użycie umiejętności
    current_time = pygame.time.get_ticks()

    if pygame.mouse.get_pressed()[0] and current_time - last_skill_used["fireball"] >= skill_cooldown["fireball"]:  # Fireball
        skill = skills["fireball"]
        if player_stats["mana"] >= skill["mana_cost"]:
            player_stats["mana"] -= skill["mana_cost"]
            mouse_pos = pygame.mouse.get_pos()  # Pozycja myszki w momencie wystrzelenia
            dx = mouse_pos[0] - player_rect.centerx
            dy = mouse_pos[1] - player_rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            direction = (dx / distance, dy / distance)  # Wektor jednostkowy kierunku
            active_effects.append({
                "type": "fireball",
                "position": list(player_rect.center),
                "direction": direction,  # Zapisz kierunek lotu
                "image": pygame.image.load("fireball.png"),  # Obrazek dla fireballa
                "lifetime": 360  # 6 sekund w 60 FPS (6 * 60 = 360)
        })
            last_skill_used["fireball"] = current_time  # Zaktualizuj czas ostatniego użycia umiejętności

    if keys[pygame.K_2] and current_time - last_skill_used["heal"] >= skill_cooldown["heal"]:  # Heal
        skill = skills["heal"]
        if player_stats["mana"] >= skill["mana_cost"]:
            player_stats["mana"] -= skill["mana_cost"]
            player_stats["health"] = min(player_stats["health"] + skill["healing"], 100)
            # Dodajemy efekt heal pod graczem
            active_effects.append({
                "type": "heal",
                "position": (player_rect.centerx - 13, player_rect.bottom - 5),  # Pojawia się pod graczem
                "image": heal_image,
                "duration": 120,  # Czas trwania efektu heal (np. 2 sekundy)
            } )
            last_skill_used["heal"] = current_time  # Zaktualizuj czas ostatniego użycia umiejętności
    
    # Regeneracja many co 0.25 sekundy
    if current_time - last_mana_regen_time >= 250:  # Co 250 ms (0.25 sekundy)
        player_stats["mana"] = min(player_stats["mana"] + 1, 50)  # Limit max many to 50
        last_mana_regen_time = current_time

    # Wróg
    if enemy_stats["health"] > 0:
        screen.blit(enemy_image, (enemy_rect.x, enemy_rect.y))  # Uwzględniamy przesunięcie tła
        font = pygame.font.SysFont(None, 20)
        enemy_name_text = font.render(f"Blue Slime - HP: {enemy_stats['health']}", True, BLACK)

        # Obliczanie pozycji tekstu nad przeciwnikiem
        text_x = enemy_rect.centerx - enemy_name_text.get_width() // 2
        text_y = enemy_rect.top - 30  # Ustawiamy tekst 30 pikseli nad przeciwnikiem

        # Rysowanie tekstu
        screen.blit(enemy_name_text, (text_x, text_y))  # Uwzględniamy przesunięcie tła
    else:
        # Reset przeciwnika, gdy jego zdrowie wynosi 0
        reset_enemy()

    # Ruch przeciwnika
    move_enemy()

    # Efekty wizualne
    for effect in active_effects[:]:
        if effect["type"] == "fireball":
            # Obróć fireball w kierunku lotu
            dx, dy = effect["direction"]
            angle = math.degrees(math.atan2(dy, dx))
            rotated_fireball = pygame.transform.rotate(effect["image"], -angle)
            rotated_rect = rotated_fireball.get_rect(center=effect["position"])
            screen.blit(rotated_fireball, rotated_rect)

            # Przesuwaj fireball w zapisanym kierunku
            effect["position"][0] += dx * 10  # Prędkość lotu
            effect["position"][1] += dy * 10

            effect["lifetime"] -= 1

            if (effect["position"][0] < 0 or effect["position"][0] > SCREEN_WIDTH or
                effect["position"][1] < 0 or effect["position"][1] > SCREEN_HEIGHT):
                active_effects.remove(effect)

            # Sprawdź, czy fireball dotarł do celu
            if effect["lifetime"] <= 0 or enemy_rect.collidepoint(effect["position"]):
                enemy_stats["health"] -= skills["fireball"]["damage"]
                active_effects.remove(effect)

        elif effect["type"] == "heal":
            screen.blit(effect["image"], effect["position"])  # Rysowanie efektu heal
             # Zmniejsz czas trwania efektu
            effect["duration"] -= 1
            if effect["duration"] <= 0:
                active_effects.remove(effect) # Możesz dodać inne warunki, aby heal trwał dłużej

    # Wyświetlanie statystyk
    font = pygame.font.SysFont(None, 24)
    stats_text = font.render(f"HP: {player_stats['health']} | Mana: {player_stats['mana']} | Gold: {player_stats['money']}", True, BLACK)
    screen.blit(stats_text, (10, 10))

    # Odśwież ekran
    pygame.display.flip()

    # Ogranicz FPS
    clock.tick(FPS)

# Zakończenie gry
player_stats["mana"] = 50
try:
    with open("game_data.json", "w") as file:
        json.dump(game_data, file, indent=4, ensure_ascii=False)
    print("Zapisano dane do pliku game_data.json")
except Exception as e:
    print(f"Błąd podczas zapisu: {e}")
pygame.quit()
sys.exit()