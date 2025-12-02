import random

import numpy as np
from ncca.ngl import Vec3


class Emitter:
    _GRAVITY = np.array((0.0, -9.81, 0.0), dtype=np.float32)

    def __init__(self, position: Vec3, num_particles: int):
        """
        Initialize the emitter and allocate all particle buffers.
        """
        self._position = position
        self._position_np = position.to_numpy()
        self._num_particles = num_particles
        self.position = np.zeros((self._num_particles, 3), dtype=np.float32)
        self.direction = np.zeros((self._num_particles, 3), dtype=np.float32)
        self.color = np.zeros((self._num_particles, 3), dtype=np.float32)
        self.life = np.zeros((self._num_particles,), dtype=int)
        self.max_life = np.zeros((self._num_particles,), dtype=int)
        self.size = np.zeros((self._num_particles,), dtype=np.float32)

        self._init_particles()

    def _init_particles(self):
        """
        Initialize all particles by respawning them once.
        """
        indices = np.arange(self._num_particles)
        self._respawn_particles(indices)

    def _respawn_particles(self, indices):
        """
        Respawn the particles specified by index.

        Args:
            indices (array-like): Indices of particles to reset.
        """
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
        max_life = np.random.randint(10, 51, size=count, dtype=int)
        size = np.full(count, 0.01, dtype=np.float32)

        self.position[index] = positions
        self.direction[index] = directions
        self.color[index] = colors
        self.life[index] = life
        self.max_life[index] = max_life
        self.size[index] = size

    def update(self, dt: float):
        """
        Update all particles for one timestep.
        Integrates velocity, applies gravity, increases size, increments life,
        and respawns expired particles.

        Args:
            dt (float): Delta time.
        """
        self.direction += Emitter._GRAVITY * (dt * 0.5)
        self.position += self.direction * dt
        self.life += 1
        self.size += 0.5

        # Now reset the dead particles
        dead_mask = self.life > self.max_life
        if np.any(dead_mask):
            dead_indices = np.nonzero(dead_mask)[0]
            self._respawn_particles(dead_indices)

    @property
    def num_particles(self):
        return self._num_particles
