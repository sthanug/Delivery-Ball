# Tile viewer: shows every tile with its number. Hover to see it big.
import pygame
from pathlib import Path

TILE = 16
SPACING = 1
SCALE = 3
BIG = TILE * SCALE
GAP = 4

ASSET_DIR = Path(__file__).resolve().parent / "assets"

pygame.init()
screen = pygame.display.set_mode((960, 720))
pygame.display.set_caption("Bounce Delivery - tile viewer")
clock = pygame.time.Clock()
small_font = pygame.font.Font(None, 20)
big_font = pygame.font.Font(None, 48)


def load_tiles(path):
    sheet = pygame.image.load(str(path)).convert_alpha()
    cols = (sheet.get_width() + SPACING) // (TILE + SPACING)
    rows = (sheet.get_height() + SPACING) // (TILE + SPACING)
    print(f"Sheet size {sheet.get_size()} -> {cols} columns x {rows} rows")
    tiles = []
    for row in range(rows):
        for col in range(cols):
            x = col * (TILE + SPACING)
            y = row * (TILE + SPACING)
            tile = sheet.subsurface((x, y, TILE, TILE))
            tiles.append(pygame.transform.scale(tile, (BIG, BIG)))
    return tiles, cols


tiles, cols = load_tiles(ASSET_DIR / "images" / "tilemap.png")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((90, 90, 100))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered = None

    for index, tile in enumerate(tiles):
        col = index % cols
        row = index // cols
        x = 10 + col * (BIG + GAP)
        y = 10 + row * (BIG + GAP)
        screen.blit(tile, (x, y))
        screen.blit(small_font.render(str(index), True, (255, 255, 0)), (x + 2, y + 2))
        tile_rect = pygame.Rect(x, y, BIG, BIG)
        if tile_rect.collidepoint(mouse_x, mouse_y):
            hovered = index
            pygame.draw.rect(screen, (255, 255, 255), tile_rect, 2)

    if hovered is not None:
        screen.blit(big_font.render(f"Tile {hovered}", True, (255, 255, 255)), (700, 20))
        screen.blit(pygame.transform.scale(tiles[hovered], (192, 192)), (700, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
