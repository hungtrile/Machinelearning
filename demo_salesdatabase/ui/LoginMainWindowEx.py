from PyQt6.QtWidgets import QMessageBox

from demo_salesdatabase.ui.LoginMainWindow import Ui_MainWindow


class LoginMainWindowEx(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow=MainWindow
        self.setupSignalAndSlot()
    def showWindow(self):
        self.MainWindow.show()

    def setupSignalAndSlot(self):
        self.pushButtonLogin.clicked.connect(self.process_login)
    def process_login(self):
        from demo_salesdatabase.dal.userDAO import userDAO

        uid = self.lineEditUserName.text()
        pwd = self.lineEditPassword.text()
        us = userDAO.login(uid, pwd)
        self.msgBox=QMessageBox()
        if us is None:
            self.msgBox.setText("Login Failed")
        else:
            self.msgBox.setText("Welcome:"+ us.username)
        self.msgBox.exec()