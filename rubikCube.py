import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import time
from copy import deepcopy

# --- settings ---
WIN_W, WIN_H = 900, 700
CUBIE_SIZE = 0.9        # side length of each small cube
GAP = 0.08              # gap between cubies to see edges
ANIM_SPEED = 360.0      # degrees per second for layer rotation animation

# Colors (RGB, 0..1)
COLORS = {
    'U': (1.0, 1.0, 1.0),   # up - white
    'D': (1.0, 1.0, 0.0),   # down - yellow
    'F': (0.0, 1.0, 0.0),   # front - green
    'B': (0.0, 0.0, 1.0),   # back - blue
    'L': (1.0, 0.5, 0.0),   # left - orange
    'R': (1.0, 0.0, 0.0),   # right - red
    None: (0.12, 0.12, 0.12) # internal / default border
}

# face normal vectors (used as keys)
NORMALS = {
    'U': (0, 1, 0),
    'D': (0, -1, 0),
    'F': (0, 0, 1),
    'B': (0, 0, -1),
    'L': (-1, 0, 0),
    'R': (1, 0, 0)
}

# Helper: rotate a 3D integer vector (x,y,z) 90 degrees around axis 'x','y' or 'z'
def rotate_vec_90(v, axis, clockwise=True):
    x, y, z = v
    if axis == 'x':
        if clockwise:
            return (x, -z, y)
        else:
            return (x, z, -y)
    if axis == 'y':
        if clockwise:
            return (z, y, -x)
        else:
            return (-z, y, x)
    if axis == 'z':
        if clockwise:
            return (-y, x, z)
        else:
            return (y, -x, z)
    return v

# Cubie class: holds position indices (ix,iy,iz) in {-1,0,1} and sticker mapping normal->face_letter
class Cubie:
    def __init__(self, pos):
        self.pos = pos  # tuple of indices (-1/0/1)
        # stickers: dict normal tuple -> face letter (U/D/F/B/L/R) or None
        self.stickers = {}
        ix, iy, iz = pos
        if iy == 1: self.stickers[NORMALS['U']] = 'U'
        if iy == -1: self.stickers[NORMALS['D']] = 'D'
        if iz == 1: self.stickers[NORMALS['F']] = 'F'
        if iz == -1: self.stickers[NORMALS['B']] = 'B'
        if ix == -1: self.stickers[NORMALS['L']] = 'L'
        if ix == 1: self.stickers[NORMALS['R']] = 'R'

    def clone(self):
        c = Cubie(self.pos)
        c.stickers = dict(self.stickers)
        return c

# Create initial cube state: dict mapping (ix,iy,iz) -> Cubie
def create_solved_cube():
    state = {}
    for ix in (-1,0,1):
        for iy in (-1,0,1):
            for iz in (-1,0,1):
                state[(ix,iy,iz)] = Cubie((ix,iy,iz))
    return state

# Convert index coordinates to world coordinates for drawing
def idx_to_world(ix, iy, iz):
    s = CUBIE_SIZE + GAP
    return (ix * s, iy * s, iz * s)

# Draw a single cubie at world position with its stickers
def draw_cubie(cubie):
    ix, iy, iz = cubie.pos
    cx, cy, cz = idx_to_world(ix, iy, iz)
    half = CUBIE_SIZE/2.0

    glPushMatrix()
    glTranslatef(cx, cy, cz)

    # dark body
    glColor3f(0.08, 0.08, 0.08)
    draw_solid_cube(CUBIE_SIZE)

    # stickers
    inset = 0.001
    sticker_thickness = 0.01
    sticker_scale = 0.82
    for normal, face in cubie.stickers.items():
        nx, ny, nz = normal
        color = COLORS.get(face, (0.0,0.0,0.0))
        sx = nx*(half + inset)
        sy = ny*(half + inset)
        sz = nz*(half + inset)

        if abs(nx) == 1:
            u = (0,1,0)
            v = (0,0,1)
        elif abs(ny) == 1:
            u = (1,0,0)
            v = (0,0,1)
        else:
            u = (1,0,0)
            v = (0,1,0)

        ux, uy, uz = u
        vx, vy, vz = v
        su = sticker_scale * half
        sv = sticker_scale * half

        corners = [
            (sx + (-ux - vx)*su, sy + (-uy - vy)*su, sz + (-uz - vz)*su),
            (sx + ( ux - vx)*su, sy + ( uy - vy)*su, sz + ( uz - vz)*su),
            (sx + ( ux + vx)*su, sy + ( uy + vy)*su, sz + ( uz + vz)*su),
            (sx + (-ux + vx)*su, sy + (-uy + vy)*su, sz + (-uz + vz)*su),
        ]

        glColor3f(*color)
        glBegin(GL_QUADS)
        for x,y,z in corners:
            glVertex3f(x, y, z)
        glEnd()

        glColor3f(0,0,0)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        for x,y,z in corners:
            glVertex3f(x, y, z)
        glEnd()
        glLineWidth(1)

    glPopMatrix()

# draw a solid cube centered at origin
def draw_solid_cube(size):
    h = size/2.0
    faces = [
        [(-h,-h,-h), ( h,-h,-h), ( h, h,-h), (-h, h,-h)],
        [( h,-h, h), (-h,-h, h), (-h, h, h), ( h, h, h)],
        [(-h,-h,-h), (-h, h,-h), (-h, h, h), (-h,-h, h)],
        [( h,-h, h), ( h, h, h), ( h, h,-h), ( h,-h,-h)],
        [(-h, h,-h), ( h, h,-h), ( h, h, h), (-h, h, h)],
        [(-h,-h, h), ( h,-h, h), ( h,-h,-h), (-h,-h,-h)]
    ]
    glBegin(GL_QUADS)
    for face in faces:
        for v in face:
            glVertex3f(*v)
    glEnd()

# Logical layer rotation
def rotate_layer(state, axis, coord_value, clockwise=True):
    new_state = {}
    for pos, cubie in state.items():
        ix, iy, iz = pos
        if (axis == 'x' and ix == coord_value) or \
           (axis == 'y' and iy == coord_value) or \
           (axis == 'z' and iz == coord_value):
            new_pos = rotate_vec_90(pos, axis, clockwise)
            new_cubie = Cubie(new_pos)
            new_cubie.stickers = {}
            for normal, face in cubie.stickers.items():
                new_normal = rotate_vec_90(normal, axis, clockwise)
                new_cubie.stickers[new_normal] = face
            new_state[new_pos] = new_cubie
        else:
            new_state[pos] = cubie.clone()
    return new_state

# Animation queue element
class RotationAnim:
    def __init__(self, axis, coord, clockwise):
        self.axis = axis
        self.coord = coord
        self.clockwise = clockwise
        self.angle = 0.0
        self.done = False

# Main
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Rubik's Cube (3x3) Dish Dirin Dirin Mashallah xD")
    gluPerspective(45, (WIN_W/WIN_H), 0.1, 100.0)
    glTranslatef(0.0, 0.0, -14)

    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)   # ← THIS IS THE ONLY FIX! All 6 faces now visible.

    state = create_solved_cube()

    rot_x = -25.0
    rot_y = -30.0
    mouse_down = False
    last_mouse = (0,0)
    clock = pygame.time.Clock()
    current_anim = None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
                last_mouse = event.pos
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
            elif event.type == MOUSEMOTION and mouse_down:
                mx, my = event.pos
                lx, ly = last_mouse
                rot_y += (mx - lx) * 0.4
                rot_x += (my - ly) * 0.4
                last_mouse = event.pos
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                keyname = pygame.key.name(event.key).lower()
                mods = pygame.key.get_mods()
                invert = mods & KMOD_SHIFT
                cw = not invert
                if keyname in ('u','d','l','r','f','b'):
                    mapping = {
                        'u': ('y', 1), 'd': ('y', -1),
                        'l': ('x', -1), 'r': ('x', 1),
                        'f': ('z', 1), 'b': ('z', -1)
                    }
                    axis, coord = mapping[keyname]
                    if current_anim is None:
                        current_anim = RotationAnim(axis, coord, cw)

        # animation
        if current_anim:
            delta = ANIM_SPEED * dt
            current_anim.angle += delta if current_anim.clockwise else -delta
            if abs(current_anim.angle) >= 90.0:
                state = rotate_layer(state, current_anim.axis, current_anim.coord, current_anim.clockwise)
                current_anim = None

        # draw
        glClearColor(0.3, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        if current_anim is None:
            for cubie in state.values():
                draw_cubie(cubie)
        else:
            axis = current_anim.axis
            coord = current_anim.coord
            angle = current_anim.angle
            for pos, cubie in state.items():
                ix, iy, iz = pos
                in_layer = ((axis == 'x' and ix == coord) or
                            (axis == 'y' and iy == coord) or
                            (axis == 'z' and iz == coord))
                if in_layer:
                    glPushMatrix()
                    cx, cy, cz = idx_to_world(ix, iy, iz)
                    glTranslatef(cx, cy, cz)
                    if axis == 'x':
                        glRotatef(angle if current_anim.clockwise else -angle, 1, 0, 0)
                    elif axis == 'y':
                        glRotatef(angle if current_anim.clockwise else -angle, 0, 1, 0)
                    elif axis == 'z':
                        glRotatef(angle if current_anim.clockwise else -angle, 0, 0, 1)
                    temp = cubie.clone()
                    temp.pos = (0,0,0)
                    draw_cubie(temp)
                    glPopMatrix()
                else:
                    draw_cubie(cubie)

        glPopMatrix()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()