class Explosion:
    def __init__(self, position, frames, frame_duration=2):
        self.frames = frames
        self.frame_duration = frame_duration  # ticks per frame
        self.current_frame = 0
        self.timer = 0
        self.position = position
        self.finished = False

    def update(self):
        self.timer += 1
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.finished = True

    def render(self, surface, camera_x=0, camera_y=0):
        if not self.finished:
            img = self.frames[self.current_frame]
            # Adjust position for camera offset
            screen_x = self.position[0] - camera_x
            screen_y = self.position[1] - camera_y
            rect = img.get_rect(center=(screen_x, screen_y))
            surface.blit(img, rect)