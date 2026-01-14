"""
ENEMY MODULE - Enemy character classes and AI

This module contains enemy character classes for the game:
- Various enemy types with different behaviors and stats
- AI behavior patterns (patrol, chase, attack)
- Enemy-specific abilities and attack patterns

Recommendations:
1. Create a base Enemy class to share common functionality
2. Implement proper AI state machine (IDLE, PATROL, CHASE, ATTACK, DEATH)
3. Add pathfinding for intelligent enemy movement
4. Implement aggression ranges and vision detection
5. Add different difficulty levels for enemy behavior
"""

import pygame as pyg
from utils.paths import get_asset_path


# ============================================================================
# CONSTANTS - Enemy configuration
# ============================================================================
ENEMY_BASE_HEALTH = 50
ENEMY_BASE_SPEED = 3
ENEMY_BASE_DAMAGE = 10
ENEMY_ATTACK_RANGE = 50
ENEMY_VISION_RANGE = 200


class Enemy:
    """
    Base Enemy class containing common enemy functionality.
    
    Attributes:
        health (int): Current health points
        speed (int): Movement speed in pixels per frame
        position (tuple): Current (x, y) position on screen
        damage (int): Damage dealt on attack
        direction (str): Current facing direction
    """
    
    def __init__(self, x=0, y=0, health=ENEMY_BASE_HEALTH, speed=ENEMY_BASE_SPEED):
        """
        Initialize enemy with base stats.
        
        Args:
            x (int): Initial X position
            y (int): Initial Y position
            health (int): Initial health (default from constant)
            speed (int): Movement speed (default from constant)
        """
        
        # ====================================================================
        # CHARACTER STATS
        # ====================================================================
        self.health = health
        self.speed = speed
        self.position = (x, y)
        self.damage = ENEMY_BASE_DAMAGE
        self.direction = "right"
        
        # ====================================================================
        # AI BEHAVIOR VARIABLES
        # ====================================================================
        self.state = "IDLE"  # Current AI state: IDLE, PATROL, CHASE, ATTACK, DEATH
        self.target = None  # Target player or waypoint
        
    # ========================================================================
    # MOVEMENT METHODS
    # ========================================================================
    
    def move(self, direction):
        """
        Move enemy in specified direction.
        
        Args:
            direction (str): Movement direction ('up', 'down', 'left', 'right')
        """
        if direction == "up":
            self.position = (self.position[0], self.position[1] - self.speed)
        elif direction == "down":
            self.position = (self.position[0], self.position[1] + self.speed)
        elif direction == "left":
            self.position = (self.position[0] - self.speed, self.position[1])
            self.direction = "left"
        elif direction == "right":
            self.position = (self.position[0] + self.speed, self.position[1])
            self.direction = "right"
    
    # ========================================================================
    # COMBAT METHODS
    # ========================================================================
    
    def take_damage(self, amount):
        """
        Reduce enemy health by specified amount.
        
        Args:
            amount (int): Damage to inflict
        """
        self.health -= amount
        if self.health <= 0:
            self.death()
    
    def attack(self, target):
        """
        Attack target player.
        
        Args:
            target (Character): Target player to attack
        """
        distance = self._calculate_distance(target.position)
        if distance <= ENEMY_ATTACK_RANGE:
            target.take_damage(self.damage)
    
    # ========================================================================
    # AI BEHAVIOR METHODS
    # ========================================================================
    
    def _calculate_distance(self, target_pos):
        """
        Calculate distance to target position.
        
        Args:
            target_pos (tuple): Target (x, y) position
            
        Returns:
            float: Distance to target
        """
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        return (dx**2 + dy**2)**0.5
    
    def chase_target(self, target):
        """
        Move towards target player.
        
        Args:
            target (Character): Target player to chase
        """
        target_x, target_y = target.position
        current_x, current_y = self.position
        
        if target_x > current_x:
            self.move("right")
        elif target_x < current_x:
            self.move("left")
            
        if target_y > current_y:
            self.move("down")
        elif target_y < current_y:
            self.move("up")
    
    def detect_player(self, player):
        """
        Check if player is within vision range.
        
        Args:
            player (Character): Player to detect
            
        Returns:
            bool: True if player is visible
        """
        distance = self._calculate_distance(player.position)
        return distance <= ENEMY_VISION_RANGE
    
    # ========================================================================
    # STATUS MANAGEMENT
    # ========================================================================
    
    def death(self):
        """Handle enemy death - can be overridden by subclasses."""
        self.state = "DEATH"
        # Drop loot or trigger events
    
    def get_status(self):
        """
        Get enemy status information.
        
        Returns:
            dict: Status containing health, position, state
        """
        return {
            "health": self.health,
            "position": self.position,
            "state": self.state
        }
    
    # ========================================================================
    # GAME LOOP UPDATE
    # ========================================================================
    
    def update(self, player=None):
        """
        Update enemy state each frame.
        Implements basic AI behavior.
        
        Args:
            player (Character): Player reference for AI decisions
        """
        if self.state == "DEATH":
            return
        
        # Basic AI: if player detected, chase and attack
        if player:
            if self.detect_player(player):
                self.state = "CHASE"
                self.chase_target(player)
                self.attack(player)
            else:
                self.state = "IDLE"
