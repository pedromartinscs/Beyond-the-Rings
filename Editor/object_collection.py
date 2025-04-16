import os
import pygame

class ObjectCollection:
    def __init__(self):
        self.objects = {}  # Dictionary to store objects by type
        self.small_objects = {}  # Dictionary for 32x32 objects
        self.large_objects = {}  # Dictionary for 64x64 objects
        self.load_objects()

    def load_objects(self):
        # Define the base path for objects
        base_path = "Maps/Common/Objects"
        
        # For each object type directory
        for object_type in os.listdir(base_path):
            type_path = os.path.join(base_path, object_type)
            if os.path.isdir(type_path):  # Check if it's a directory
                self.small_objects[object_type] = []
                self.large_objects[object_type] = []
                
                # Load all objects of this type
                for filename in os.listdir(type_path):
                    if filename.endswith(".png"):
                        try:
                            # Extract the number from the filename (format: type00000.png)
                            number_str = filename[len(object_type.lower()):-4]
                            if number_str.isdigit():  # Check if it's a valid number
                                number = int(number_str)
                                
                                # Load the image
                                image = pygame.image.load(os.path.join(type_path, filename))
                                
                                # Determine object size based on image dimensions
                                width, height = image.get_size()
                                is_large = width == 64 and height == 64
                                
                                # Scale the image appropriately
                                if is_large:
                                    image = pygame.transform.scale(image, (64, 64))
                                    target_dict = self.large_objects
                                else:
                                    image = pygame.transform.scale(image, (32, 32))
                                    target_dict = self.small_objects
                                
                                # Store the object information
                                target_dict[object_type].append({
                                    'id': number,
                                    'image': image,
                                    'type': object_type,
                                    'filename': filename,
                                    'size': 'large' if is_large else 'small'
                                })
                        except ValueError:
                            print(f"Warning: Could not parse number from filename: {filename}")
                            continue
                        except pygame.error as e:
                            print(f"Warning: Could not load image {filename}: {e}")
                            continue
                
                # Sort objects by their ID
                self.small_objects[object_type].sort(key=lambda x: x['id'])
                self.large_objects[object_type].sort(key=lambda x: x['id'])

    def get_objects_by_type(self, object_type, size=None):
        """Return all objects of a specific type and size"""
        if size == 'small':
            return self.small_objects.get(object_type, [])
        elif size == 'large':
            return self.large_objects.get(object_type, [])
        else:
            # Return all objects of the type, small first, then large
            return (self.small_objects.get(object_type, []) + 
                   self.large_objects.get(object_type, []))

    def get_object(self, object_type, object_id):
        """Get a specific object by type and ID"""
        # Check small objects first
        for obj in self.small_objects.get(object_type, []):
            if obj['id'] == object_id:
                return obj
        # Then check large objects
        for obj in self.large_objects.get(object_type, []):
            if obj['id'] == object_id:
                return obj
        return None

    def get_total_objects(self, size=None):
        """Get the total number of objects across all types"""
        if size == 'small':
            return sum(len(objects) for objects in self.small_objects.values())
        elif size == 'large':
            return sum(len(objects) for objects in self.large_objects.values())
        else:
            return (sum(len(objects) for objects in self.small_objects.values()) +
                   sum(len(objects) for objects in self.large_objects.values())) 