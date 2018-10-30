# These are things to students should do and will not be uploaded to github
# Functions that do these things are in helpers.py
# TODO: create an object for a linkage
# TODO: create an object for a node
# TODO: create a parser for the data file
# TODO: calculate the state of the links (fsolve system)

# Things I need to do
# DONE: Create a data file format
# TODO: OpenGL drawer for the linkage state matrix
# TODO: precalc all states
# TODO: stop at lockup
# TODO: A way to actuate the system (change the driven member)
# TODO:

from OpenGL.GL import *
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QOpenGLWidget, QApplication

# example data for graphing. not to be used as actual data.
import helpers


# Basics of OpenGL taken from:
# http://trevorius.com/scrapbook/uncategorized/part-1-drawing-with-pyopengl-using-moden-opengl-buffers/
# https://pythonprogramming.net/opengl-rotating-cube-example-pyopengl-tutorial/
class LinkageOpenGLWidget(QOpenGLWidget):
    def __init__(self, linkage_data):
        super(LinkageOpenGLWidget, self).__init__()
        self.__timer = None
        self.__vao = None

        self.linkage_data = linkage_data

    def initializeGL(self):
        # set the RGBA values of the background
        glClearColor(0.1, 0.2, 0.3, 1.0)
        # set a timer to redraw every 1/60th of a second
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.repaint)  # make it repaint when triggered
        self.__timer.start(1000 / 60)  # make it trigger every 1000/60 milliseconds

        # set up for drawing lines (really narrow rectangles because that's how OpenGL rolls
        positions = (0, 0, 1, 0, 0, 1, 1, 1)
        elements = (0, 1, 2, 1, 3, 2)

        # generate a vertex array object so we can easily draw the resulting mesh later
        self.__vao = glGenVertexArrays(1)
        # enable the vertex array before doing anything else, so anything we do is captured in the VAO context
        glBindVertexArray(self.__vao)
        # generate 2 buffers, 1 for positions, 1 for elements. this is memory on the GPU that our model will be saved in.
        bufs = glGenBuffers(2)
        # set the first buffer for the main vertex data, that GL_ARRAY_BUFFER indicates that use case
        glBindBuffer(GL_ARRAY_BUFFER, bufs[0])
        # upload the position data to the GPU
        # some info about the arguments:
        # GL_ARRAY_BUFFER: this is the buffer we are uploading into, that is why we first had to bind the created buffer, else we'd be uploading to nothing
        # sizeof(ctypes.c_float) * len(positions): openGL wants our data as raw C pointer, and for that it needs to know the size in bytes.
        # the ctypes module helps us figure out the size in bytes of a single number, then we just multiply that by the array length
        # (ctypes.c_float * len(positions))(*positions): this is a way to convert a python list or tuple to a ctypes array of the right data type
        # internally this makes that data the right binary format
        # GL_STATIC_DRAW: in OpenGL you can specify what you will be doing with this buffer, static means draw it a lot but never access or alter the data once uploaded.
        # I suggest changing this only when hitting performance issues at a time you are doing way more complicated things. In general usage static is the fastest.
        glBufferData(GL_ARRAY_BUFFER, sizeof(ctypes.c_float) * len(positions),
                     (ctypes.c_float * len(positions))(*positions), GL_STATIC_DRAW)
        # set the second buffer for the triangulation data, GL_ELEMENT_ARRAY_BUFFER indicates the use here
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, bufs[1])
        # upload the triangulation data
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(ctypes.c_uint) * len(elements),
                     (ctypes.c_uint * len(elements))(*elements), GL_STATIC_DRAW)
        # because the data is now on the GPU, our python positions & elements can be safely garbage collected hereafter
        # turn on the position attribute so OpenGL starts using our array buffer to read vertex positions from
        glEnableVertexAttribArray(0)
        # set the dimensions of the position attribute, so it consumes 2 floats at a time (default is 4)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)

    def resizeGL(self, width, height):
        # this tells openGL how many pixels it should be drawing into
        glViewport(0, 0, width, height)

    def paintGL(self):
        # empty the screen, setting only the background color
        # the depth_buffer_bit also clears the Z-buffer, which is used to make sure
        # objects that are behind other objects actually are not shown drawing
        # a faraway object later than a nearby object naively implies that it will
        # just fill in the pixels with itself, but if there is already an object there
        # the depth buffer will handle checking if it is closer or not automatically
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # the openGL window has coordinates from (-1,-1) to (1,1), so this fills in
        # the top right corner with a rectangle. The default color is white.
        # glRecti(0, 0, 1, 1)

        # enable the vertex array we initialized, it will bind the right buffers in the background again
        glBindVertexArray(self.__vao)
        # draw triangles based on the active GL_ELEMENT_ARRAY_BUFFER
        # that 6 is the element count, we can save the len(elements) in initializeGL in the future
        # that None is because openGL allows us to supply an offset for what element to start drawing at
        # (we could only draw the second triangle by offsetting by 3 indices for example)
        # problem is that the data type for this must be None or ctypes.c_void_p.
        # In many C++ example you will see just "0" being passed in
        # but in PyOpenGL this doesn't work and will result in nothing being drawn.
        glDrawElements(GL_LINES, 6, GL_UNSIGNED_INT, None)

    def shape(self):
        # glBegin(GL_LINES)
        # for edge in edges:
        #     for vertex in edge:
        #         glVertex3fv(vertices[vertex])
        # glEnd()
        pass


def main():
    linkage_data = helpers.Linkage(r'linkageData.txt')
    linkage_data.parse_data()
    # for i in linkage_data.nodes:
    #     print(i)
    print(linkage_data)
    app = QApplication([])
    widget = LinkageOpenGLWidget(linkage_data)
    widget.resizeGL(100, 100)
    widget.show()
    app.exec_()


if __name__ == '__main__':
    # app = QApplication([])
    # widget = LinkageOpenGLWidget()
    # widget.show()
    # app.exec_()
    main()
