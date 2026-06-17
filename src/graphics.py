import gpu
from gpu_extras.batch import batch_for_shader



def draw_rect(self, context):
    x1, y1 = self.start
    x2, y2 = self.end

    vertices = [
        (x1, y1),
        (x2, y1),
        (x2, y2),
        (x1, y2),
    ]

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')

    batch = batch_for_shader(shader, 'LINE_LOOP', {"pos": vertices})

    shader.bind()
    shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))

    batch.draw(shader)
