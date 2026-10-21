import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from demo_salesdatabase.ui.CustomerMainWindowEx import CustomerMainWindowEx

app=QApplication(sys.argv)
myui=CustomerMainWindowEx()
myui.setupUi(QMainWindow())
myui.showWindow()
app.exec()