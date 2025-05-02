import pygame
import math

# Init
pygame.init()
WIDTH, HEIGHT = 900, 600  # Larger window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Artificial Horizon - Modular Surface")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Colors
BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
SKY = (246, 255, 255)


def wrap_angle(angle):
    angle = angle % 360
    if angle > 180:
        angle -= 360
    return angle


def draw_artificial_horizon(roll, pitch, yaw):
    surface_size = (500, 300)
    surface = pygame.Surface(surface_size)
    surface.fill(SKY)

    radius = 150
    center = (radius, radius)
    oversize = radius * 5
    pitch_offset = int(pitch * 2)

    # Sky & ground
    horizon = pygame.Surface((oversize, oversize), pygame.SRCALPHA)
    pygame.draw.rect(horizon, BLUE, (0, 0, oversize,
                     oversize // 2 + pitch_offset))
    pygame.draw.rect(horizon, BROWN, (0, oversize // 2 +
                     pitch_offset, oversize, oversize))
    pygame.draw.line(horizon, BLACK, (0, oversize // 2 + pitch_offset),
                     (oversize, oversize // 2 + pitch_offset), 4)

    # Rotate and mask
    rotated = pygame.transform.rotate(horizon, -roll)
    rotated_rect = rotated.get_rect(center=center)

    circular_surface = pygame.Surface(
        (radius * 2, radius * 2), pygame.SRCALPHA)
    mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255), center, radius)
    circular_surface.blit(rotated, rotated_rect)
    circular_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Paste to modular surface
    surface.blit(circular_surface, (0, 0))
    pygame.draw.circle(surface, BLACK, center, radius, 4)

    # Red cross
    pygame.draw.line(surface, RED, (radius - 20, radius),
                     (radius + 20, radius), 2)
    pygame.draw.line(surface, RED, (radius, radius - 20),
                     (radius, radius + 20), 2)

    # Yaw compass
    pygame.draw.circle(surface, BLACK, (350, 250), 50, 2)
    yaw_rad = math.radians(yaw)
    end_x = 350 + 40 * math.sin(yaw_rad)
    end_y = 250 - 40 * math.cos(yaw_rad)
    pygame.draw.line(surface, GREEN, (350, 250), (end_x, end_y), 3)
    pygame.draw.circle(surface, RED, (int(end_x), int(end_y)), 5)

    # Text
    surface.blit(font.render(f"Roll: {int(roll)}°", True, BLACK), (300, 10))
    surface.blit(font.render(f"Pitch: {int(pitch)}°", True, BLACK), (300, 40))
    surface.blit(font.render(f"Yaw: {int(yaw)}°", True, BLACK), (300, 70))

    return surface


# Main loop
roll = 0
pitch = 0
yaw = 0
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        roll -= 1
    if keys[pygame.K_RIGHT]:
        roll += 1
    if keys[pygame.K_UP]:
        pitch -= 1
    if keys[pygame.K_DOWN]:
        pitch += 1
    if keys[pygame.K_a]:
        yaw -= 1
    if keys[pygame.K_d]:
        yaw += 1

    roll = wrap_angle(roll)
    pitch = wrap_angle(pitch)
    yaw = wrap_angle(yaw)

    screen.fill((220, 230, 240))  # Neutral background
    horizon_surface = draw_artificial_horizon(roll, pitch, yaw)
    screen.blit(horizon_surface, (50, 50))  # Position the horizon widget

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
