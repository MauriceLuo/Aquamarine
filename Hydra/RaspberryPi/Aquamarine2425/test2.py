import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Cubic Function Line Drawing')

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)

# Function to draw lines based on cubic spacing
def draw_cubic_lines(spacing):
    # Clear the screen
    screen.fill(white)
    
    # Center of the screen
    center_x = width // 2
    center_y = 10
    
    # Draw lines
    for i in range(1, 14):  # Adjust the range for more lines
        # Calculate vertical displacement based on cubic function
        # We use the spacing to determine how much the lines diverge
        y_offset = spacing * (i ** 3) / 1000  # Adjust the divisor for scaling
        
        
        # Draw lines upward and downward from the center line
        pygame.draw.line(screen, black, (0, 100 + y_offset), (width, 100 + y_offset), 1)
        pygame.draw.line(screen, black, (0, 400 - y_offset), (width, 400 - y_offset), 1)

    pygame.display.flip()

# Main loop
def main():
    spacing = 60
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        draw_cubic_lines(spacing)

# Run the main function
if __name__ == "__main__":
    main()