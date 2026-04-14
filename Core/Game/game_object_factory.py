import uuid


class GameObjectFactory:
    def __init__(self, object_collection, animation_manager):
        self.object_collection = object_collection
        self.animation_manager = animation_manager

    def create_map_object(self, x, y, obj_type, obj_id, current_health, z_index):
        unique_id = f"{x}_{y}_{obj_type}_{obj_id}"
        obj_image = self._load_primary_image(obj_type, obj_id, unique_id)
        if not obj_image:
            return None

        metadata = self.object_collection.get_object_metadata(obj_type, obj_id) or {}
        properties = metadata.get('properties', {})
        visuals = metadata.get('visuals', {})

        return {
            'x': x,
            'y': y,
            'type': obj_type,
            'id': obj_id,
            'health': current_health,
            'max_health': properties.get('health', -1 if obj_type == 'resource' else 100),
            'z_index': z_index,
            'image': obj_image,
            'offset': 64 if obj_image.get_width() == 128 else 32,
            'damage': properties.get('damage', 1),
            'unique_id': unique_id,
            'name': metadata.get('name', 'Unknown'),
            'animation_speed': visuals.get('animation_speed', 0),
            'frames': visuals.get('frames', 1),
            'is_unit': metadata.get('is_unit', False),
            'direction': metadata.get('direction', 0),
            'has_turret': metadata.get('has_turret', False),
            'turret_direction': metadata.get('turret_direction', 0),
            'charge_percent': 1.0,
        }

    def create_builder_unit(self, x, y, unit_id=0):
        unit_type = 'unit'
        metadata = self.object_collection.get_object_metadata(unit_type, unit_id)
        if not metadata:
            return None

        sprite_size = metadata.get('size', 'small')
        sprite_image = self.object_collection.get_object(unit_type, unit_id, sprite_size)
        if not sprite_image:
            return None

        properties = metadata.get('properties', {})
        visuals = metadata.get('visuals', {})

        return {
            'x': x,
            'y': y,
            'type': unit_type,
            'id': unit_id,
            'health': properties.get('health', 100),
            'max_health': properties.get('health', 100),
            'z_index': properties.get('z_index', 1),
            'image': sprite_image,
            'offset': 32,
            'damage': properties.get('damage', 0),
            'name': metadata.get('name', 'Builder'),
            'animation_speed': visuals.get('animation_speed', 0),
            'frames': visuals.get('frames', 1),
            'is_unit': True,
            'direction': 0,
            'has_turret': False,
            'turret_direction': 0,
            'charge_percent': 1.0,
            'unique_id': str(uuid.uuid4()),
        }

    def create_resource_from_destroyed_building(self, x, y, resource_id):
        resource_image = self._load_fallback_image('resource', resource_id)
        if not resource_image:
            return None

        resource_metadata = self.object_collection.get_object_metadata('resource', resource_id) or {}
        return {
            'x': x,
            'y': y,
            'type': 'resource',
            'id': resource_id,
            'health': -1,
            'max_health': -1,
            'z_index': 1,
            'image': resource_image,
            'offset': 32,
            'damage': 0,
            'unique_id': f"{x}_{y}_resource_{resource_id}",
            'name': resource_metadata.get('name', 'Unknown Resource'),
            'charge_percent': 1.0,
        }

    def _load_primary_image(self, obj_type, obj_id, unique_id):
        animation = self.animation_manager.load_animation(obj_type, obj_id, unique_id, 'static', 0)
        if animation:
            return animation[0]
        return self._load_fallback_image(obj_type, obj_id)

    def _load_fallback_image(self, obj_type, obj_id):
        for size in ('huge', 'large', 'small'):
            obj_image = self.object_collection.get_object(obj_type, obj_id, size)
            if obj_image:
                return obj_image
        return None
