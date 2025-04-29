import os, sys, math, pdb

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtCore import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# OpenGL libraries (pip install pyOpenGL)
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *
import OpenGL.GL as gl

# numpy libraries
import numpy as np

# scipy libraries
from scipy import linalg

# imageio libraries (pip install imageio)
import imageio
from imageio.v2 import imsave
from imageio.v2 import imread

# Import the class "Ui_MainWindow" from the file "GUI.py"
from GUI3 import Ui_MainWindow

# Import the class "OBJ" from the file "OBJ.py"
from OBJ import OBJ, OBJFastV

import warnings
warnings.filterwarnings("ignore")


####################################################################################################
# The Main Window (GUI)
####################################################################################################
class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)  # The 2 lines here are always presented like this
        QMainWindow.__init__(self, parent)  # Just to initialize the window

        # All the elements from our GUI are added in "ui"
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Default param
        self.InputModelLoaded = False
        self.InputTextureLoaded = False
        self.InputListCreated = False
        self.InputTexturePath = []
        self.InputModel = []
        self.InputTextureDim = 256

        self.TargetModelLoaded = False
        self.TargetTextureLoaded = False
        self.TargetListCreated = False
        self.TarTexturePath = []
        self.TarModel = []


        self.bg_color = 0.0
        self.Root = {}
        self.Tval = self.Gval = 0
        self.P_Tval = self.P_Gval = 0
        self.Tx = self.Ty = 0
        self.Tz = 1
        self.r_mode = self.c_mode = "Faces"
        self.bg_color = 0.0
        self.LeftXRot = self.LeftYRot = 0
        self.b_Ready = False
        self.Updated = False
        self.b_ProcessDone = self.b_Process2Done = self.b_Ready = self.PCA_done = False
        self.old_Gval = self.old_Tval = 0

        # Add a GLWidget (will be used to display our 3D object)
        self.glWidget = GLWidget(parent=self)
        # Add the widget in "frame_horizontalLayout", an element from the GUI
        self.ui.frame_horizontalLayout.addWidget(self.glWidget)

        # Update Widgets
        # Connect a signal "updated" between the GLWidget and the GUI, just to have a link between the 2 classes
        self.glWidget.updated.connect(self.updateFrame)

        # RadioButton (Rendering Mode)
        # Connect the radiobutton to the function on_rendering_button_toggled
        # It will be used to switch between 3 modes, full/wire model or cloud of points
        self.ui.rbFaces.toggled.connect(self.rendering_button_toggled)
        self.ui.rbPoints.toggled.connect(self.rendering_button_toggled)
        self.ui.rbWire.toggled.connect(self.rendering_button_toggled)

        # RadioButton (Background Color)
        # Connect the radiobutton to the function on_bgcolor_button_toggled
        self.ui.rbWhite.toggled.connect(self.bgcolor_button_toggled)
        # Just an example to change the background of the 3D frame
        self.ui.rbBlack.toggled.connect(self.bgcolor_button_toggled)

        # Buttons
        # Connect the button to the function LoadFileClicked (will read the 3D file)
        self.ui.LoadFile.clicked.connect(self.LoadFileClicked)
        # Connect the button to the function ProcessClicked (will process PCA)
        self.ui.Process.clicked.connect(self.ProcessClicked)
        # Connect the button to the function SaveOBJ (will write a 3D file)
        self.ui.exportResult.clicked.connect(self.SaveOBJ)

        # Sliders
        # Connect the slider to the function T_SliderValueChange
        self.ui.Tslider.valueChanged.connect(self.T_SliderValueChange)
        # Connect the slider to the function G_SliderValueChange
        self.ui.Gslider.valueChanged.connect(self.G_SliderValueChange)

        # Disable buttons/sliders before PCA
        self.ui.Tslider.setEnabled(False)
        self.ui.Gslider.setEnabled(False)

    def LoadFileClicked(self):
        try:
            # To display a popup window that will be used to select a file (.obj or .png)
            # The .obj and .png should have the same name!
            self.myFile = QFileDialog.getOpenFileName(None, 'OpenFile', "", "3D object(*.obj);;Texture(*.png)")
            self.myPath = self.myFile[0]
            # If the extension is .obj (or .png), will remove the 4 last characters (== the extension)
            self.GlobalNameWithoutExtension = self.myPath[:-4]
            self.FileNameWithExtension = QFileInfo(self.myFile[0]).fileName()  # Just the filename
            if self.myFile[0] == self.myFile[1] == '':
                # No file selected or cancel button clicked - so do nothing
                pass
            else:
                self.InputModel = self.TarModel = []
                self.InputModelLoaded = self.InputTextureLoaded = False
                self.InputTexturePath = self.GlobalNameWithoutExtension + ".png"

                # Will use the class OBJ to read our 3D file and extract everything
                self.InputModel = OBJ(self.GlobalNameWithoutExtension + ".obj")

                imsave("TarTexture" + ".png", imread(self.InputTexturePath))

                self.TarTexturePath = '/'.join(self.myPath.split('/')[:-1]) + '/TarTexture.png'
                self.TarModel = self.InputModel

                # We read the 2 files, so we can now set the boolean value to True
                # (the GLWidget will now display it automatically because of the 2 variables used there)
                self.InputModelLoaded = self.InputTextureLoaded = True
                self.Updated = True
                self.PCA_done = False
                self.glWidget.update()

        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            print(self.myFile)
        except ValueError:
            print("Value Error.")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def ProcessClicked(self):

        # For the bonus task, you will need to call the thread instead of the PCA function

        self.PCA_Tex()  # Run the function to do the PCA on textures
        self.b_ProcessDone = True
        print("PCA TEX DONE")

        self.PCA_Geo()  # Run the function to do the PCA on vertices
        self.b_Process2Done = True
        print("PCA GEO DONE")

        self.PCA_done = True

        # Unlock and prepare sliders
        self.ui.Tslider.blockSignals(True)
        self.ui.Tslider.setValue(0)
        self.T_SliderValueChange(0)
        self.ui.Tslider.blockSignals(False)
        self.ui.Tslider.setEnabled(True)
        S = self.checkSign(round(self.Root['Tex']['WTex'][0]), round(self.Root['Tex']['WTex'][1]))

        Tmin = round (S * self.Root['Tex']['WTex'][0])
        Tmax = round (S * self.Root['Tex']['WTex'][1])
        self.ui.Tslider.setRange(Tmin, Tmax)

        self.ui.Gslider.blockSignals(True)
        self.ui.Gslider.setValue(0)
        self.G_SliderValueChange(0)
        self.ui.Gslider.blockSignals(False)
        self.ui.Gslider.setEnabled(True)
        Gmin = round(self.Root['models']['WGeo'][0])
        Gmax = round(self.Root['models']['WGeo'][1])
        self.ui.Gslider.setRange(Gmin, Gmax)

    def PCA_Tex(self):
        try:
            # Load textures (model1.png and model2.png)
            img1 = imageio.v2.imread("model1.png").astype(np.float32)
            img2 = imageio.v2.imread("model2.png").astype(np.float32)

            # Flatten the images for PCA
            img1_flat = img1.reshape(-1)
            img2_flat = img2.reshape(-1)

            # Combine the two textures into a single matrix
            images = np.vstack([img1_flat, img2_flat])

            # Compute the mean texture
            mu = np.mean(images, axis=0)

            # Center the data by subtracting the mean
            ma_data = images - mu

            # Perform PCA using SVD
            e_faces, sigma, v = np.linalg.svd(ma_data.T, full_matrices=False)

            # Compute the PCA weights
            weights = np.dot(ma_data, e_faces)

            # Save results
            self.Root['Tex'] = {
                'VrTex': e_faces.T,
                'XmTex': mu,
                'WTex': [weights[:, 0].min(), weights[:, 0].max()]
            }
        except Exception as e:
            print("PCA_Tex Error:", e)

    def PCA_Geo(self):
        try:
            # Extract vertices from model1.obj and model2.obj
            vertices1 = np.array(OBJFastV("model1.obj").vertices)
            vertices2 = np.array(OBJFastV("model2.obj").vertices)

            # Flatten vertices
            vertices1_flat = vertices1.flatten()
            vertices2_flat = vertices2.flatten()

            # Combine vertices for PCA
            obj_v_list = np.vstack([vertices1_flat, vertices2_flat])

            # Compute the mean geometry
            mu_v = np.mean(obj_v_list, axis=0)

            # Center the data
            ma_data_v = obj_v_list - mu_v

            # Perform PCA using SVD
            e_faces_v, sigma_v, v_v = np.linalg.svd(ma_data_v.T, full_matrices=False)

            # Compute the PCA weights
            weights_v = np.dot(ma_data_v, e_faces_v)

            # Save results
            self.Root['models'] = {
                'VrGeo': e_faces_v.T,
                'XmGeo': mu_v,
                'WGeo': [weights_v[:, 0].min(), weights_v[:, 0].max()]
            }
        except Exception as e:
            print("PCA_Geo Error:", e)

    def T_SliderValueChange(self, value):
        try:
            self.Tval = value
            if self.b_ProcessDone:
                # Update texture based on PCA
                mu = self.Root['Tex']['XmTex']
                E = self.Root['Tex']['VrTex'][0]
                new_texture = mu + value * E
                new_texture = new_texture.reshape(256, 256, 4).astype(np.uint8)

                # Save new texture
                self.TarTexture = new_texture
                imageio.v2.imsave("TarTexture.png", self.TarTexture)
        except Exception as e:
            print("T_SliderValueChange Error:", e)

    def G_SliderValueChange(self, value):
        try:
            self.Gval = value
            if self.b_Process2Done:
                # Update geometry based on PCA
                mu = self.Root['models']['XmGeo']
                E = self.Root['models']['VrGeo'][0]
                new_geometry = mu + value * E

                # Reshape geometry to original format
                arr_3d = new_geometry.reshape((-1, 3))

                # Update vertices in model
                self.TarModel.vertices = [
                    (float(arr_3d[i, 0]), float(arr_3d[i, 1]), float(arr_3d[i, 2]))
                    for i in range(arr_3d.shape[0])
                ]
        except Exception as e:
            print("G_SliderValueChange Error:", e)

    def SaveOBJ(self):
        try:
            output_file = "ModifiedModel.obj"
            with open(output_file, "w") as file:
                # Write vertices
                for v in self.TarModel.vertices:
                    file.write(f"v {v[0]} {v[1]} {v[2]}\n")

                # Copy other data from the original file
                with open("model1.obj", "r") as original_file:
                    for line in original_file:
                        if not line.startswith("v "):
                            file.write(line)
            print(f"Saved modified model as {output_file}")
        except Exception as e:
            print("SaveOBJ Error:", e)

    def checkSign(self, W1, W2):
        ## Check the weight, to know which one is negative/positive
        ## Important for the sliders to have the - on the left and + on the right
        if W1 < 0:
            res = 1
        else:
            res = -1
        return res

    def rendering_button_toggled(self):
        radiobutton = self.sender()

        if radiobutton.isChecked():
            self.r_mode = radiobutton.text()  # Save "Faces" or "Points" in r_mode
        self.Updated = True
        self.glWidget.update()

    def bgcolor_button_toggled(self):
        radiobutton = self.sender()  # Catch the click
        if radiobutton.isChecked():  # Will check which button is checked
            # Will store and use the text of the radiobutton
            # to store a value in the variable "bg_color" that will be used in the GLWidget
            color = radiobutton.text()
            if color == "White":
                self.bg_color = 1.0
            elif color == "Black":
                self.bg_color = 0.0

    def updateFrame(self):
        self.glWidget.update()

####################################################################################################
# The OpenGL Widget --- it's normally not needed to touch this part especially paintGL
####################################################################################################
class GLWidget(QGLWidget):
    updated = pyqtSignal(int)  # pyqtSignal is used to allow the GUI and the OpenGL widget to sync
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    def __init__(self, parent):
        super(GLWidget, self).__init__(parent)
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.lastPos = QPoint()

        self.Tx = self.Ty = 0
        self.Tz = 1
        self.LeftXRot = self.LeftYRot = 0

        self.parent = parent

        self.InputListCreated = False
        self.TargetListCreated = False

    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        self.tex = glGenTextures(1)

    def paintGL(self):

        self.InputModelLoaded = self.parent.InputModelLoaded
        self.InputTextureLoaded = self.parent.InputTextureLoaded
        # self.InputListCreated = self.parent.InputListCreated
        self.InputTexturePath = self.parent.InputTexturePath
        self.InputModel = self.parent.InputModel
        self.InputTextureDim = self.parent.InputTextureDim

        self.TargetModelLoaded = self.parent.TargetModelLoaded
        self.TargetTextureLoaded = self.parent.TargetTextureLoaded
        # self.TargetListCreated = self.parent.TargetListCreated
        self.TarTexturePath = self.parent.TarTexturePath
        self.TarModel = self.parent.TarModel

        self.bg_color = self.parent.bg_color
        self.Root = self.parent.Root
        self.Tval = self.parent.Tval
        self.Gval = self.parent.Gval
        self.P_Tval = self.parent.P_Tval
        self.P_Gval = self.parent.P_Gval
        # self.Tx = self.parent.Tx
        # self.Ty = self.parent.Ty
        # self.Tz = self.parent.Tz

        self.r_mode = self.parent.r_mode
        self.c_mode = self.parent.c_mode
        self.bg_color = self.parent.bg_color
        # self.LeftXRot = self.parent.LeftXRot
        # self.LeftYRot = self.parent.LeftYRot
        self.b_Ready = self.parent.b_Ready
        self.Updated = self.parent.Updated
        self.b_ProcessDone = self.parent.b_ProcessDone
        self.b_Process2Done = self.parent.b_Process2Done
        self.PCA_done = self.parent.PCA_done
        self.old_Gval = self.parent.old_Gval
        self.old_Tval = self.parent.old_Tval

        # IF we have nothing to display, no model loaded: just a default background with axis
        if not self.InputModelLoaded:
            glClearColor(self.bg_color, self.bg_color, self.bg_color, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()  # identity matrix, resets the matrix back to its default state

            # field of view (angle), ratio, near plane, far plane: all values must be > 0
            gluPerspective(60, self.aspect, 0.01, 10000)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslate(self.Tx, self.Ty, -self.Tz)

            glRotated(self.xRot / 16, 1.0, 0.0, 0.0)
            glRotated(self.yRot / 16, 0.0, 1.0, 0.0)
            glRotated(self.zRot / 16, 0.0, 0.0, 1.0)

            self.qglColor(Qt.red)
            self.renderText(10, 20, "X")
            self.qglColor(Qt.green)
            self.renderText(10, 40, "Y")
            self.qglColor(Qt.blue)
            self.renderText(10, 60, "Z")

            glLineWidth(2.0)  # Width of the lines
            # To start creating lines (you also have glBegin(GL_TRIANGLES), glBegin(GL_POLYGONES), etc....
            # depending on what you want to draw)
            glBegin(GL_LINES)
            # X axis (red)
            glColor3ub(255, 0, 0)
            glVertex3d(0, 0, 0)  # The first glVertex3d is the starting point and the second the end point
            glVertex3d(1, 0, 0)
            # Y axis (green)
            glColor3ub(0, 255, 0)
            glVertex3d(0, 0, 0)
            glVertex3d(0, 1, 0)
            # Z axis (blue)
            glColor3ub(0, 0, 255)
            glVertex3d(0, 0, 0)
            glVertex3d(0, 0, 1)
            glEnd()  # Stop
            glLineWidth(1.0)  # Change back the width to default if you want to draw something else after normally

        else:
            PCA_done = self.parent.PCA_done
            if PCA_done == False:
                # display input 3D model
                if self.InputModelLoaded == True and self.InputTextureLoaded == True:
                    self.updated.emit(1)
                    glClearColor(self.bg_color, self.bg_color, self.bg_color, 1.0)
                    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                    glMatrixMode(GL_PROJECTION)
                    glLoadIdentity()  # identity matrix, resets the matrix back to its default state
                    # field of view (angle), ratio, near plane, far plane, all values must be > 0
                    gluPerspective(60, self.aspect, 0.01, 10000)
                    glMatrixMode(GL_MODELVIEW)
                    glLoadIdentity()
                    glTranslate(self.Tx, self.Ty, -self.Tz)
                    glRotated(self.xRot / 16, 1.0, 0.0, 0.0)
                    glRotated(self.yRot / 16, 0.0, 1.0, 0.0)
                    glRotated(self.zRot / 16, 0.0, 0.0, 1.0)
                    # Move 3D object to center
                    glPushMatrix()  # Save any translate/scale/rotate operations that you previously used
                    # In InputModel.vertices you have the coordinates of the vertices (X,Y,Z)
                    InputModel_Xs = [row[0] for row in self.InputModel.vertices]  # Here you will extract X
                    InputModel_Ys = [row[1] for row in self.InputModel.vertices]  # Here you will extract Y
                    InputModel_Zs = [row[2] for row in self.InputModel.vertices]  # Here you will extract Z
                    # A 3D object can have coordinates not always centered on 0
                    # So we are calculating u0,v0,w0 (center of mass/gravity of the 3D model)
                    # To be able to move it after to the center of the scene
                    u0 = (min(InputModel_Xs) + max(InputModel_Xs)) / 2
                    v0 = (min(InputModel_Ys) + max(InputModel_Ys)) / 2
                    w0 = (min(InputModel_Zs) + max(InputModel_Zs)) / 2
                    # Here we are calculating the best zoom factor by default (to see the 3D model entirely)
                    d1 = max(InputModel_Xs) - min(InputModel_Xs)
                    d2 = max(InputModel_Ys) - min(InputModel_Ys)
                    d3 = max(InputModel_Zs) - min(InputModel_Zs)
                    Q = 0.5 / ((d1 + d2 + d3) / 3)
                    glScale(Q, Q, Q)
                    glTranslate(-u0, -v0, -w0)  # Move the 3D object to the center of the scene
                    # Display 3D Model via a CallList (GOOD, extremely fast!)
                    # If the list is not created, we will do it
                    if self.InputModelLoaded == True and self.InputTextureLoaded == True and self.InputListCreated == False:
                        # pdb.set_trace()
                        ## This is how to set up a display list, whose invocation by glCallList
                        self.glinputModel = glGenLists(1)  # Allocate one list into memory
                        glNewList(self.glinputModel, GL_COMPILE)  # Begin building the passed in list
                        self.addTexture(self.InputTexturePath)  # Call function to add texture
                        self.addModel(self.InputModel)  # Call function to add 3D model
                        glEndList()  # Stop list creation
                        self.InputListCreated = True
                        self.c_mode = self.r_mode
                        glCallList(self.glinputModel)  # Call the list (display the model)
                    # If the list is already created, no need to process again and loose time, just display it
                    elif self.InputModelLoaded == True and self.InputTextureLoaded == True and self.InputListCreated == True:
                        # however, if we are changing the mode (Faces/Points), we need to recreate again
                        if self.Updated == True:
                            # Here we have to create the list again because it's not exactly the same list
                            # if we want to show just the points or the full model
                            self.glinputModel = glGenLists(1)
                            glNewList(self.glinputModel, GL_COMPILE)
                            self.addTexture(self.InputTexturePath)
                            self.addModel(self.InputModel)
                            glEndList()
                            self.c_mode = self.r_mode
                            glCallList(self.glinputModel)
                            self.Updated = False
                            self.parent.Updated = False
                        else:
                            glCallList(self.glinputModel)
                    glPopMatrix()  # Will reload the old model view matrix
                else:
                    print(0)

            # if the PCA is done, we will display the new model here
            else:
                glClearColor(self.bg_color, self.bg_color, self.bg_color, 1.0)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()  # identity matrix, resets the matrix back to its default state
                gluPerspective(60, self.aspect, 0.01, 10000)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                glTranslate(self.Tx, self.Ty, -self.Tz)
                glRotated(self.xRot / 16, 1.0, 0.0, 0.0)
                glRotated(self.yRot / 16, 0.0, 1.0, 0.0)
                glRotated(self.zRot / 16, 0.0, 0.0, 1.0)
                # Move 3D object to center
                glPushMatrix()  # Save any translate/scale/rotate operations that you previously used
                # In InputModel.vertices you have the coordinates of the vertices (X,Y,Z), here you will extract X
                InputModel_Xs = [row[0] for row in self.InputModel.vertices]
                InputModel_Ys = [row[1] for row in self.InputModel.vertices]  # Here you will extract Y
                InputModel_Zs = [row[2] for row in self.InputModel.vertices]  # Here you will extract Z
                u0 = (min(InputModel_Xs) + max(InputModel_Xs)) / 2
                v0 = (min(InputModel_Ys) + max(InputModel_Ys)) / 2
                w0 = (min(InputModel_Zs) + max(InputModel_Zs)) / 2
                # Here we are calculating the best zoom factor by default (to see the 3D model entirely)
                d1 = max(InputModel_Xs) - min(InputModel_Xs)
                d2 = max(InputModel_Ys) - min(InputModel_Ys)
                d3 = max(InputModel_Zs) - min(InputModel_Zs)
                Q = 0.5 / ((d1 + d2 + d3) / 3)
                glScale(Q, Q, Q)
                glTranslate(-u0, -v0, -w0)  # Move the 3D object to the center of the scene
                self.setXRotation(self.LeftXRot)
                self.setYRotation(self.LeftYRot)
                self.updated.emit(1)
                if self.TargetListCreated == False:
                    # pdb.set_trace()
                    ##This is how to set up a display list, whose invocation by glCallList
                    self.targetModel = glGenLists(1)
                    glNewList(self.targetModel, GL_COMPILE)
                    self.applyTarTexture(self.parent.TarTexture)
                    self.addModel(self.InputModel)
                    glEndList()
                    self.TargetListCreated = True
                    self.c_mode = self.r_mode
                    glCallList(self.targetModel)
                elif self.TargetListCreated == True:
                    if self.c_mode == self.r_mode and self.old_Gval == self.Gval and self.old_Tval == self.Tval:
                        glCallList(self.targetModel)
                    else:
                        self.targetModel = glGenLists(1)
                        glNewList(self.targetModel, GL_COMPILE)
                        self.applyTarTexture(self.parent.TarTexture)
                        self.addModel(self.InputModel)
                        glEndList()
                        self.c_mode = self.r_mode
                        glCallList(self.targetModel)
                self.old_Gval = self.Gval
                self.old_Tval = self.Tval
                glPopMatrix()

    def addModel(self, InputModel):
        if self.r_mode == "Faces":
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_DEPTH_TEST)  # to show all faces
            # glEnable(GL_CULL_FACE) # To hide non visible faces
            glBindTexture(GL_TEXTURE_2D, self.tex)
            glBegin(GL_TRIANGLES)
            for i in InputModel.faces:
                F = i[0]
                for j in F:
                    glColor3ub(255, 255, 255)
                    glTexCoord2f(InputModel.texcoords[j-1][0], InputModel.texcoords[j-1][1])
                    glNormal3d(InputModel.normals[j-1][0], InputModel.normals[j-1][1], InputModel.normals[j-1][2])
                    glVertex3d(InputModel.vertices[j-1][0], InputModel.vertices[j-1][1], InputModel.vertices[j-1][2])
            glEnd()
            glDisable(GL_TEXTURE_2D)
        elif self.r_mode == "Points":
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.tex)
            glBegin(GL_POINTS)
            for i in range(len(InputModel.vertices)):
                glColor3ub(255, 255, 255)
                glTexCoord2f(InputModel.texcoords[i][0], InputModel.texcoords[i][1])
                glNormal3d(InputModel.normals[i][0], InputModel.normals[i][1], InputModel.normals[i][2])
                glVertex3d(int(InputModel.vertices[i][0]), int(InputModel.vertices[i][1]), int(InputModel.vertices[i][2]))
            glEnd()
            glDisable(GL_TEXTURE_2D)

    def addTexture(self, TexturePath):
        img = QImage(TexturePath)
        img = QGLWidget.convertToGLFormat(img)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width(), img.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, img.bits().asstring(img.byteCount()))

    def applyTarTexture(self, TarTexture):
        img = QImage("TarTexture.png")
        img = QGLWidget.convertToGLFormat(img)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width(), img.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, img.bits().asstring(img.byteCount()))

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def wheelEvent(self, event):
        numDegrees = event.angleDelta() / 8
        orientation = numDegrees.y()
        if orientation > 0:
            self.Tz -= 0.1  # zoom out
        else:
            self.Tz += 0.1  # zoom in
        self.updateGL()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        if event.buttons() & Qt.LeftButton:  # holding left button of mouse and moving will rotate the object
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
            self.LeftXRot = self.xRot + 8 * dy
            self.LeftYRot = self.yRot + 8 * dx
        elif event.buttons() & Qt.RightButton:  # holding right button of mouse and moving will translate the object
            self.Tx += dx / 100
            self.Ty -= dy / 100
            self.updateGL()
        elif event.buttons() & Qt.MidButton:  # holding middle button of mouse and moving will reset zoom/translations
            self.Tx = Ty = 0
            self.Tz = 1
            self.setXRotation(0)
            self.setYRotation(90)
            self.updateGL()

        self.lastPos = event.pos()

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 50:
            return

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        self.aspect = float(width) / float(height)
        gluPerspective(60.0, self.aspect, 0.01, 10000)
        glMatrixMode(GL_MODELVIEW)

    def setClearColor(self, c):
        gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
