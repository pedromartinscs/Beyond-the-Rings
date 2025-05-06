import pygame
import os
import json

class AnimationManager:
    def __init__(self):
        self.animations = {}  # Cache for loaded animations
        self.current_frames = {}  # Track current frame for each object
        self.last_update = {}  # Track last update time for each object
        self.object_metadata = {}  # Cache for object metadata
        self.animation_states = {}  # Track current animation state for each object

    def load_object_metadata(self, object_type, object_id):
        """Load and cache object metadata from JSON"""
        cache_key = f"{object_type}{object_id}"
        if cache_key in self.object_metadata:
            return self.object_metadata[cache_key]

        json_path = os.path.join("Maps", "Common", "Objects", object_type, f"{object_type}{object_id:05d}.json")
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                metadata = json.load(f)
                self.object_metadata[cache_key] = metadata
                return metadata
        return None

    def load_animation(self, object_type, object_id, animation_type, direction=0):
        """Load animation frames for a specific object and animation type"""
        cache_key = f"{object_type}{object_id}_{animation_type}_{direction}"
        
        if cache_key in self.animations:
            return self.animations[cache_key]

        # Load object metadata
        metadata = self.load_object_metadata(object_type, object_id)
        if not metadata:
            return None

        # Construct the path to the animation folder
        base_path = os.path.join("Animation", f"{object_type}{object_id:05d}")
        
        if animation_type == "static":
            # For static animations, we just need the single frame for the given direction
            frame_path = os.path.join(base_path, "static", f"{direction}.png")
            if os.path.exists(frame_path):
                frame = pygame.image.load(frame_path).convert_alpha()
                self.animations[cache_key] = [frame]
                return self.animations[cache_key]
            return None
        else:
            # For other animations (movement, fire, destruction), we need all frames
            anim_path = os.path.join(base_path, animation_type, str(direction))
            if os.path.exists(anim_path):
                frames = []
                frame_index = 0
                while True:
                    frame_path = os.path.join(anim_path, f"{frame_index}.png")
                    if not os.path.exists(frame_path):
                        break
                    frame = pygame.image.load(frame_path).convert_alpha()
                    frames.append(frame)
                    frame_index += 1
                if frames:
                    self.animations[cache_key] = frames
                    return self.animations[cache_key]
            return None

    def set_animation_state(self, object_id, state):
        """Set the current animation state for an object"""
        self.animation_states[object_id] = state
        self.reset_animation(object_id)

    def get_current_frame(self, object_id, object_type, animation_type="static", direction=0, animation_speed=0):
        """Get the current animation frame for an object"""
        # Get the current animation state
        current_state = self.animation_states.get(object_id, "static")
        
        # If the object is in a special state (fire or destruction), use that instead
        if current_state in ["fire", "destruction"]:
            animation_type = current_state

        # Use the same cache key format as load_animation
        cache_key = f"{object_type}{object_id}_{animation_type}_{direction}"
        
        # Initialize tracking for this object if not exists
        if object_id not in self.current_frames:
            self.current_frames[object_id] = 0
            self.last_update[object_id] = pygame.time.get_ticks()

        # Get the animation frames
        frames = self.animations.get(cache_key)
        if not frames:
            # Try to load the animation if it's not in cache
            frames = self.load_animation(object_type, object_id, animation_type, direction)
            if not frames:
                return None

        # If it's a static animation or no animation speed, return the first frame
        if animation_type == "static" or animation_speed == 0:
            return frames[0]

        # Update frame based on animation speed
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update[object_id] >= animation_speed:
            self.current_frames[object_id] = (self.current_frames[object_id] + 1) % len(frames)
            self.last_update[object_id] = current_time

            # If this was the last frame of a destruction animation, mark the object for removal
            if animation_type == "destruction" and self.current_frames[object_id] == 0:
                return "DESTROYED"

        return frames[self.current_frames[object_id]]

    def reset_animation(self, object_id):
        """Reset animation state for an object"""
        if object_id in self.current_frames:
            self.current_frames[object_id] = 0
            self.last_update[object_id] = pygame.time.get_ticks() 