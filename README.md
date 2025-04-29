# 3D-PCA-Face-Morphing
A PyQt5 and OpenGL application to apply PCA to 3D face geometry and texture for morphing and transformation visualization.
# 3D-PCA-Face-Morphing

An application for applying Principal Component Analysis (PCA) on 3D face geometry and texture using PyQt5, OpenGL, and NumPy.

## 🧠 Project Summary

This tool loads two 3D face models and their corresponding textures, applies PCA separately to geometry (vertices) and texture, and enables dynamic transformation via GUI sliders.

It allows interactive control over geometry and texture modes and exports the resulting transformed model.

## ✨ Features

- PCA-based manipulation of 3D face shape and texture
- Load `.obj` and `.png` files with same filename
- Real-time texture and geometry morphing using sliders
- 3D OpenGL rendering with rotation, zoom, and pan
- Save transformed models as `.obj`
- Face render modes: Points, Wireframe, Solid
- PyQt5 GUI with OpenGL widget integration

## 🧰 Requirements

Install required packages using pip:

```bash
pip install PyQt5 opencv-python imageio numpy PyOpenGL


.
├── M1_Elham Nasrollahzadeh Soufiani- PCA.py  # Main script (PyQt5 GUI + logic)
├── OBJ.py                                    # OBJ file loader (vertices, faces, textures)
├── model1.obj
├── model2.obj
├── model1.png
├── model2.png
├── TarTexture.png                            # Generated output texture
├── ModifiedModel.obj                         # Generated 3D model after PCA


python "M1_Elham Nasrollahzadeh Soufiani- PCA.py"
