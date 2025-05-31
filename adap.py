import pygame
import random
import time

pygame.init()
WIDTH, HEIGHT = 600, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Adaptability Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

player = pygame.Rect(300, 200, 30, 30)
score = 0
start_time = time.time()
change_time = random.randint(5, 10)
control_flipped = False

def draw(score):
    win.fill((30, 30, 30))
    pygame.draw.rect(win, (0, 255, 0), player)
    txt = font.render(f'Score: {score}', True, (255, 255, 255))
    win.blit(txt, (10, 10))
    pygame.display.update()

running = True
while running:
    clock.tick(60)
    current_time = time.time()
    if current_time - start_time > change_time and not control_flipped:
        control_flipped = True
        print("Controls flipped!")  # Simulating change in rule

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    speed = 5

    if not control_flipped:
        if keys[pygame.K_LEFT]: player.x -= speed
        if keys[pygame.K_RIGHT]: player.x += speed
        if keys[pygame.K_UP]: player.y -= speed
        if keys[pygame.K_DOWN]: player.y += speed
    else:
        if keys[pygame.K_LEFT]: player.x += speed
        if keys[pygame.K_RIGHT]: player.x -= speed
        if keys[pygame.K_UP]: player.y += speed
        if keys[pygame.K_DOWN]: player.y -= speed

    # Keep within bounds
    player.x = max(0, min(WIDTH - 30, player.x))
    player.y = max(0, min(HEIGHT - 30, player.y))

    score += 1  # Increase score over time or based on actions
    draw(score)

pygame.quit()

# Save score for model integration
print(f"Final Adaptability Score: {score}")
