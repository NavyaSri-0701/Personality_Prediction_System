import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FONT = pygame.font.Font(None, 36)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Task Tracker - Conscientiousness Game")

clock = pygame.time.Clock()

# Create tasks
tasks = []
for _ in range(5):
    x = random.randint(50, WIDTH - 100)
    y = random.randint(50, HEIGHT - 100)
    tasks.append(pygame.Rect(x, y, 50, 50))

score = 0
current_task = 0
start_time = time.time()

running = True
while running:
    screen.fill(WHITE)

    # Draw tasks
    for i, task in enumerate(tasks):
        color = GREEN if i == current_task else RED
        pygame.draw.rect(screen, color, task)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if tasks[current_task].collidepoint(event.pos):
                score += 1
                current_task += 1
            else:
                score -= 1

            if current_task >= len(tasks):
                running = False

    # Draw score
    score_text = FONT.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()

# Final conscientiousness score
end_time = time.time()
duration = end_time - start_time
conscientiousness_score = max(0, min(100, (score / len(tasks)) * 100 - duration // 2))
print(f"Estimated CSN Score: {conscientiousness_score:.2f}")
