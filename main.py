# These are things to students should do and will not be uploaded to github
# Functions that do these things are in FourBar.py
# DONE: create an object for a node
# TODO: Fix the node object (coordinates as 1 property) (it's fine for now)
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
# DONE: frame number tells how many theta step away from staring theta (1 frame = 1 deg right now)
# DONE: add drag points to the drawing.
# DONE: make nodes draggable
# TODO: recalc after moving
# TODO: add movable and fixed to the data file
# TODO: add ability to draw svg like graphics for coupler/statics (stretch right now)
# TODO: add coupler point of interest
# TODO: add tracing of coupler poi


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
        self.calc_linkage_motion(30, 120)
        self.draw_bar_list = self.vertexlist[0]
        self.moved_nodes = False

        # show the GUI
        self.show()

    def assign_widgets(self):  # callbacks for Widgets on your GUI
        self.ui.pushButton_Exit.clicked.connect(self.ExitApp)
        self.ui.pushButton_Animate.clicked.connect(self.StartAnimation)
        self.ui.pushButton_StopAnimation.clicked.connect(self.StopAnimation)
        self.ui.pushButton_PauseResumeAnimation.clicked.connect(self.PauseResumeAnimation)
        self.ui.horizontalSlider_zoom.valueChanged.connect(self.glZoomSlider)
        self.ui.checkBox_Dragging.stateChanged.connect(self.DraggingOnOff)

    # Widget callbacks start here

    def glZoomSlider(self):  # I used a slider to control GL zooming
        zoomval = float((self.ui.horizontalSlider_zoom.value()) / 200 + 0.25)
        self.glwindow1.glZoom(zoomval)  # set the zoom value
        self.glwindow1.glUpdate()  # update the GL image

    def DraggingOnOff(self):  # used a checkbox to Enable GL Dragging
        if self.ui.checkBox_Dragging.isChecked():  # start dragging
            self.StartStopDragging(True)  # StartStopDragging is defined below
        else:  # stop dragging
            self.StartStopDragging(False)

    def StartAnimation(self):  # a button to start GL Animation
        # a playlist is a list values defining the look of the picture for
        # each FRAME in the animation.

        nframes = len(self.vertexlist)
        # frames = np.linspace(0, nframes - 1, nframes)

        # take the currently drawn points and run them through the FourBar.py module
        if self.moved_nodes:
            for i in range(len(self.draw_bar_list)):
                self.linkage_data.nodes[i].x = self.draw_bar_list[i][0]
                self.linkage_data.nodes[i].y = self.draw_bar_list[i][1]
            self.calc_linkage_motion(20, 30)
        self.moved_nodes = False

        self.glwindow1.glStartAnimation(self.AnimationCallback, nframes, reverse=True, repeat=False,
                                        RestartDraggingCallback=self.StartStopDragging)

    def StopAnimation(self):  # a button to Stop GL Animati0n
        self.glwindow1.glStopAnimation()

    def PauseResumeAnimation(self):  # a button to Resume GL Animation
        self.glwindow1.glPauseResumeAnimation()

    def ExitApp(self):
        app.exit()

    # Setup OpenGL Drawing and Viewing

    def setupGLWindows(self):  # setup all GL windows
        # send it the GL Widget and the drawing Callback function
        self.glwindow1 = gl2D(self.ui.openGLWidget, self.DrawingCallback)

        # set the drawing space: xmin, xmax, ymin, ymax
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

        # call DrawBars
        self.DrawBars()

        # if using dragging, let GL show dragging handles
        self.glwindow1.glDraggingShowHandles()

    def AnimationCallback(self, frame: int, nframes: int):
        # a callback function for frames of animation
        # then, call glUpdate() to update the image
        self.draw_bar_list = self.vertexlist[int(frame)]
        # change object properties of each node here
        app.processEvents()  # absolutely required!!!

    def draggingCallback(self, x: float, y: float, draglist: list, i: int):
        # TODO: Change for linkage nodes
        # pass
        # self.linkage_data.nodes[i].x = x
        # self.linkage_data.nodes[i].y = y
        self.draw_bar_list[i] = [x, y]
        self.moved_nodes = True
        # if index == 0:  # mouse near circle 1
        #     self.circle1x, self.circle1y = [x, y]  # change circle 1 data
        #     draglist[index] = [x, y]  # save both x and y back to the draglist
        #
        # if index == 1:  # mouse near circle 2 ... only change the x-value
        #     self.circle2x = x  # only change the  x-value for circle 2
        #     draglist[index][0] = x  # only save the x value to the draglist
        # end method

    def StartStopDragging(self, start: bool):  # needs problem specific customization!
        if start is True:
            draglist = self.draw_bar_list
            near = 0.1  # define an acceptable mouse distance for dragging
            self.glwindow1.glStartDragging(self.draggingCallback, draglist, near,
                                           handlesize=.05, handlewidth=.005, handlecolor=[1, 0, 0])
            self.ui.checkBox_Dragging.setChecked(True)
        elif start is False:
            self.glwindow1.glStopDragging()
            self.ui.checkBox_Dragging.setChecked(False)

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

    def calc_linkage_motion(self, start_theta: int, stop_theta: int):
        for x in range(start_theta, stop_theta):
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
