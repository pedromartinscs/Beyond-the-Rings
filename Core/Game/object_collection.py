import os
import pygame
import json

class ObjectCollection:
    def __init__(self):
        self.objects = {}  # Dictionary to store objects by type
        self.small_objects = {}  # Dictionary for 32x32 objects
        self.large_objects = {}  # Dictionary for 64x64 objects
        self.huge_objects = {}   # Dictionary for 128x128 objects
        self.object_metadata = {}  # Cache for object metadata (name, description)
        self.load_objects()

    def load_object_metadata(self, obj_type, obj_id):
        """Load and cache object metadata from JSON file"""
        # Create a unique key for this object type and ID
        cache_key = f"{obj_type}_{obj_id}"
        
        # Return cached metadata if available
        if cache_key in self.object_metadata:
            return self.object_metadata[cache_key]
        
        # Try to load metadata from JSON file
        try:
            json_path = os.path.join("Maps", "Common", "Objects", obj_type, f"{obj_type}{obj_id:05d}.json")
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    # Store all metadata from the JSON file
                    self.object_metadata[cache_key] = data
                    return data
        except Exception as e:
            print(f"Error loading metadata for {obj_type} {obj_id}: {e}")
        
        # Return default metadata if JSON file doesn't exist or has an error
        default_metadata = {
            'name': f"{obj_type.capitalize()} {obj_id}",
            'description': '',
            'buttons': []
        }
        self.object_metadata[cache_key] = default_metadata
        return default_metadata

    def get_object_metadata(self, obj_type, obj_id):
        """Get cached metadata for an object"""
        cache_key = f"{obj_type}_{obj_id}"
        if cache_key not in self.object_metadata:
            return self.load_object_metadata(obj_type, obj_id)
        return self.object_metadata[cache_key]

    def load_objects(self):
        # Define the base path for objects using os.path.join for consistent separators
        base_path = os.path.join("Maps", "Common", "Objects")
        
        # Track loaded object IDs to prevent duplicates
        loaded_ids = set()
        
        # For each object type directory
        for object_type in os.listdir(base_path):
            type_path = os.path.join(base_path, object_type)
            if os.path.isdir(type_path):  # Check if it's a directory
                # Load all objects of this type
                for filename in os.listdir(type_path):
                    if filename.endswith(".png"):
                        try:
                            # Extract the type and number from the filename (format: type00000.png)
                            # The type is everything before the numbers
                            type_end = 0
                            for i, char in enumerate(filename):
                                if char.isdigit():
                                    type_end = i
                                    break
                            
                            if type_end == 0:  # No numbers found
                                continue
                                
                            obj_type = filename[:type_end].lower()  # Use filename prefix as type
                            number_str = filename[type_end:-4]  # Remove .png
                            
                            if number_str.isdigit():  # Check if it's a valid number
                                number = int(number_str)
                                
                                # Create a unique identifier for this object
                                obj_id = f"{obj_type}_{number}"
                                
                                # Skip if we've already loaded this object
                                if obj_id in loaded_ids:
                                    continue
                                
                                loaded_ids.add(obj_id)
                                
                                # Load the image and convert it for proper transparency
                                image_path = os.path.join(type_path, filename)
                                image = pygame.image.load(image_path).convert_alpha()
                                
                                # Load object metadata
                                metadata = self.load_object_metadata(obj_type, number)
                                
                                # Determine object size based on image dimensions
                                width, height = image.get_size()
                                if width == 128 and height == 128:
                                    target_dict = self.huge_objects
                                    size = 'huge'
                                elif width == 64 and height == 64:
                                    target_dict = self.large_objects
                                    size = 'large'
                                else:
                                    target_dict = self.small_objects
                                    size = 'small'
                                
                                # Initialize the dictionary for this object type if it doesn't exist
                                if obj_type not in target_dict:
                                    target_dict[obj_type] = []
                                
                                # Store the object information
                                target_dict[obj_type].append({
                                    'id': number,
                                    'image': image,
                                    'type': obj_type,
                                    'filename': filename,
                                    'size': size,
                                    'name': metadata['name'],
                                    'description': metadata['description']
                                })
                        except ValueError as e:
                            print(f"Error parsing filename {filename}: {e}")
                            continue
                        except pygame.error as e:
                            print(f"Error loading image {filename}: {e}")
                            continue
                
                # Sort objects by their ID for each type
                for obj_type in self.small_objects:
                    self.small_objects[obj_type].sort(key=lambda x: x['id'])
                for obj_type in self.large_objects:
                    self.large_objects[obj_type].sort(key=lambda x: x['id'])
                for obj_type in self.huge_objects:
                    self.huge_objects[obj_type].sort(key=lambda x: x['id'])

    def get_objects_by_size(self, size=None):
        """Return all objects of a specific size, or all objects ordered by size if no size is specified.
        Args:
            size (str, optional): The size of objects to return ('small', 'large', or 'huge'). If None, returns all objects.
        Returns:
            list: List of objects of the specified size, or all objects ordered by size.
        """
        if size == 'small':
            # Return all small objects from all types
            all_small = []
            for objects in self.small_objects.values():
                all_small.extend(objects)
            return sorted(all_small, key=lambda x: (x['type'], x['id']))
        elif size == 'large':
            # Return all large objects from all types
            all_large = []
            for objects in self.large_objects.values():
                all_large.extend(objects)
            return sorted(all_large, key=lambda x: (x['type'], x['id']))
        elif size == 'huge':
            # Return all huge objects from all types
            all_huge = []
            for objects in self.huge_objects.values():
                all_huge.extend(objects)
            return sorted(all_huge, key=lambda x: (x['type'], x['id']))
        else:
            # Return all objects, ordered by size (small → large → huge)
            all_objects = []
            # Add small objects
            for objects in self.small_objects.values():
                all_objects.extend(objects)
            # Add large objects
            for objects in self.large_objects.values():
                all_objects.extend(objects)
            # Add huge objects
            for objects in self.huge_objects.values():
                all_objects.extend(objects)
            return sorted(all_objects, key=lambda x: (x['type'], x['id']))

    def get_objects_by_type(self, object_type, size=None):
        """Return all objects of a specific type and size.
        This function is maintained for backward compatibility.
        Args:
            object_type (str): The type of object to return.
            size (str, optional): The size of objects to return ('small', 'large', or 'huge').
        Returns:
            list: List of objects of the specified type and size.
        """
        if size == 'small':
            return self.small_objects.get(object_type, [])
        elif size == 'large':
            return self.large_objects.get(object_type, [])
        elif size == 'huge':
            return self.huge_objects.get(object_type, [])
        else:
            # Return all objects of the type, ordered by size
            return (self.small_objects.get(object_type, []) + 
                   self.large_objects.get(object_type, []) +
                   self.huge_objects.get(object_type, []))

    def get_object(self, obj_type, obj_id, size='small'):
        """Get an object by its type and ID.
        Args:
            obj_type (str): The type of object (e.g., "Trees")
            obj_id (int): The ID of the object
            size (str): The size of the object ('small', 'large', or 'huge')
        Returns:
            pygame.Surface: The object's image, or None if not found
        """
        if size == 'small':
            objects = self.small_objects.get(obj_type, [])
        elif size == 'large':
            objects = self.large_objects.get(obj_type, [])
        elif size == 'huge':
            objects = self.huge_objects.get(obj_type, [])
        else:
            objects = []
        
        for obj in objects:
            if obj['id'] == obj_id:
                return obj['image']
        return None

    def get_total_objects(self, size=None):
        """Get the total number of objects across all types"""
        if size == 'small':
            return sum(len(objects) for objects in self.small_objects.values())
        elif size == 'large':
            return sum(len(objects) for objects in self.large_objects.values())
        elif size == 'huge':
            return sum(len(objects) for objects in self.huge_objects.values())
        else:
            return (sum(len(objects) for objects in self.small_objects.values()) +
                   sum(len(objects) for objects in self.large_objects.values()) +
                   sum(len(objects) for objects in self.huge_objects.values())) 