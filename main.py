# These are things to students should do and will not be uploaded to github
# Functions that do these things are in FourBar.py
# DONE: create an object for a node
# TODO: Fix the node object (coordinates as 1 property)
# DONE: create an object for a linkage
# DONE: create a parser for the data file
# DONE: calculate the state of the links (fsolve system)

# Things I need to do
# DONE: make a fourbar movie happen ASAP
# TODO: Update data file format
# DONE: OpenGL drawer for the linkage state matrix
# DONE: precalc all states
# DONE: stop at lockup (sort of done. ValueError will be raised. It seems like fsolve plows through the optimization.)
# DONE: A way to actuate the system (change the driven member) changes by del_theta each call to calc_motion
# DONE: Take a list of points of the fourbar nodes and draw lines (use Dela's examples/UI)
# frame number tells how many theta step away from staring theta
# TODO: add movable and fixed to the data file
# TODO: add ability to draw svg like graphics for coupler/statics (stretch right now)
# TODO: add coupler point of interest
# TODO: add tracing of coupler poi


import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from PyQt5.QtWidgets import QDialog, QApplication

# DONE: actually use the code the students would write
import FourBar
from OpenGL_2D_class import gl2D
from OpenGL_2D_ui import Ui_Dialog


class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Dialog()
        # setup the GUI
        self.ui.setupUi(self)

        # define any data (including object variables) your program might need
        self.showlabels = True

        # self.circle1x = -1
        # self.circle1y = -0.5
        # self.circle1radius = 0.2
        #
        # self.save_circle1x = 0
        # self.save_circle1y = 0
        #
        # self.circle2x = -1
        # self.circle2y = 2
        # self.circle2radius = 0.15

        # create and setup the GL window object
        self.glwindow1 = None
        self.setupGLWindows()

        # and define any Widget callbacks or other necessary setup
        self.assign_widgets()

        # get linkage data and objects set up
        self.linkage_data = None
        self.setup_linkage_data()
        self.vertexlist = list()
        # make sure given data is good by calculating initial state
        # will raise ValueError if it is not solve. fsolve does not raise an error
        self.calc_linkage_motion()
        self.draw_bar_list = self.vertexlist[0]

        # show the GUI
        self.show()

    def assign_widgets(self):  # callbacks for Widgets on your GUI
        self.ui.pushButton_Exit.clicked.connect(self.ExitApp)
        self.ui.pushButton_Animate.clicked.connect(self.StartAnimation)
        self.ui.pushButton_StopAnimation.clicked.connect(self.StopAnimation)
        self.ui.pushButton_ResumeAnimation.clicked.connect(self.ResumeAnimation)
        self.ui.horizontalSlider_zoom.valueChanged.connect(self.glZoomSlider)
        self.ui.horizontalSlider_rotate.valueChanged.connect(self.glRotateSlider)
        self.ui.checkBox_Dragging.stateChanged.connect(self.DraggingToggle)

    # Widget callbacks start here

    def glZoomSlider(self):  # I used a slider to control GL zooming
        zoomval = float((self.ui.horizontalSlider_zoom.value()) / 200 + 0.25)
        self.glwindow1.glZoom(zoomval)  # set the zoom value
        self.glwindow1.glUpdate()  # update the GL image

    def glRotateSlider(self):  # I used a slider to control GL rotation
        angle = -float(self.ui.horizontalSlider_rotate.value())
        self.glwindow1.glRotate(angle, 0.5, 0.5)  # set the rotation angle and centerpoint
        self.glwindow1.glUpdate()  # update the GL image

    def DraggingToggle(self):  # used a checkbox to Enable GL Dragging
        if self.ui.checkBox_Dragging.isChecked():  # start dragging
            # put locations of "draggable" things into a  list
            draglist = [[self.circle1x, self.circle1y],
                        [self.circle2x, self.circle2y]]
            near = 0.1  # define an acceptable mouse distance for dragging
            self.glwindow1.glStartDragging(self.DraggingCallback, draglist, near, handlesize=0.06, handlewidth=3,
                                           handlecolor=[1, 0, 0])

        else:  # stop dragging
            self.glwindow1.glStopDragging()

    def StartAnimation(self):  # a button to start GL Animation
        # a playlist is a list values defining the look of the picture for
        # each FRAME in the animation.

        nframes = len(self.vertexlist)
        frames = np.linspace(0, nframes - 1, nframes)

        self.glwindow1.glStartAnimation(self.AnimationCallback, frames, reverse=True, repeat=False)

    def StopAnimation(self):  # a button to Stop GL Animati0n
        self.glwindow1.glStopAnimation()

    def ResumeAnimation(self):  # a button to Resume GL Animation
        self.glwindow1.glResumeAnimation()

    def ExitApp(self):
        app.exit()

    # Setup OpenGL Drawing and Viewing

    def setupGLWindows(self):  # setup all GL windows
        # send it the   GL Widget     and the drawing Callback function
        self.glwindow1 = gl2D(self.ui.openGLWidget, self.DrawingCallback)

        # set the drawing space:    xmin  xmax  ymin   ymax
        self.glwindow1.setViewSize(-3, 3, -1, 3, allowDistortion=False)

        # Optional: Setup GL Mouse Functionality
        self.ui.openGLWidget.installEventFilter(self)  # to read mouse events
        self.ui.openGLWidget.setMouseTracking(True)  # to enable mouse events

        # OPTIONAL: to display the mouse location  - the name of the TextBox
        self.glwindow1.glMouseDisplayTextBox(self.ui.MouseLocation)

    def eventFilter(self, source, event):  # allow GL to handle Mouse Events
        self.glwindow1.glHandleMouseEvents(event)  # let GL handle the event
        return super(QDialog, self).eventFilter(source, event)

    def DrawingCallback(self):
        # this is what actually draws the initial picture
        # using data to control what is drawn

        # range is the thetas of interest

        # call DrawBars
        self.DrawBars()

        # if dragging, let GL show dragging handles
        self.glwindow1.glDraggingShowHandles()

    def AnimationCallback(self, frame, nframes):
        # a callback function for frames of animation
        # then, call glUpdate() to update the image
        self.draw_bar_list = self.vertexlist[int(frame)]
        # change object properties of each node here
        app.processEvents()  # absolutely required!!!

    def DraggingCallback(self, x, y, draglist, index):
        # TODO: Change for linkage nodes
        pass
        # if index == 0:  # mouse near circle 1
        #     self.circle1x, self.circle1y = [x, y]  # change circle 1 data
        #     draglist[index] = [x, y]  # save both x and y back to the draglist
        #
        # if index == 1:  # mouse near circle 2 ... only change the x-value
        #     self.circle2x = x  # only change the  x-value for circle 2
        #     draglist[index][0] = x  # only save the x value to the draglist
        # end method

    def DrawBars(self):
        # Draw some lines
        # Set color and line width
        glColor3f(0, 0.90, 0.25)
        glLineWidth(4)
        for i in range(len(self.draw_bar_list) - 1):
            # self.draw_line(self.draw_bar_list[i], self.draw_bar_list[i + 1])
            vertex1 = self.draw_bar_list[i]
            vertex2 = self.draw_bar_list[i + 1]
            glBegin(GL_LINE_STRIP)
            glVertex2f(vertex1[0], vertex1[1])
            glVertex2f(vertex2[0], vertex2[1])
            glEnd()

    def setup_linkage_data(self):
        self.linkage_data = FourBar.Linkage(r'linkageData.txt')
        self.linkage_data.parse_data()

    def calc_linkage_motion(self):
        for x in range(30, 120):
            self.linkage_data.calc_motion(x)
            templist = list()
            for node in self.linkage_data.nodes:
                templist.append([node.x, node.y])
            self.vertexlist.append(templist)

    # def theta_generator(self, x):
    #     self.linkage_data.calc_motion(x)
    #     coords = list
    #     for node in self.linkage_data.nodes:
    #         coords.append([node.x,node.y])
    #     return coords


if __name__ == '__main__':
    # linkage_data = helpers.Linkage(r'linkageData.txt')
    # linkage_data.parse_data()
    # for i in linkage_data.nodes:
    #     print(i)
    # print(linkage_data)
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    main_win = MainWindow()
    sys.exit(app.exec_())
