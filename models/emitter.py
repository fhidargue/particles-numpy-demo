import random
from typing import Tuple

import numpy as np
from ncca.ngl import Vec3


class Emitter:
    _GRAVITY = np.array((0.0, -9.81, 0.0), dtype=np.float32)

    def __init__(
        self, position: Vec3, num_particles: int, max_alive: int, max_per_frame: int, life_range: Tuple[int, int]
    ):
        self.max_per_frame = max_per_frame
        self.life_range = life_range
        self._position = position
        self._position_np = position.to_numpy()
        self._num_particles = num_particles
        self.position = np.zeros((self._num_particles, 3), dtype=np.float32)
        self.direction = np.zeros((self._num_particles, 3), dtype=np.float32)
        self.color = np.zeros((self._num_particles, 3), dtype=np.float32)

        self.life = np.zeros((self._num_particles,), dtype=int)
        self.max_life = np.zeros((self._num_particles,), dtype=int)
        self.size = np.zeros((self._num_particles,), dtype=np.float32)
        self.alive = np.full(self.num_particles, False, dtype=np.bool)
        self.max_alive = max_alive

        self._init_particles()

    def _init_particles(self):
        num_to_create = random.randint(10, 50)
        indices = np.arange(num_to_create)
        self._respawn_particles(indices)

    def _respawn_particles(self, indices):
        # Init particles vectorized
        if len(indices) == 0:
            return

        index = np.asarray(indices, dtype=int)
        count = index.size
        EMIT_DIR = np.array((0.0, 1.0, 0.0), dtype=np.float32)
        SPREAD = 15.0
        rand_pos = np.random.rand(count, 1)

        # Now create a directon vector
        rand_normals = np.random.normal(size=(count, 3))
        norms = np.linalg.norm(rand_normals, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        rand_unit = rand_normals / norms

        # Build a dir
        directions = EMIT_DIR + rand_pos + rand_unit * SPREAD
        directions[:, 1] = np.abs(directions[:, 1])

        # Positions at start from pos
        positions = np.tile(self._position_np.reshape(1, 3), (count, 1))
        colors = np.random.rand(count, 3)
        life = np.zeros(count, dtype=int)
        max_life = np.random.randint(self.life_range[0], self.life_range[1], size=count, dtype=int)
        size = np.full(count, 0.01, dtype=np.float32)

        self.position[index] = positions
        self.direction[index] = directions
        self.color[index] = colors
        self.life[index] = life
        self.max_life[index] = max_life
        self.size[index] = size

    def update(self, dt: float):
        self.direction += Emitter._GRAVITY * (dt * 0.5)
        self.position += self.direction * dt
        self.life += 1
        self.size += 0.1

        # Create new particles if we're not at max alive
        if np.count_nonzero(self.alive) <= self.max_alive:
            num_to_create = random.randint(0, self.max_per_frame)

            # Find the indices of the dead (false) particles
            dead_indices = np.where(self.alive == False)[0]

            # Select num to create from this list
            revive_indices = dead_indices[:num_to_create]

            # Revive them
            self.alive[revive_indices] = True

        # Now reset the dead particles
        dead_mask = self.life > self.max_life
        if np.any(dead_mask) and np.any(self.alive):
            dead_indices = np.nonzero(dead_mask)[0]
            self._respawn_particles(dead_indices)
            self.alive[dead_mask] = False

        print(f"Num alive {np.count_nonzero(self.alive)}")

    @property
    def num_particles(self):
        return self._num_particles
