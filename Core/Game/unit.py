import pygame
import math
from typing import Optional, Tuple, Dict, Any
from Core.Game.animation_manager import AnimationManager

class Unit:
    """A class representing a game unit with movement, combat, and building capabilities."""
    
    def __init__(self, x: int, y: int, faction: str, unit_type: str, unit_id: int, 
                 metadata: Dict[str, Any], animation_manager: AnimationManager):
        # Position and movement
        self.x = x
        self.y = y
        self.tile_x = x  # Tile coordinates
        self.tile_y = y
        self.target_x = x  # Target position for movement
        self.target_y = y
        self.faction = faction
        self.unit_type = unit_type
        self.unit_id = unit_id
        self.unique_id = f"{x}_{y}_{unit_type}_{unit_id}"
        
        # Stats from metadata
        self.metadata = metadata
        self.properties = metadata.get('properties', {})
        self.max_health = self.properties.get('health', 100)
        self.health = self.max_health
        self.damage = self.properties.get('damage', 10)
        self.attack_range = self.properties.get('attack_range', 5)
        self.attack_cooldown = self.properties.get('attack_cooldown', 1000)  # in milliseconds
        self.speed = self.properties.get('speed', 1.0)
        
        # State management
        self.state = "idle"  # idle, moving, attacking, building, dead
        self.target = None  # Target object for attacking/following
        self.last_attack_time = 0
        
        # Animation
        self.animation_manager = animation_manager
        self.direction = 0  # 0, 45, 90, 135, 180, 225, 270, 315
        self.available_directions = metadata.get('visuals', {}).get('directions', [0])
        self.has_turret = metadata.get('has_turret', False)
        self.turret_direction = 0
        
        # Path finding
        self.path = []  # List of waypoints to follow
        self.current_waypoint = 0
        
        # Rendering properties
        self.tile_size = 32  # Size of a tile in pixels
        self.offset = 32  # Default offset for centering (half of standard unit size)
        
    def update(self, dt: float) -> None:
        """Update unit state and position.
        
        Args:
            dt: Time delta in seconds
        """
        if self.state == "dead":
            return
            
        self.handle_state(dt)
        
        # Update animation state
        if self.state == "moving":
            self.animation_manager.set_animation_state(self.unique_id, "move")
        elif self.state == "attacking":
            self.animation_manager.set_animation_state(self.unique_id, "attack")
        elif self.state == "idle":
            self.animation_manager.set_animation_state(self.unique_id, "idle")
            
    def handle_state(self, dt: float) -> None:
        """Handle different unit states.
        
        Args:
            dt: Time delta in seconds
        """
        if self.state == "moving":
            self.move_toward_target(dt)
        elif self.state == "attacking":
            self.attack_target(dt)
        elif self.state == "building":
            self.build_structure(dt)
            
    def move_toward_target(self, dt: float) -> None:
        """Move unit toward its target position.
        
        Args:
            dt: Time delta in seconds
        """
        if not self.path:
            self.state = "idle"
            return
            
        # Get current waypoint
        target_x, target_y = self.path[self.current_waypoint]
        
        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 1:  # Reached waypoint
            self.current_waypoint += 1
            if self.current_waypoint >= len(self.path):
                self.path = []
                self.state = "idle"
                return
                
        # Move toward target
        if distance > 0:
            # Calculate movement this frame
            move_distance = self.speed * dt
            self.x += (dx / distance) * move_distance
            self.y += (dy / distance) * move_distance
            
            # Update unit direction
            angle = math.degrees(math.atan2(-dy, dx)) + 90
            angle = (angle + 360) % 360
            self.direction = self.get_nearest_direction(angle)
            
    def attack_target(self, dt: float) -> None:
        """Attack the current target if in range and cooldown is ready.
        
        Args:
            dt: Time delta in seconds
        """
        if not self.target or self.target.get('health', 0) <= 0:
            self.state = "idle"
            self.target = None
            return
            
        # Calculate distance to target
        dx = self.target['x'] - self.tile_x
        dy = self.target['y'] - self.tile_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if target is in range
        if distance > self.attack_range:
            # Move toward target
            self.set_movement_target(self.target['x'], self.target['y'])
            return
            
        # Update direction to face target
        angle = math.degrees(math.atan2(-dy, dx)) + 90
        angle = (angle + 360) % 360
        target_direction = self.get_nearest_direction(angle)
        
        if self.has_turret:
            self.turret_direction = target_direction
        else:
            self.direction = target_direction
            
        # Check attack cooldown
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.perform_attack()
            
    def perform_attack(self) -> None:
        """Perform an attack on the current target."""
        if not self.target:
            return
            
        # Deal damage to target
        if self.target.get('max_health', -1) != -1:  # Don't damage indestructible objects
            self.target['health'] = max(0, self.target.get('health', 0) - self.damage)
            
        # Update last attack time
        self.last_attack_time = pygame.time.get_ticks()
        
        # Set attack animation
        self.animation_manager.set_animation_state(self.unique_id, "fire")
            
    def build_structure(self, dt: float) -> None:
        """Handle building state."""
        # TODO: Implement building mechanics
        pass
        
    def set_movement_target(self, x: int, y: int) -> None:
        """Set a new movement target for the unit.
        
        Args:
            x: Target x coordinate
            y: Target y coordinate
        """
        self.target_x = x
        self.target_y = y
        self.state = "moving"
        # TODO: Calculate path to target using A* pathfinding
        self.path = [(x, y)]  # Temporary direct path
        self.current_waypoint = 0
        
    def set_attack_target(self, target: Dict[str, Any]) -> None:
        """Set a new attack target for the unit.
        
        Args:
            target: Target object dictionary
        """
        self.target = target
        self.state = "attacking"
        
    def take_damage(self, amount: int) -> None:
        """Apply damage to the unit.
        
        Args:
            amount: Amount of damage to apply
        """
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.die()
            
    def die(self) -> None:
        """Handle unit death."""
        self.state = "dead"
        self.animation_manager.set_animation_state(self.unique_id, "death")
        
    def get_nearest_direction(self, angle: float) -> int:
        """Get the nearest available direction for the given angle.
        
        Args:
            angle: Angle in degrees
            
        Returns:
            Nearest available direction in degrees
        """
        # Find the closest direction by comparing the absolute difference
        return min(self.available_directions,
                  key=lambda x: min(abs(x - angle), 360 - abs(x - angle)))
        
    def get_position(self) -> Tuple[int, int]:
        """Get the unit's current position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)
        
    def get_tile_position(self) -> Tuple[int, int]:
        """Get the unit's current tile position.
        
        Returns:
            Tuple of (tile_x, tile_y) coordinates
        """
        return (self.tile_x, self.tile_y)

    def render(self, surface: pygame.Surface, camera_x: int, camera_y: int) -> Optional[pygame.Rect]:
        """Render the unit on the given surface with camera offset.
        
        Args:
            surface: The pygame surface to render on
            camera_x: Camera x offset
            camera_y: Camera y offset
            
        Returns:
            pygame.Rect: The area that was updated, or None if unit is not visible
        """
        # Convert tile coordinates to pixel coordinates
        world_x = self.x * self.tile_size
        world_y = self.y * self.tile_size
        
        # Apply camera offset to get screen coordinates
        screen_x = world_x - camera_x
        screen_y = world_y - camera_y
        
        # Get current animation frame
        current_frame = self.animation_manager.get_next_frame(
            self.unit_id,
            self.unit_type,
            self.unique_id
        )
        
        # If no animation frame or unit is destroyed, return None
        if current_frame == "DESTROYED" or not current_frame:
            return None
            
        # Calculate the offset for centering the unit
        # If the unit is larger than standard size (64x64 or 128x128), adjust offset
        unit_width = current_frame.get_width()
        unit_height = current_frame.get_height()
        self.offset = unit_width // 2 - self.tile_size // 2
        
        # Calculate final screen position with centering offset
        final_x = screen_x - self.offset
        final_y = screen_y - self.offset
        
        # Check if unit is visible on screen
        screen_rect = surface.get_rect()
        unit_rect = pygame.Rect(final_x, final_y, unit_width, unit_height)
        
        if not screen_rect.colliderect(unit_rect):
            return None
            
        # Draw the unit
        surface.blit(current_frame, (final_x, final_y))
        
        # Return the area that was updated
        return unit_rect 