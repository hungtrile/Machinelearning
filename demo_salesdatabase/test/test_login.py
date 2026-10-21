
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

from demo_salesdatabase.ui.LoginMainWindowEx import LoginMainWindowEx

app = QApplication(sys.argv)

window = QMainWindow()
ui = LoginMainWindowEx()
ui.setupUi(window)

window.setWindowTitle("Login System")
window.show()

sys.exit(app.exec())
