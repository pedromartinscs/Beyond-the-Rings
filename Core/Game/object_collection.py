import os
import pygame

class ObjectCollection:
    def __init__(self):
        self.objects = {}  # Dictionary to store objects by type
        self.small_objects = {}  # Dictionary for 32x32 objects
        self.large_objects = {}  # Dictionary for 64x64 objects
        self.huge_objects = {}   # Dictionary for 128x128 objects
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
                self.huge_objects[object_type] = []
                
                # Load all objects of this type
                for filename in os.listdir(type_path):
                    if filename.endswith(".png"):
                        try:
                            # Extract the number from the filename (format: tree00000.png)
                            number_str = filename[len(object_type.lower()):-4]
                            if number_str.isdigit():  # Check if it's a valid number
                                number = int(number_str)
                                
                                # Load the image and convert it for proper transparency
                                image_path = os.path.join(type_path, filename)
                                image = pygame.image.load(image_path).convert_alpha()
                                
                                # Determine object size based on image dimensions
                                width, height = image.get_size()
                                if width == 128 and height == 128:
                                    image = pygame.transform.scale(image, (128, 128))
                                    target_dict = self.huge_objects
                                    size = 'huge'
                                elif width == 64 and height == 64:
                                    image = pygame.transform.scale(image, (64, 64))
                                    target_dict = self.large_objects
                                    size = 'large'
                                else:
                                    image = pygame.transform.scale(image, (32, 32))
                                    target_dict = self.small_objects
                                    size = 'small'
                                
                                # Store the object information
                                target_dict[object_type].append({
                                    'id': number,
                                    'image': image,
                                    'type': object_type,
                                    'filename': filename,
                                    'size': size
                                })
                        except ValueError:
                            continue
                        except pygame.error as e:
                            continue
                
                # Sort objects by their ID
                self.small_objects[object_type].sort(key=lambda x: x['id'])
                self.large_objects[object_type].sort(key=lambda x: x['id'])
                self.huge_objects[object_type].sort(key=lambda x: x['id'])

    def get_objects_by_type(self, object_type, size=None):
        """Return all objects of a specific type and size"""
        if size == 'small':
            return self.small_objects.get(object_type, [])
        elif size == 'large':
            return self.large_objects.get(object_type, [])
        elif size == 'huge':
            return self.huge_objects.get(object_type, [])
        else:
            # Return all objects of the type, small first, then large, then huge
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