# Particle System — NumPy GPU Implementation

This project implements a **high-performance GPU particle system** in Python using:

- **NumPy** for vectorized particle simulation
- **PyOpenGL** for rendering
- **PySide6** (`QOpenGLWindow`) for real-time visualization
- **ncca.ngl** helpers (ShaderLib, VAOFactory, Vec3, etc.)

The emitter updates thousands of particles using vectorized operations and streams the particle attributes (position + color) directly to GPU buffers every frame.

---

```mermaid
classDiagram
    class Emitter {
        - int max_per_frame
        - Tuple[int, int] life_range
        - Vec3 _position
        - ndarray _position_np
        - int _num_particles
        - ndarray position
        - ndarray direction
        - ndarray color
        - ndarray life
        - ndarray max_life
        - ndarray size
        - ndarray alive
        - int max_alive
        + __init__(position, num_particles)
        + _init_particles()
        + _respawn_particles(indices)
        + update(dt)
        + num_particles
    }

    class ParticleSystem {
        <<OpenGL Window>>
        + initializeGL()
        + resizeGL(w,h)
        + paintGL()
        + timerEvent()
    }

    class Vec3 {
        + x
        + y
        + z
        + to_numpy()
        + copy()
    }

    ParticleSystem --> Emitter : owns
    Emitter --> Vec3 : uses
```

## Demo

This section describes the program function by running the `main.py` executable file.

![Particles Numpy](./particles/particles_numpy.gif)
