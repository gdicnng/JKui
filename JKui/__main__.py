import os
import locale

import qtpy
#from qtpy.QtWidgets import *
#from qtpy.QtGui import *
#from qtpy.QtCore import *

print(locale.setlocale(locale.LC_ALL, ))
locale.setlocale(locale.LC_ALL, '')
print()
print(locale.setlocale(locale.LC_ALL, ))

print("current directory:",os.getcwd())

print( "the qt binding version" )
if qtpy.PYSIDE_VERSION:
    print( "pyside",qtpy.PYSIDE_VERSION)
if qtpy.PYQT_VERSION:
    print( "pyqt",qtpy.PYQT_VERSION )



import ui_mainwindow
ui_mainwindow.main()

