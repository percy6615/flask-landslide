from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog

from ui import ui
import sys


class MainWindow(QtWidgets.QDialog):
     def __init__(self):
         super(QDialog, self).__init__()
         self.ui = ui.Ui_Dialog()
         self.ui.setupUi(self)
         # self.ui.label.setText('Hello World!')


if __name__ == '__main__':
     app = QtWidgets.QApplication([])
     window = MainWindow()
     window.show()
     sys.exit(app.exec_())