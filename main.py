import pygame
import random
from pathlib import Path

TILE = 16
SPACING = 1
SCALE = 3
BIG = TILE * SCALE

ASSET_DIR = Path(__file__).resolve().parent / "assets"

pygame.init()
screen = pygame.display.set_mode((960, 720), pygame.SCALED | pygame.FULLSCREEN)
pygame.display.set_caption("Delivery Ball")
clock = pygame.time.Clock()
WIDTH, HEIGHT = screen.get_size()


def load_tiles(path):
    sheet = pygame.image.load(str(path)).convert_alpha()
    cols = (sheet.get_width() + SPACING) // (TILE + SPACING)
    rows = (sheet.get_height() + SPACING) // (TILE + SPACING)

    tiles = []
    for row in range(rows):
        for col in range(cols):
            x = col * (TILE + SPACING)
            y = row * (TILE + SPACING)
            tile = sheet.subsurface((x, y, TILE, TILE))
            tile = pygame.transform.scale(tile, (BIG, BIG))
            tiles.append(tile)
    return tiles, cols


tiles, cols = load_tiles(ASSET_DIR / "images" / "tilemap.png")

PACKAGE_SIZE = 28

package_image = pygame.image.load(str(ASSET_DIR / "images" / "packages.png")).convert_alpha()
package_image = pygame.transform.scale(package_image, (PACKAGE_SIZE, PACKAGE_SIZE))

AUDIO_DIR = ASSET_DIR / "audio"

pickup_sound = pygame.mixer.Sound(str(AUDIO_DIR / "PackageCollected.mp3"))
deliver_sound = pygame.mixer.Sound(str(AUDIO_DIR / "PackageDelivered.mp3"))
car_sound = pygame.mixer.Sound(str(AUDIO_DIR / "HitCar.mp3"))

pickup_sound.set_volume(1.0)
deliver_sound.set_volume(1.0)
car_sound.set_volume(1.0)

pygame.mixer.music.load(str(AUDIO_DIR / "Music.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

FONT_FILE = ASSET_DIR / "fonts" / "ArcadeClassic.ttf"
FONT_PATH = str(FONT_FILE) if FONT_FILE.exists() else None

if FONT_PATH is None:
    print("FONT NOT FOUND")
hud_font = pygame.font.Font(FONT_PATH, 40)
big_font = pygame.font.Font(FONT_PATH, 96)
button_font = pygame.font.Font(FONT_PATH, 44)


ROOF = [
    [0, 1, 2],
    [12, 13, 14],
    [24, 25, 26],
]
BLUE_ROOF = [[6, 7, 8], [18, 19, 20], [30, 31, 32]]
WALL = 37
BROWN_WALL = 43
DOOR = 52
SHOP = 56
SHOP_RIGHT = 57
SIDEWALK = 88
TREE = 71
LAMP = 84
HEDGE = 82
ROAD = 75
ROAD_COLOR = (62, 70, 92)

CITY_MAP = [
    ".####....BBBB...###L",
    ".####....BBBB...###.",
    ".wdww....bsSb...wdw.",
    "T,P,,,,,,,P,,,,,,P,T",
    "....................",
    "...BBB....####..BBB.",
    "...BBB....####..BBB.",
    "...sSb....wwdw..sSb.",
    "L,,,P,,H,,,,P,,,,P,L",
    "....................",
    ".###...BBBB....####.",
    ".###...BBBB....####.",
    ".wdw...bsSb....wdww.",
    "T,P,,,,,,PH,,,,,P,,T",
    "....................",
]


def is_roof(x, y, char):
    if y < 0 or y >= len(CITY_MAP) or x < 0 or x >= len(CITY_MAP[y]):
        return False
    return CITY_MAP[y][x] == char


def roof_tile(x, y, char, grid):
    if not is_roof(x, y - 1, char):
        row = 0
    elif not is_roof(x, y + 1, char):
        row = 2
    else:
        row = 1

    if not is_roof(x - 1, y, char):
        col = 0
    elif not is_roof(x + 1, y, char):
        col = 2
    else:
        col = 1

    return grid[row][col]


def build_city():
    city = pygame.Surface(screen.get_size())
    city.fill(ROAD_COLOR)

    for y, line in enumerate(CITY_MAP):
        for x, char in enumerate(line):
            pos = (x * BIG, y * BIG)
            city.blit(tiles[ROAD], pos)
            if char == ",":
                city.blit(tiles[SIDEWALK], pos)
            elif char == "#":
                city.blit(tiles[roof_tile(x, y, "#", ROOF)], pos)
            elif char == "B":
                city.blit(tiles[roof_tile(x, y, "B", BLUE_ROOF)], pos)
            elif char == "w":
                city.blit(tiles[WALL], pos)
            elif char == "d":
                city.blit(tiles[DOOR], pos)
            elif char == "b":
                city.blit(tiles[BROWN_WALL], pos)
            elif char == "s":
                city.blit(tiles[SHOP], pos)
            elif char == "S":
                city.blit(tiles[SHOP_RIGHT], pos)
            elif char == "L":
                city.blit(tiles[SIDEWALK], pos)
                city.blit(tiles[LAMP], pos)
            elif char == "H":
                city.blit(tiles[SIDEWALK], pos)
                city.blit(tiles[HEDGE], pos)
            elif char == "P":
                city.blit(tiles[SIDEWALK], pos)
            elif char == "T":
                city.blit(tiles[SIDEWALK], pos)
                city.blit(tiles[TREE], pos)
    return city


for row_number, line in enumerate(CITY_MAP):
    if len(line) != 20:
        print(f"MAP WARNING: row {row_number} has {len(line)} characters, not 20")

city_surface = build_city()


SOLID = "#BwdbsSTLH"

walls = []
for y, line in enumerate(CITY_MAP):
    for x, char in enumerate(line):
        if char in SOLID:
            walls.append(pygame.Rect(x * BIG, y * BIG, BIG, BIG))

BALL_RADIUS = 12
ACCEL = 1400
MAX_SPEED = 520
DRAG = 0
BOUNCE = 1

ball_image = pygame.image.load(str(ASSET_DIR / "images" / "ball.png")).convert_alpha()
ball_image = pygame.transform.scale(ball_image, (BALL_RADIUS * 2 + 4, BALL_RADIUS * 2 + 4))
tint_color = (255, 19, 240)
ball_image.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)

ball_x = 10 * BIG + BIG / 2
ball_y = 4 * BIG + BIG / 2
ball_vx = 0
ball_vy = 0


def ball_rect():
    return pygame.Rect(int(ball_x - BALL_RADIUS), int(ball_y - BALL_RADIUS),
                       BALL_RADIUS * 2, BALL_RADIUS * 2)


def move_ball(dt):
    global ball_x, ball_y, ball_vx, ball_vy

    keys = pygame.key.get_pressed()
    right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
    left = keys[pygame.K_a] or keys[pygame.K_LEFT]
    down = keys[pygame.K_s] or keys[pygame.K_DOWN]
    up = keys[pygame.K_w] or keys[pygame.K_UP]
    ball_vx += (right - left) * ACCEL * dt
    ball_vy += (down - up) * ACCEL * dt

    ball_vx -= ball_vx * DRAG * dt
    ball_vy -= ball_vy * DRAG * dt

    speed = (ball_vx ** 2 + ball_vy ** 2) ** 0.5
    if speed > MAX_SPEED:
        ball_vx = ball_vx / speed * MAX_SPEED
        ball_vy = ball_vy / speed * MAX_SPEED

    ball_x += ball_vx * dt
    for wall in walls:
        if ball_rect().colliderect(wall):
            if ball_vx > 0:
                ball_x = wall.left - BALL_RADIUS
            else:
                ball_x = wall.right + BALL_RADIUS
            ball_vx = -ball_vx * BOUNCE

    ball_y += ball_vy * dt
    for wall in walls:
        if ball_rect().colliderect(wall):
            if ball_vy > 0:
                ball_y = wall.top - BALL_RADIUS
            else:
                ball_y = wall.bottom + BALL_RADIUS
            ball_vy = -ball_vy * BOUNCE

    if ball_x < BALL_RADIUS:
        ball_x = BALL_RADIUS
        ball_vx = abs(ball_vx) * BOUNCE
    if ball_x > WIDTH - BALL_RADIUS:
        ball_x = WIDTH - BALL_RADIUS
        ball_vx = -abs(ball_vx) * BOUNCE
    if ball_y < BALL_RADIUS:
        ball_y = BALL_RADIUS
        ball_vy = abs(ball_vy) * BOUNCE
    if ball_y > HEIGHT - BALL_RADIUS:
        ball_y = HEIGHT - BALL_RADIUS
        ball_vy = -abs(ball_vy) * BOUNCE


def draw_ball():
    rect = ball_image.get_rect(center=(int(ball_x), int(ball_y)))
    screen.blit(ball_image, rect)


PERSON_TILES = [108, 120, 121]

person_spots = []
for y, line in enumerate(CITY_MAP):
    for x, char in enumerate(line):
        if char == "P":
            person_spots.append(pygame.Rect(x * BIG, y * BIG, BIG, BIG))


def random_spot(avoid):
    spot = random.choice(person_spots)
    while spot == avoid:
        spot = random.choice(person_spots)
    return spot


sender = random_spot(None)
sender_look = random.choice(PERSON_TILES)
receiver = None
receiver_look = None
has_package = False
deliveries = 0


def update_people():
    global sender, sender_look, receiver, receiver_look, has_package, deliveries
    if not has_package:
        if ball_rect().colliderect(sender):
            has_package = True
            pickup_sound.play()
            receiver = random_spot(sender)
            receiver_look = random.choice(PERSON_TILES)
    else:
        if ball_rect().colliderect(receiver):
            has_package = False
            deliveries += 1
            deliver_sound.play()
            sender = random_spot(receiver)
            sender_look = random.choice(PERSON_TILES)


def draw_box(cx, cy):
    rect = package_image.get_rect(center=(cx, cy))
    screen.blit(package_image, rect)


def draw_people():
    if has_package:
        screen.blit(tiles[receiver_look], receiver)
    else:
        screen.blit(tiles[sender_look], sender)
        draw_box(sender.centerx, sender.top - 4)


ROUND_TIME = 60
time_left = ROUND_TIME
game_over = False
started = False

PLAY_AGAIN_BUTTON = pygame.Rect(0, 0, 300, 70)
PLAY_AGAIN_BUTTON.center = (WIDTH // 2, HEIGHT // 2 + 100)


def draw_hud():
    panel = pygame.Rect(0, 0, 540, 56)
    panel.midtop = (WIDTH // 2, 8)

    background = pygame.Surface(panel.size, pygame.SRCALPHA)
    pygame.draw.rect(background, (20, 20, 35, 190), background.get_rect(), border_radius=14)
    screen.blit(background, panel)
    pygame.draw.rect(screen, (255, 170, 60), panel, 3, border_radius=14)

    icon_rect = package_image.get_rect(midleft=(panel.left + 18, panel.centery))
    screen.blit(package_image, icon_rect)
    text = hud_font.render(f"DELIVERED  {deliveries}", True, (255, 255, 255))
    screen.blit(text, text.get_rect(midleft=(icon_rect.right + 12, panel.centery)))

    seconds = max(time_left, 0)
    color = (255, 80, 80) if seconds <= 10 else (255, 255, 255)
    text = hud_font.render(f"TIME  {seconds:.0f}", True, color)
    screen.blit(text, text.get_rect(midright=(panel.right - 18, panel.centery)))


def draw_text(text, font, center):
    shadow = font.render(text, True, (20, 20, 30))
    image = font.render(text, True, (255, 255, 255))
    rect = image.get_rect(center=center)
    screen.blit(shadow, (rect.x + 3, rect.y + 3))
    screen.blit(image, rect)


def draw_game_over():
    shade = pygame.Surface((WIDTH, HEIGHT))
    shade.set_alpha(170)
    screen.blit(shade, (0, 0))

    draw_text("TIMES UP", big_font, (WIDTH // 2, HEIGHT // 2 - 90))
    draw_text(f"YOU DELIVERED  {deliveries}  PACKAGES", hud_font, (WIDTH // 2, HEIGHT // 2))

    mouse_over = PLAY_AGAIN_BUTTON.collidepoint(pygame.mouse.get_pos())
    color = (255, 170, 60) if mouse_over else (230, 120, 40)
    pygame.draw.rect(screen, color, PLAY_AGAIN_BUTTON, border_radius=12)
    pygame.draw.rect(screen, (40, 20, 10), PLAY_AGAIN_BUTTON, 4, border_radius=12)
    draw_text("PLAY AGAIN", button_font, PLAY_AGAIN_BUTTON.center)
    draw_text("or press R", hud_font, (WIDTH // 2, PLAY_AGAIN_BUTTON.bottom + 35))


def reset_game():
    global ball_x, ball_y, ball_vx, ball_vy
    global sender, sender_look, receiver, has_package, deliveries
    global time_left, game_over
    ball_x = 10 * BIG + BIG / 2
    ball_y = 4 * BIG + BIG / 2
    ball_vx = 0
    ball_vy = 0
    sender = random_spot(None)
    sender_look = random.choice(PERSON_TILES)
    receiver = None
    has_package = False
    deliveries = 0
    time_left = ROUND_TIME
    game_over = False


def draw_start_screen():
    shade = pygame.Surface((WIDTH, HEIGHT))
    shade.set_alpha(170)
    screen.blit(shade, (0, 0))

    draw_text("DELIVERY BALL", big_font, (WIDTH // 2, HEIGHT // 2 - 120))
    draw_text("DELIVER PACKAGES IN 60 SECONDS", hud_font, (WIDTH // 2, HEIGHT // 2 - 30))
    draw_text("WASD OR ARROWS TO MOVE", hud_font, (WIDTH // 2, HEIGHT // 2 + 15))

    mouse_over = PLAY_AGAIN_BUTTON.collidepoint(pygame.mouse.get_pos())
    color = (255, 170, 60) if mouse_over else (230, 120, 40)
    pygame.draw.rect(screen, color, PLAY_AGAIN_BUTTON, border_radius=12)
    pygame.draw.rect(screen, (40, 20, 10), PLAY_AGAIN_BUTTON, 4, border_radius=12)
    draw_text("PLAY", button_font, PLAY_AGAIN_BUTTON.center)
    draw_text("ESC TO QUIT", hud_font, (WIDTH // 2, PLAY_AGAIN_BUTTON.bottom + 35))


debug_font = pygame.font.Font(None, 24)
show_debug = False


def draw_debug():
    lines = [
        f"FPS: {clock.get_fps():.0f}",
        f"ball: ({ball_x:.0f}, {ball_y:.0f})",
        f"speed: ({ball_vx:.0f}, {ball_vy:.0f})",
        f"has_package: {has_package}",
    ]
    for i, text in enumerate(lines):
        image = debug_font.render(text, True, (255, 255, 0))
        screen.blit(image, (8, 72 + i * 20))

    pygame.draw.rect(screen, (255, 0, 0), ball_rect(), 1)
    target = receiver if has_package else sender
    pygame.draw.rect(screen, (0, 255, 0), target, 2)


running = True
game_over = False
started = False
while running:
    dt = min(clock.tick(60) / 1000, 1 / 30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            show_debug = not show_debug
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if not started:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if PLAY_AGAIN_BUTTON.collidepoint(event.pos):
                    started = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                started = True
        if game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if PLAY_AGAIN_BUTTON.collidepoint(event.pos):
                    reset_game()

    if started and not game_over:
        move_ball(dt)
        update_people()
        time_left -= dt
        if time_left <= 0:
            game_over = True

    screen.blit(city_surface, (0, 0))
    draw_people()
    draw_ball()
    if has_package:
        draw_box(int(ball_x), int(ball_y) - 20)
    draw_hud()
    if show_debug:
        draw_debug()
    if game_over:
        draw_game_over()
    if not started:
        draw_start_screen()
    pygame.display.flip()

pygame.quit()
