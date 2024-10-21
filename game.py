import pygame
import sys
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Set screen dimensions and zoom factor
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Urban Zoning Map - Flood Fill and Clipping')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GRAY = (50, 50, 50)
ORANGE = (255, 165, 0)

# Text font
font = pygame.font.SysFont(None, 30)

# Initialize zoom parameters
zoom_factor = 1.0
pan_x, pan_y = 0, 0

# FPS and clock
FPS = 60
clock = pygame.time.Clock()

# Define zoning areas (polygons)
zones = [
    [(100, 100), (300, 100), (300, 300), (100, 300)],  # Residential
    [(400, 100), (600, 100), (600, 300), (400, 300)],  # Commercial
    [(100, 400), (300, 400), (300, 600), (100, 600)],  # Industrial
]

zone_colors = [None, None, None]  # To store the fill color for each zone

# Flood Fill Algorithm
def flood_fill(surface, x, y, fill_color, boundary_color):
    current_color = surface.get_at((x, y))
    if current_color != boundary_color and current_color != fill_color:
        surface.set_at((x, y), fill_color)
        if x > 0:
            flood_fill(surface, x - 1, y, fill_color, boundary_color)
        if x < WIDTH - 1:
            flood_fill(surface, x + 1, y, fill_color, boundary_color)
        if y > 0:
            flood_fill(surface, x, y - 1, fill_color, boundary_color)
        if y < HEIGHT - 1:
            flood_fill(surface, x, y + 1, fill_color, boundary_color)

# Clipping and zooming
def apply_clipping(points, zoom_factor, pan_x, pan_y):
    """Adjust polygon points based on zoom and panning"""
    return [(int(x * zoom_factor + pan_x), int(y * zoom_factor + pan_y)) for (x, y) in points]

# Draw the polygons (zones)
def draw_zones():
    """Draw the different zones with their colors"""
    for i, zone in enumerate(zones):
        adjusted_zone = apply_clipping(zone, zoom_factor, pan_x, pan_y)
        color = zone_colors[i] if zone_colors[i] else BLACK
        pygame.draw.polygon(screen, color, adjusted_zone, 0 if zone_colors[i] else 1)

def draw_ui():
    """Draw additional UI components like labels, titles, and instructions"""
    # Title
    title = font.render("Urban Zoning Map", True, DARK_GRAY)
    screen.blit(title, (10, 10))

    # Instructions
    instructions = [
        "Instructions:",
        "Left-click to fill zones",
        "Right-click + drag to pan",
        "Scroll to zoom in/out",
    ]
    for i, instruction in enumerate(instructions):
        instruction_text = font.render(instruction, True, DARK_GRAY)
        screen.blit(instruction_text, (10, 50 + 30 * i))

    # Zone Labels
    zone_labels = ["Residential", "Commercial", "Industrial"]
    for i, zone in enumerate(zones):
        zone_center = (sum([p[0] for p in zone]) // 4, sum([p[1] for p in zone]) // 4)
        label = font.render(zone_labels[i], True, BLACK)
        adjusted_label_pos = (int(zone_center[0] * zoom_factor + pan_x), int(zone_center[1] * zoom_factor + pan_y))
        screen.blit(label, adjusted_label_pos)

# Smooth zoom function
def smooth_zoom(new_zoom_factor, zoom_speed=0.1):
    global zoom_factor
    zoom_factor += (new_zoom_factor - zoom_factor) * zoom_speed

def main():
    global zoom_factor, pan_x, pan_y

    filling = False
    selected_zone = None
    while True:
        screen.fill(WHITE)
        draw_zones()
        draw_ui()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                x, y = event.pos

                # Adjust clicked point based on zoom and panning
                adjusted_x = int((x - pan_x) / zoom_factor)
                adjusted_y = int((y - pan_y) / zoom_factor)

                # Check which zone is clicked for flood fill
                for i, zone in enumerate(zones):
                    adjusted_zone = apply_clipping(zone, zoom_factor, pan_x, pan_y)
                    if pygame.draw.polygon(screen, BLACK, adjusted_zone, 0).collidepoint(x, y):
                        if event.button == 1:  # Left click - fill the zone
                            selected_zone = i
                            fill_color = RED if i == 0 else (GREEN if i == 1 else BLUE)
                            flood_fill(screen, x, y, fill_color, BLACK)
                            zone_colors[i] = fill_color
                            filling = True
                        break

            elif event.type == MOUSEBUTTONUP:
                filling = False

            elif event.type == MOUSEMOTION:
                if event.buttons[2]:  # Right click for panning
                    pan_x += event.rel[0]
                    pan_y += event.rel[1]

            elif event.type == MOUSEWHEEL:  # Zoom in/out
                if event.y > 0:
                    smooth_zoom(zoom_factor * 1.1)  # Zoom in
                elif event.y < 0:
                    smooth_zoom(zoom_factor / 1.1)  # Zoom out

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
