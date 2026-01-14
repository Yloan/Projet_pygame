"""
BUTTON MODULE - UI button implementation

This module provides the Button class for creating clickable UI buttons.
Buttons automatically handle:
- Image rendering and scaling
- Mouse position detection
- Click state management
- Single click registration (prevents double-clicks)

Recommendations:
1. Add hover effects (highlight, scale change)
2. Implement button animations
3. Add disabled state support
4. Create button groups for easier management
5. Add tooltips and button descriptions
"""

import pygame


# ============================================================================
# CONSTANTS - Button configuration
# ============================================================================
DEFAULT_SCALE = 1


class Button:
    """
    Interactive button class for UI elements.
    
    Attributes:
        image (pygame.Surface): Scaled button image
        rect (pygame.Rect): Button position and size rectangle
        clicked (bool): Internal state for click detection
        
    Features:
        - Automatic position and size scaling
        - Robust click detection preventing accidental double-clicks
        - Collision detection with mouse position
    """
    
    def __init__(self, x, y, image, scale=DEFAULT_SCALE):
        """
        Initialize button at specified position with image and scale.
        
        Args:
            x (int): X coordinate for button position
            y (int): Y coordinate for button position
            image (pygame.Surface): Button image surface
            scale (float): Scale factor for image (default 1)
        """
        # ====================================================================
        # IMAGE SETUP AND SCALING
        # ====================================================================
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(
            image, 
            (int(width * scale), int(height * scale))
        )
        
        # ====================================================================
        # POSITION AND COLLISION SETUP
        # ====================================================================
        # Create rect for collision detection and positioning
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # ====================================================================
        # STATE MANAGEMENT
        # ====================================================================
        self.clicked = False  # Track if button was clicked in previous frame

    def draw(self, surface):
        """
        Draw button on surface and detect clicks.
        
        Implements robust click detection:
        1. Detect mouse over button
        2. Register click only on mouse up (prevents double-clicks)
        3. Reset state when mouse leaves button
        
        Args:
            surface (pygame.Surface): Surface to draw button on
            
        Returns:
            bool: True if button was clicked this frame, False otherwise
        """
        action = False
        pos = pygame.mouse.get_pos()

        # ====================================================================
        # DRAW BUTTON
        # ====================================================================
        surface.blit(self.image, (self.rect.x, self.rect.y))

        # ====================================================================
        # CLICK DETECTION LOGIC
        # ====================================================================
        # Check if mouse is over button
        if self.rect.collidepoint(pos):
            # Check if mouse button is pressed
            if pygame.mouse.get_pressed()[0]:
                # If not already clicked, set clicked flag
                if not self.clicked:
                    self.clicked = True
            else:
                # Mouse button released
                # If was clicked before, register action on release
                if self.clicked:
                    self.clicked = False
                    action = True
        else:
            # Mouse moved outside button
            # Reset clicked state if button is released
            if not pygame.mouse.get_pressed()[0]:
                self.clicked = False

        return action
