"""
ITEMS MODULE - Game items and loot system

This module handles all game items:
- Item classes (weapons, armor, consumables, etc.)
- Item effects and properties
- Inventory management
- Item pickups and drops

Recommendations:
1. Create a base Item class with common properties
2. Implement item rarity system (common, rare, epic, legendary)
3. Add item effects/buffs system
4. Implement inventory management system
5. Add item descriptions and UI elements
"""

import pygame as pyg
from utils.paths import get_asset_path


# ============================================================================
# CONSTANTS - Item configuration
# ============================================================================
ITEM_RARITY_COMMON = 1
ITEM_RARITY_RARE = 2
ITEM_RARITY_EPIC = 3
ITEM_RARITY_LEGENDARY = 4

# Rarity colors for UI
RARITY_COLORS = {
    ITEM_RARITY_COMMON: (200, 200, 200),      # Gray
    ITEM_RARITY_RARE: (0, 128, 255),           # Blue
    ITEM_RARITY_EPIC: (128, 0, 255),           # Purple
    ITEM_RARITY_LEGENDARY: (255, 165, 0),      # Gold
}


class Item:
    """
    Base Item class representing any collectable item in the game.
    
    Attributes:
        name (str): Item name
        description (str): Item description
        value (int): Item value (for trading/selling)
        rarity (int): Item rarity level
        position (tuple): Current (x, y) position on map
    """
    
    def __init__(self, name, description="", value=0, rarity=ITEM_RARITY_COMMON, x=0, y=0):
        """
        Initialize item with basic properties.
        
        Args:
            name (str): Item name
            description (str): Item description
            value (int): Item value
            rarity (int): Rarity level (constant)
            x (int): Initial X position
            y (int): Initial Y position
        """
        self.name = name
        self.description = description
        self.value = value
        self.rarity = rarity
        self.position = (x, y)
        self.picked_up = False
    
    # ========================================================================
    # ITEM INFORMATION METHODS
    # ========================================================================
    
    def get_info(self):
        """
        Get item information dictionary.
        
        Returns:
            dict: Item name, description, value, and rarity
        """
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "rarity": self.rarity
        }
    
    def get_rarity_color(self):
        """
        Get color for UI display based on rarity.
        
        Returns:
            tuple: RGB color tuple
        """
        return RARITY_COLORS.get(self.rarity, RARITY_COLORS[ITEM_RARITY_COMMON])
    
    # ========================================================================
    # ITEM INTERACTION METHODS
    # ========================================================================
    
    def use(self, player=None):
        """
        Use item - to be implemented by specific item types.
        
        Args:
            player (Character): Player using the item
        """
        pass
    
    def update(self):
        """Update item state - for animated items or effects."""
        pass


class Consumable(Item):
    """
    Consumable item (potions, food, etc.) that can be used once.
    
    Attributes:
        effect (str): Type of effect (heal, buff, etc.)
        amount (int): Effect amount (healing, damage, etc.)
    """
    
    def __init__(self, name, effect, amount, description="", value=0, rarity=ITEM_RARITY_COMMON):
        """
        Initialize consumable item.
        
        Args:
            name (str): Item name
            effect (str): Effect type (e.g., 'heal')
            amount (int): Effect amount
            description (str): Item description
            value (int): Item value
            rarity (int): Rarity level
        """
        super().__init__(name, description, value, rarity)
        self.effect = effect
        self.amount = amount
    
    def use(self, player=None):
        """
        Use consumable on player.
        
        Args:
            player (Character): Player to apply effect on
        """
        if player:
            if self.effect == "heal":
                player.heal(self.amount)
            elif self.effect == "damage_boost":
                # Implement buff system later
                pass
        self.picked_up = True


class Equipment(Item):
    """
    Equipment item (weapons, armor) with stat bonuses.
    
    Attributes:
        slot (str): Equipment slot (head, chest, legs, feet, hand_l, hand_r)
        armor (int): Armor value
        damage_bonus (int): Damage bonus
    """
    
    def __init__(self, name, slot, armor=0, damage_bonus=0, description="", value=0, rarity=ITEM_RARITY_COMMON):
        """
        Initialize equipment item.
        
        Args:
            name (str): Item name
            slot (str): Equipment slot
            armor (int): Armor points (default 0)
            damage_bonus (int): Damage bonus (default 0)
            description (str): Item description
            value (int): Item value
            rarity (int): Rarity level
        """
        super().__init__(name, description, value, rarity)
        self.slot = slot
        self.armor = armor
        self.damage_bonus = damage_bonus
    
    def get_stats(self):
        """
        Get equipment stat bonuses.
        
        Returns:
            dict: Equipment armor and damage bonus
        """
        return {
            "armor": self.armor,
            "damage_bonus": self.damage_bonus
        }


class Inventory:
    """
    Inventory system for managing player items.
    
    Attributes:
        items (list): List of Item objects in inventory
        max_size (int): Maximum inventory size
    """
    
    def __init__(self, max_size=20):
        """
        Initialize inventory.
        
        Args:
            max_size (int): Maximum number of items (default 20)
        """
        self.items = []
        self.max_size = max_size
    
    # ========================================================================
    # INVENTORY MANAGEMENT METHODS
    # ========================================================================
    
    def add_item(self, item):
        """
        Add item to inventory.
        
        Args:
            item (Item): Item to add
            
        Returns:
            bool: True if added successfully, False if inventory full
        """
        if len(self.items) < self.max_size:
            self.items.append(item)
            return True
        return False
    
    def remove_item(self, item):
        """
        Remove item from inventory.
        
        Args:
            item (Item): Item to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def get_inventory_value(self):
        """
        Calculate total inventory value.
        
        Returns:
            int: Total value of all items
        """
        return sum(item.value for item in self.items)
    
    def is_full(self):
        """
        Check if inventory is full.
        
        Returns:
            bool: True if at maximum capacity
        """
        return len(self.items) >= self.max_size
    
    def get_items_by_type(self, item_type):
        """
        Get all items of specific type.
        
        Args:
            item_type (type): Item class type to filter
            
        Returns:
            list: Items matching the type
        """
        return [item for item in self.items if isinstance(item, item_type)]
