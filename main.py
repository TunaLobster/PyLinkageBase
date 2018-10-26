# These are things to students should do and will not be uploaded to github
# TODO: create an object for the linkage
# TODO: create a parser for the data file
# TODO: calculate the state of the links (fsolve system)

# Things I need to do
# TODO: Create a data file format
# TODO: OpenGL drawer for the linkage state matrix (precalc all states. stop at lockup.)
# TODO: A way to actuate the system (change the driven member)

import numpy as np
from OpenGL import GL
from PyQt5.QtWidgets import QOpenGLWidget, QApplication


class OpenGLWidget(QOpenGLWidget):
    def initializeGL(self):
        vertices = np.array([0.0, 1.0, -1.0, -1.0, 1.0, -1.0], dtype=np.float32)

        bufferId = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, bufferId)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

    def paintGL(self):
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)


if __name__ == '__main__':
    app = QApplication([])
    widget = OpenGLWidget()
    widget.show()
    app.exec_()
