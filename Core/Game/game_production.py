import pygame


class GameProduction:
    def __init__(self, game):
        self.game = game
        self.max_queue_size = 6
        self.default_production_duration = 1000

    def update(self):
        for obj in self.game.objects:
            production_queue = obj.get('production_queue', [])
            if not production_queue:
                continue

            if obj.get('charge_percent', 1.0) < 1.0:
                continue

            self._complete_current_order(obj, production_queue)

    def enqueue_builder_unit(self, building):
        if not self._can_queue_builder(building):
            return False

        production_order = self._create_builder_production_order(building)
        if not self.game.remove_credits(production_order['cost']):
            print("Not enough credits to build a unit.")
            return False

        production_queue = building.setdefault('production_queue', [])
        production_queue.append(production_order)

        if len(production_queue) == 1:
            self._start_production(building, production_order)

        print("Builder production queued.")
        return True

    def cancel_queue_item(self, building, queue_index):
        if not building:
            return False

        production_queue = building.get('production_queue', [])
        if queue_index < 0 or queue_index >= len(production_queue):
            return False

        removed_order = production_queue.pop(queue_index)
        self.game.add_credits(removed_order.get('cost', 0))

        if not production_queue:
            self._clear_production_state(building)
        elif queue_index == 0:
            self._start_production(building, production_queue[0])

        print(f"Removed {removed_order.get('name', 'unit')} from production queue.")
        return True

    def _can_queue_builder(self, building):
        if not building or building['type'] != 'building' or building['id'] != 0:
            return False

        production_queue = building.setdefault('production_queue', [])
        if len(production_queue) >= self.max_queue_size:
            print("Production queue is full.")
            return False

        if not self.game.has_enough_credits(250):
            print("Not enough credits to build a unit.")
            return False

        return True

    def _complete_current_order(self, building, production_queue):
        current_order = production_queue[0]
        if current_order.get('action') == 'builder_unit':
            self._complete_builder_production(building, production_queue)

    def _complete_builder_production(self, building, production_queue):
        spawn_tile = self._find_builder_spawn_tile(building)
        if not spawn_tile:
            return

        tile_x, tile_y = spawn_tile
        unit_id = production_queue[0].get('unit_id', 0)
        new_unit = self.game.object_factory.create_builder_unit(tile_x, tile_y, unit_id=unit_id)
        if not new_unit:
            print("Builder unit could not be created.")
            return

        self.game.objects.append(new_unit)
        self.game.game_world.add_object_to_grid(new_unit)
        self.game.camera_moved = True
        self.game.game_camera.update_visible_objects()

        production_queue.pop(0)
        if production_queue:
            self._start_production(building, production_queue[0])
        else:
            self._clear_production_state(building)

        print("Builder unit created at", tile_x, tile_y)

    def _start_production(self, building, production_order):
        current_time = pygame.time.get_ticks()
        building['charge_percent'] = 0.0
        building['last_charge_time'] = current_time
        building['charge_duration'] = production_order.get('duration', 0)

    def _clear_production_state(self, building):
        building['charge_percent'] = 1.0
        building.pop('last_charge_time', None)
        building.pop('charge_duration', None)
        building.pop('production_queue', None)

    def _create_builder_production_order(self, building):
        unit_id = 0
        unit_type = 'unit'
        unit_metadata = self.game.object_collection.get_object_metadata(unit_type, unit_id) or {}
        unit_name = unit_metadata.get('name', 'Builder')

        return {
            'action': 'builder_unit',
            'unit_type': unit_type,
            'unit_id': unit_id,
            'cost': 250,
            'duration': self._get_builder_production_duration(building),
            'name': unit_name,
            'thumbnail_name': f"{unit_name}_mini",
        }

    def _get_builder_production_duration(self, building):
        metadata = self.game.object_collection.get_object_metadata(building['type'], building['id'])
        if not metadata:
            return self.default_production_duration
        return metadata.get('properties', {}).get('cooldown', self.default_production_duration)

    def _find_builder_spawn_tile(self, building):
        hq_x, hq_y = building['x'], building['y']
        excluded_tiles = {
            (hq_x, hq_y),
            (hq_x - 1, hq_y),
            (hq_x + 1, hq_y),
            (hq_x, hq_y + 1),
        }

        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                tile_x, tile_y = hq_x + dx, hq_y + dy
                if (tile_x, tile_y) in excluded_tiles:
                    continue

                if not any(obj['x'] == tile_x and obj['y'] == tile_y for obj in self.game.objects):
                    return tile_x, tile_y

        return None
