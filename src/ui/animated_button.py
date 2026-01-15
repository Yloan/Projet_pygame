"""
ANIMATED BUTTON MODULE - Animated UI button implementation

This module provides the AnimatedButton class for creating animated clickable UI buttons.
Animated buttons automatically handle:
- Frame-by-frame animation from a list of surfaces
- Mouse position detection and click state management
- Single click registration (prevents double-clicks)
- Animation timing control
"""

import pygame


# ============================================================================
# CONSTANTS - Button configuration
# ============================================================================
DEFAULT_SCALE = 1
DEFAULT_ANIMATION_SPEED = 1  # frames per second


class AnimatedButton:
    """
    Interactive animated button class for UI elements.
    
    Attributes:
        frames (list): List of pygame.Surface objects for animation
        current_frame (int): Current frame index
        animation_speed (int): Milliseconds between frame updates
        rect (pygame.Rect): Button position and size rectangle
        clicked (bool): Internal state for click detection
        
    Features:
        - Frame-by-frame animation with configurable speed
        - Automatic position and size scaling
        - Robust click detection preventing accidental double-clicks
        - Collision detection with mouse position
    """
    
    def __init__(self, x, y, frames, scale=DEFAULT_SCALE, animation_speed=DEFAULT_ANIMATION_SPEED):
        """
        Initialize animated button at specified position with animation frames.
        
        Args:
            x (int): X coordinate for button position
            y (int): Y coordinate for button position
            frames (list): List of pygame.Surface objects for animation
            scale (float): Scale factor for images (default 1)
            animation_speed (int): Frames per second for animation (default 10)
        """
        # ====================================================================
        # ANIMATION SETUP
        # ====================================================================
        self.frames = []
        self.scale = scale
        
        # Scale all frames
        for frame in frames:
            width = frame.get_width()
            height = frame.get_height()
            scaled_frame = pygame.transform.scale(
                frame, 
                (int(width * scale), int(height * scale))
            )
            self.frames.append(scaled_frame)
        
        self.current_frame = 0
        self.animation_speed = max(1, animation_speed)  # Ensure at least 1
        self.animation_counter = 0
        
        
        # ====================================================================
        # POSITION AND COLLISION SETUP
        # ====================================================================
        if self.frames:
            self.rect = self.frames[0].get_rect(topleft=(x, y))
        else:
            self.rect = pygame.Rect(x, y, 0, 0)
        
        # ====================================================================
        # STATE MANAGEMENT
        # ====================================================================
        self.clicked = False  # Track if button was clicked in previous frame

    def update(self):
        """
        Update animation frame based on animation speed.
        Should be called once per frame.
        """
        if not self.frames:
            return
        
        self.animation_counter += 1
        if self.animation_counter >= 60 // self.animation_speed:  # 60 FPS assumption
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, surface):
        """
        Draw button on surface and detect clicks.
        
        Implements robust click detection:
        1. Update animation frame
        2. Detect mouse over button
        3. Register click only on mouse up (prevents double-clicks)
        4. Reset state when mouse leaves button
        
        Args:
            surface (pygame.Surface): Surface to draw button on
            
        Returns:
            bool: True if button was clicked this frame, False otherwise
        """
        action = False
        
        # ====================================================================
        # UPDATE ANIMATION
        # ====================================================================
        self.update()
        
        if not self.frames:
            return False
        
        pos = pygame.mouse.get_pos()

        # ====================================================================
        # DRAW BUTTON
        # ====================================================================
        current_image = self.frames[self.current_frame]
        surface.blit(current_image, (self.rect.x, self.rect.y))

        # ====================================================================
        # CLICK DETECTION LOGIC
        # ====================================================================
        # Check if mouse is over button
        if self.rect.collidepoint(pos):
            # Get current mouse button state
            if pygame.mouse.get_pressed()[0] == 1:  # Left mouse button pressed
                if not self.clicked:
                    self.clicked = True
            else:
                # Mouse button released
                if self.clicked:
                    action = True  # Register click
                    self.clicked = False
        else:
            # Mouse left button area
            self.clicked = False

        return action

    def presse(self):
        """
        Special animation for button press effect.
        """
        pass