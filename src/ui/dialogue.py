"""
DIALOGUE MODULE - Game dialogue and conversation system

This module handles NPC dialogue and player conversations:
- Dialogue trees and branching conversations
- NPC dialogue boxes and text display
- Dialogue choices and player responses
- Dialogue state management

Recommendations:
1. Implement dialogue tree structure for complex conversations
2. Add dialogue parsing from JSON/YAML files
3. Implement dialogue choices that affect game state
4. Add NPC personality and tone variations
5. Implement dialogue history tracking
6. Add localization support for multiple languages
"""

import pygame as pyg


# ============================================================================
# CONSTANTS - Dialogue configuration
# ============================================================================
DIALOGUE_WIDTH = 600
DIALOGUE_HEIGHT = 150
DIALOGUE_PADDING = 20
DIALOGUE_TEXT_SIZE = 20
DIALOGUE_BG_COLOR = (50, 50, 50, 200)  # Dark gray with transparency
DIALOGUE_TEXT_COLOR = (255, 255, 255)  # White
DIALOGUE_BORDER_COLOR = (200, 200, 200)  # Light gray


class DialogueBox:
    """
    Dialogue box for displaying NPC conversations.
    
    Attributes:
        text (str): Dialogue text to display
        speaker (str): Name of character speaking
        position (tuple): (x, y) position on screen
        choices (list): Optional dialogue choices for player
    """
    
    def __init__(self, speaker="", text="", x=100, y=100):
        """
        Initialize dialogue box.
        
        Args:
            speaker (str): Character name speaking (default empty)
            text (str): Dialogue text to display (default empty)
            x (int): X position (default 100)
            y (int): Y position (default 100)
        """
        self.speaker = speaker
        self.text = text
        self.position = (x, y)
        self.choices = []
        self.active = False
        self.font = pyg.font.SysFont("arialblack", DIALOGUE_TEXT_SIZE)
    
    # ========================================================================
    # DIALOGUE MANAGEMENT
    # ========================================================================
    
    def set_dialogue(self, speaker, text, choices=None):
        """
        Set dialogue content.
        
        Args:
            speaker (str): Character name speaking
            text (str): Dialogue text
            choices (list): Optional dialogue choices (list of strings)
        """
        self.speaker = speaker
        self.text = text
        self.choices = choices if choices else []
        self.active = True
    
    def add_choice(self, choice_text):
        """
        Add dialogue choice for player.
        
        Args:
            choice_text (str): Choice text to display
        """
        self.choices.append(choice_text)
    
    def clear_choices(self):
        """Clear all dialogue choices."""
        self.choices = []
    
    # ========================================================================
    # RENDERING
    # ========================================================================
    
    def draw(self, surface):
        """
        Draw dialogue box on surface.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        if not self.active:
            return
        
        # Draw semi-transparent background
        dialogue_rect = pyg.Rect(
            self.position[0],
            self.position[1],
            DIALOGUE_WIDTH,
            DIALOGUE_HEIGHT
        )
        pyg.draw.rect(surface, DIALOGUE_BG_COLOR, dialogue_rect)
        pyg.draw.rect(surface, DIALOGUE_BORDER_COLOR, dialogue_rect, 2)
        
        # Draw speaker name
        speaker_text = self.font.render(self.speaker, True, DIALOGUE_TEXT_COLOR)
        surface.blit(
            speaker_text,
            (self.position[0] + DIALOGUE_PADDING, self.position[1] + DIALOGUE_PADDING)
        )
        
        # Draw dialogue text (wrapped)
        self._draw_wrapped_text(surface)
    
    def _draw_wrapped_text(self, surface):
        """
        Draw text with word wrapping.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Simple word wrapping implementation
        words = self.text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_text = ' '.join(current_line)
            text_surface = self.font.render(test_text, True, DIALOGUE_TEXT_COLOR)
            
            if text_surface.get_width() > DIALOGUE_WIDTH - 2 * DIALOGUE_PADDING:
                # Line too long, move word to next line
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add remaining text
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw all lines
        y_offset = self.position[1] + DIALOGUE_PADDING + 30
        for line in lines:
            text_surface = self.font.render(line, True, DIALOGUE_TEXT_COLOR)
            surface.blit(text_surface, (self.position[0] + DIALOGUE_PADDING, y_offset))
            y_offset += DIALOGUE_TEXT_SIZE + 5
    
    # ========================================================================
    # STATE MANAGEMENT
    # ========================================================================
    
    def close(self):
        """Close dialogue box."""
        self.active = False
        self.clear_choices()
    
    def is_active(self):
        """
        Check if dialogue box is currently active.
        
        Returns:
            bool: True if dialogue is displayed
        """
        return self.active


class DialogueTree:
    """
    Dialogue tree for managing branching conversations.
    
    Attributes:
        nodes (dict): Dictionary of dialogue nodes
        current_node (str): ID of current dialogue node
    """
    
    def __init__(self):
        """Initialize empty dialogue tree."""
        self.nodes = {}
        self.current_node = None
    
    # ========================================================================
    # TREE BUILDING
    # ========================================================================
    
    def add_node(self, node_id, speaker, text, choices=None):
        """
        Add dialogue node to tree.
        
        Args:
            node_id (str): Unique node identifier
            speaker (str): Character speaking
            text (str): Dialogue text
            choices (dict): {choice_text: next_node_id} mapping
        """
        self.nodes[node_id] = {
            'speaker': speaker,
            'text': text,
            'choices': choices if choices else {}
        }
    
    # ========================================================================
    # TREE NAVIGATION
    # ========================================================================
    
    def start(self, node_id):
        """
        Start dialogue tree at specified node.
        
        Args:
            node_id (str): Starting node ID
        """
        self.current_node = node_id
    
    def get_current_dialogue(self):
        """
        Get current dialogue content.
        
        Returns:
            dict: {speaker, text, choices} or None if no current node
        """
        if not self.current_node or self.current_node not in self.nodes:
            return None
        
        node = self.nodes[self.current_node]
        return {
            'speaker': node['speaker'],
            'text': node['text'],
            'choices': list(node['choices'].keys())
        }
    
    def choose(self, choice_index):
        """
        Select a dialogue choice and move to next node.
        
        Args:
            choice_index (int): Index of selected choice
            
        Returns:
            bool: True if choice was valid, False otherwise
        """
        if not self.current_node or self.current_node not in self.nodes:
            return False
        
        node = self.nodes[self.current_node]
        choices = list(node['choices'].items())
        
        if 0 <= choice_index < len(choices):
            _, next_node = choices[choice_index]
            self.current_node = next_node
            return True
        
        return False
