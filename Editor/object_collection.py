import os
import pygame

class ObjectCollection:
    def __init__(self):
        self.objects = {}  # Dictionary to store objects by type
        self.load_objects()

    def load_objects(self):
        # Define the base path for objects
        base_path = "Maps/Common/Objects"
        
        # For each object type directory
        for object_type in os.listdir(base_path):
            type_path = os.path.join(base_path, object_type)
            if os.path.isdir(type_path):  # Check if it's a directory
                self.objects[object_type] = []
                
                # Load all objects of this type
                for filename in os.listdir(type_path):
                    if filename.endswith(".png"):
                        try:
                            # Extract the number from the filename (format: type00000.png)
                            # Remove the type prefix and .png extension
                            number_str = filename[len(object_type.lower()):-4]
                            if number_str.isdigit():  # Check if it's a valid number
                                number = int(number_str)
                                
                                # Load and scale the image
                                image = pygame.image.load(os.path.join(type_path, filename))
                                image = pygame.transform.scale(image, (32, 32))  # Assuming 32x32 tiles
                                
                                # Store the object information
                                self.objects[object_type].append({
                                    'id': number,
                                    'image': image,
                                    'type': object_type,
                                    'filename': filename
                                })
                        except ValueError:
                            print(f"Warning: Could not parse number from filename: {filename}")
                            continue
                        except pygame.error as e:
                            print(f"Warning: Could not load image {filename}: {e}")
                            continue
                
                # Sort objects by their ID
                self.objects[object_type].sort(key=lambda x: x['id'])

    def get_objects_by_type(self, object_type):
        """Return all objects of a specific type"""
        return self.objects.get(object_type, [])

    def get_object(self, object_type, object_id):
        """Get a specific object by type and ID"""
        for obj in self.objects.get(object_type, []):
            if obj['id'] == object_id:
                return obj
        return None

    def get_total_objects(self):
        """Get the total number of objects across all types"""
        return sum(len(objects) for objects in self.objects.values()) 