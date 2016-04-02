#!/bin/python

import math
import random
import time
import numpy

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

from textures import *

from gletools import (
    Projection, Framebuffer, Texture,
    interval, quad, Group, Matrix,
)
from gletools.gl import *

from voxtools import sectorize
from voxtools import normalize
from voxtools import cube_vertices

import yaml
import config


class Model(object):

    def __init__(self):

        '''
        Some good info on pyglet batch processing 
        https://pyglet.readthedocs.org/en/pyglet-1.2-maintenance/api/pyglet/pyglet.graphics.html
        '''
        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        self._initialize()

    def _initialize(self):
        """ Initialize the world by placing all the blocks.

        """
        n = config.WORLD_SIZE  # 1/2 width and height of world
        s = 1  # step size
        y = 1  # initial y height
        g = 4 # ground depth

        verts = [] # all the vertecies that form the terrain

        o = n - 10

        # generate home island
        t = GRASS
        a = 0 # x pos
        b = 0 # z pos
        c = 2 # y pos
        h = 18 # depth
        s = 8 # side length
        d = 1 # how quickly to taper
        t = GRASS

        verts.append(self.home_island(a,b,c,h,s,d,t)) # adds vertex coords to main vert list

        # generate derpleton
        self.add_block((1, 0, 0), HEAD, immediate=False)
        self.add_block((1, -1, 0), BODY, immediate=False)

        # generate clouds
        for _ in xrange(24):
            t= CLOUD
            a,b,c,h,s,d = self.terrain_vals(
                n, # 1/2 height/width of world
                0, # subtract this number from n
                1, # min height
                2, # max height
                1, # min 2 * s is the side length
                6, # max 2 * s is the side length
                1, # min taper
                2, # max taper
                )
            verts.append(self.cluster_cloud(a,b,c,h,s,d,t)) # adds vertex coords to main vert list

        # generate random islands
        for _ in xrange(12):
            t = GRASS
            a,b,c,h,s,d = self.terrain_vals(
                n,  # a = 1/2 height/width of world
                0,  # b = subtract this number from n
                24, # c = min height
                96, # h = max height
                12, # s = min 2 * s is the side length
                18, # s = max 2 * s is the side length
                1,  # d = min taper
                2,  # d = max taper
                )
            verts.append(self.cluster_island(a,b,c,h,s,d,t)) # adds vertex coords to main vert list

        self.place_blocks(verts)

    def place_blocks(self, verts):
        for l in verts: # iterates through vertex coords and places blocks
            for i in l:
                self.add_block(tuple(i[:-1]), i[-1],immediate=False)


    def cluster_cloud(self, a,b,c,h,s,d,t):
        verts = []
        for y in xrange(c, c + h):
            for x in xrange(a - s, a + s + 1):
                for z in xrange(b - s, b + s + 1):
                    for y in xrange(c - s, c + s + 1):
                        if (x - a) ** 2 + (y - c) ** 2 + (z - b) ** 2 > (s + 1) ** 2: # creates hole around coords 0,0,0
                            continue
                        if (x - 0) ** 2 + (y - 0) ** 2 + (z - 0) ** 2 < s *4 ** 2: # creates hole around coords 0,0,0
                            continue
                        verts.append([x, y, z,t]) # creates list of verts with +y incriment
            s -= d  # decrement side length so hills taper off
        return verts

    def cluster_island(self, a,b,c,h,s,d,t):
        verts = []
        for y in xrange(c, c + h):
            for x in xrange(a - s, a + s - 1):
                for z in xrange(b - s, b + s - 1):
                    if (x - a) ** 2 + (z - b) ** 2 > (s - 1) ** 2: # creates hole around coords 0,0,0
                        continue
                    if (x - 0) ** 2 + (y - 0) ** 2 + (z - 0) ** 2 < s *4 ** 2: # creates hole around coords 0,0,0
                        continue
                    verts.append([x, -y, z,t]) # creates list of verts with -y incriment
            s -= d  # decrement side length so hills taper off
            t = DIRT
        return verts

    def home_island(self, a,b,c,h,s,d,t):
        verts = []
        for y in xrange(c, c + h):
            for x in xrange(a - s, a + s - 1):
                for z in xrange(b - s, b + s - 1):
                    if (x - a) ** 2 + (z - b) ** 2 > (s - 1) ** 2: # creates hole around coords 0,0,0
                        continue
                    verts.append([x, -y, z,t]) # creates list of verts with -y incriment
            s -= d  # decrement side length so hills taper off
            t = DIRT
        return verts


    def terrain_vals(self,n,n0,h1,h2,s1,s2,d1,d2):
        """
        Generates the base variables for creating vertex clusters
        for terrain
        """
        o = n - n0
        a = random.randint(-o, o) # x position
        b = random.randint(-o, o) # z position
        c = random.randint(-o, o) # y base
        h = random.randint(h1, h2)  # depth
        s = random.randint(s1, s2)  # 2 * s is the side length
        d = random.randint(d1, d2) # how quickly to taper
        return a,b,c,h,s,d

    def hit_test(self, position, vector, max_distance):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 3
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, texture, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.

        """
        self.type = 'none'
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    def show_block(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)

    def _show_block(self, position, texture):
        """ Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.

        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def hide_block(self, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        """ Private implementation of the 'hide_block()` method.

        """
        self._shown.pop(position).delete()

    def show_sector(self, sector):
        """ Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector):
        """ Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before, after):
        """ Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.

        """
        before_set = set()
        after_set = set()
        pad = 4
        for dx in xrange(-pad, pad + 1):
            for dy in [0]:  # xrange(-pad, pad + 1):
                for dz in xrange(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.

        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.

        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.clock()

        while self.queue and time.clock() - start < 1.0 / config.TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.

        """
        while self.queue:
            self._dequeue()
