from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
import sys
import os 
class MainWindow(QMainWindow):
    def __init__(self):
		# Parent constructor which initializes QMainWindow
        super(MainWindow, self).__init__()

		# Sets window size (x, y, width, height), temporarily smaller
        self.setGeometry(100, 100, 600, 600)

        # Sets vertical layout for GUI, makes the text editor center/ top-to-bottom
        layout = QVBoxLayout()
        
        # Building editor object using QPlainTextEdit()
        self.editor = QPlainTextEdit()
        
		# self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None
        
        # Then adds the new editor to the layout as a widget
        layout.addWidget(self.editor)

		# Container widget to hold the layout
        container = QWidget()
        
        # Sets layout of container as our previous layout including widgets
        container.setLayout(layout)
        
        # Sets container as Central Widget on screen, main focus
        self.setCentralWidget(container)

        # Status bar for bottom of window, this allows for info to user ('File Saved', etc)
        self.status = QStatusBar()

        # Sets status bar to window 
        self.setStatusBar(self.status)

        # Creates horizontal bar on top to hold clickable items. Not displayed until below
        file_toolbar = QToolBar("File")

        # Adds this toolbar to the main window making it show visually
        self.addToolBar(file_toolbar)

        # Creates 'File' menu, this is where each drop down comes from 
        # 			calls the menuBar object and adds to menu "File"
        file_menu = self.menuBar().addMenu("File")
        
        build_menu = self.menuBar().addMenu("Build")
        
        print_menu = self.menuBar().addMenu("Print")
        
        
        # Displaying messages to status bar. This is the welcome message until replaced .
        self.status.showMessage("~~~~~~~~~~~~~~Welcome to The MultiLang IDE --- Share with Friends and Code Away!~~~~~~~~~~~~~~")
        #setStatusTip()
        
		# Redundant show window call 
        self.show()

		# Override Key Press event for allowing button presses such as ESC to exit
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.confirm_exit()

    def confirm_exit(self):
		# Creating a Yes/No message box for the user to confirm their exit. 
        reply = QMessageBox.question(self, "Exit", "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No)
                                     
        # If yes, quit application
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()

# Standard PyQT setup 
app = QApplication(sys.argv)	# Creates application object
window = MainWindow()			# Incorporates our custom window class from above as main window
app.exec_()						# Event loop, keeps app running until exit
