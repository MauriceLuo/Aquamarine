import pygame
import math

# Init
pygame.init()
WIDTH, HEIGHT = 700, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Artificial Horizon with Yaw")
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
    radius = 150
    center = (radius, radius)
    oversize = radius * 5  # Bigger to avoid black edges
    pitch_offset = int(pitch * 2)

    # Draw sky/ground on large surface
    horizon = pygame.Surface((oversize, oversize), pygame.SRCALPHA)
    pygame.draw.rect(horizon, BLUE, (0, 0, oversize,
                     oversize // 2 + pitch_offset))
    pygame.draw.rect(horizon, BROWN, (0, oversize // 2 +
                     pitch_offset, oversize, oversize))
    pygame.draw.line(horizon, BLACK, (0, oversize // 2 + pitch_offset),
                     (oversize, oversize // 2 + pitch_offset), 4)

    # Rotate it
    rotated = pygame.transform.rotate(horizon, -roll)
    rotated_rect = rotated.get_rect(center=center)

    # Create circular mask and paste rotated image
    circular_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    mask = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255), center, radius)
    circular_surface.blit(rotated, rotated_rect)

    # Apply mask to keep it circular
    circular_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Blit final to screen
    screen.blit(circular_surface, (25, 25))

    # Draw a black circular outline
    pygame.draw.circle(screen, BLACK, (25 + radius, 25 + radius), radius, 4)

    # Fixed red cross
    pygame.draw.line(screen, RED, (25 + radius - 20, 25 + radius),
                     (25 + radius + 20, 25 + radius), 2)
    pygame.draw.line(screen, RED, (25 + radius, 25 + radius - 20),
                     (25 + radius, 25 + radius + 20), 2)

    # Yaw Compass
    pygame.draw.circle(screen, BLACK, (450, 250), 50, 2)
    yaw_rad = math.radians(yaw)
    end_x = 450 + 40 * math.sin(yaw_rad)
    end_y = 250 - 40 * math.cos(yaw_rad)
    pygame.draw.line(screen, GREEN, (450, 250), (end_x, end_y), 3)
    pygame.draw.circle(screen, RED, (int(end_x), int(end_y)), 5)

    # Roll, Pitch, Yaw values
    screen.blit(font.render(f"Roll: {int(roll)}°", True, BLACK), (350, 80))
    screen.blit(font.render(f"Pitch: {int(pitch)}°", True, BLACK), (350, 110))
    screen.blit(font.render(f"Yaw: {int(yaw)}°", True, BLACK), (350, 140))


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

    screen.fill(SKY)
    draw_artificial_horizon(roll, pitch, yaw)
    pygame.display.flip()
    clock.tick(60)
    print(clock.get_fps())

pygame.quit()
