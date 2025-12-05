#!/usr/bin/env -S uv run --script


import sys

import numpy as np
import OpenGL.GL as gl
from ncca.ngl import (
    FirstPersonCamera,
    Primitives,
    Prims,
    ShaderLib,
    Transform,
    VAOFactory,
    VAOType,
    Vec3,
    VertexData,
    look_at,
    perspective,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGL import QOpenGLWindow
from PySide6.QtWidgets import QApplication

from models.emitter import Emitter


class MainWindow(QOpenGLWindow):
    def __init__(self):
        super().__init__()
        self.setTitle("PyNGL Demo")
        self.animate: bool = True
        self.keys_pressed = set()
        self.rotate: bool = False
        self.original_x_position: int = 0
        self.original_y_position: int = 0

    def initializeGL(self):
        gl.glClearColor(0.4, 0.4, 0.4, 1.0)
        ShaderLib.load_shader("Pass", "shaders/Vertex.glsl", "shaders/Fragment.glsl")
        ShaderLib.use("Pass")
        self.camera = FirstPersonCamera(Vec3(0, 5, 20), Vec3(0, 0, 0), Vec3(0, 1, 0), 45.0)
        self.emitter = Emitter(Vec3(0, 0, 0), 5000, 2500, 200, (30, 200))
        self.startTimer(16)

        # GL settings
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_MULTISAMPLE)

        # Create a multi buffer
        self.vao = VAOFactory.create_vao(VAOType.MULTI_BUFFER, gl.GL_POINTS)

        with self.vao:
            data = VertexData(data=[], size=0)
            self.vao.set_data(data, index=0)  # Index here is the buffer position
            self.vao.set_data(data, index=1)  # Index here is the buffer color

    def resizeGL(self, w: int, h: int):
        ratio = self.devicePixelRatio()
        self.camera.set_projection(45.0, (w * ratio / h * ratio), 0.05, 200)

    def keyReleaseEvent(self, event):
        self.keys_pressed.discard(event.key())
        self.update()

    def keyPressEvent(self, event):
        self.keys_pressed.add(event.key())

        match event.key():
            case Qt.Key.Key_Escape:
                self.close()
            case Qt.Key.Key_W:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            case Qt.Key.Key_S:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
            case Qt.Key.Key_A:
                self.animate = self.animate is not True
            case Qt.Key.Key_1:
                self.emitter.update(0.01)
        self.update()

    def _process_camera_movements(self):
        x_dir = 0.0
        y_dir = 0.0

        for key in self.keys_pressed:
            if key == Qt.Key_Left:
                y_dir = -1.0
            elif key == Qt.Key_Right:
                y_dir = 1.0
            elif key == Qt.Key_Up:
                x_dir = 1.0
            elif key == Qt.Key_Down:
                x_dir = -1.0

        if x_dir != 0.0 or y_dir != 0.0:
            self.camera.move(x_dir, y_dir, 0.5)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glViewport(0, 0, self.width(), self.height())
        gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)

        self._process_camera_movements()

        ShaderLib.set_uniform("MVP", self.camera.get_vp())

        with self.vao:
            position_size = np.concatenate([self.emitter.position, self.emitter.size[:, np.newaxis]], axis=1)

            self.vao.set_data(VertexData(data=position_size.flatten(), size=position_size.nbytes), index=0)
            self.vao.set_vertex_attribute_pointer(0, 4, gl.GL_FLOAT, 0, 0)

            self.vao.set_data(VertexData(data=self.emitter.color.flatten(), size=self.emitter.color.nbytes), index=1)
            self.vao.set_vertex_attribute_pointer(1, 3, gl.GL_FLOAT, 0, 0)

            self.vao.set_num_indices(len(self.emitter.position))
            self.vao.draw()

    def timerEvent(self, event):
        if self.animate:
            self.emitter.update(0.01)
            self.update()

    def mousePressEvent(self, event):
        position = event.position()

        if event.button() == Qt.LeftButton:
            self.original_x_position = position.x()
            self.original_y_position = position.y()
            self.rotate = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rotate = False

    def mouseMoveEvent(self, event):
        if self.rotate and event.buttons() == Qt.LeftButton:
            position = event.position()
            diff_x = position.x() - self.original_x_position
            diff_y = position.y() - self.original_y_position

            self.original_x_position = position.x()
            self.original_y_position = position.y()
            self.camera.process_mouse_movement(diff_x, diff_y)
            self.update()


if __name__ == "__main__":
    app = QApplication()
    format = QSurfaceFormat()
    format.setMajorVersion(4)
    format.setMinorVersion(6)  # Change it to 1 on a Mac
    format.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(format)

    print(f"{format.profile()} OpenGL {format.majorVersion()} {format.minorVersion()}")
    win = MainWindow()
    win.resize(1024, 720)
    win.show()
    sys.exit(app.exec())
