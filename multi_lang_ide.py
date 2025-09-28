from PyQt5.QtWidgets import *
from PyQt5.QtCore import *				# Used for building the QT text editor itself
from PyQt5.QtPrintSupport import *

import os								# Allows working with file paths and extensions
import shlex
import shutil							# Locates system exe such as compilers
import subprocess
import sys								# Accesses current python interpreter path

import platform							# For testing what platform (ie windows, mac, linux)

class MainWindow(QMainWindow):
    def __init__(self):
        # Parent constructor which initializes QMainWindow
        super(MainWindow, self).__init__()

        # Sets window size (x, y, width, height), temporarily smaller
        self.setGeometry(100, 100, 800, 600)

        # Sets vertical layout for GUI, makes the text editor center/ top-to-bottom
        layout = QVBoxLayout()
        
        # Building editor object using QPlainTextEdit()
        self.editor = QPlainTextEdit()
        
        # self.path holds the path of the currently open file.
        # If none, there is currently no file open or it is a new file.
        self.path = None
        
        # Then adds the new editor to the layout as a widget
        layout.addWidget(self.editor)

        # Container widget that holds everything
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
        #           calls the menuBar object and adds to menu "File"
        file_menu = self.menuBar().addMenu("File")
        
        # Adding options within File dropdown w/ file opening being most important for an IDE
        # Sets var to be QAction which is any user click, key shortcut, etc. "Open file" is the text displayed.
        open_file_action = QAction("Open file", self)

        # Sends status to bottom status bar
        open_file_action.setStatusTip("Open file")

        # adding action to the open file -- uses function from below 
        #open_file_action.triggered.connect(self.file_open)

        # This adds to the file dropdown menu 
        file_menu.addAction(open_file_action)

        # This adds the Open file option to the toolbar.
        file_toolbar.addAction(open_file_action)
        
#-----------------------Editing features needed for a good text editor, copy and paste, undo, etc-----------------------
        # Edit menu same as above
        edit_menu = self.menuBar().addMenu("Edit")
        edit_toolbar = QToolBar("Edit")

        # Adding edit tools to the main window
        self.addToolBar(edit_toolbar)

        # Actions for toolbar when user clicks these
        undo_action = QAction("Undo", self)             # Undo
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(self.editor.undo)

        # This will add the undo to toolbar created above
        edit_toolbar.addAction(undo_action)
        edit_menu.addAction(undo_action)

        # Redo button - same as above
        redo_action = QAction("Redo", self)
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.editor.redo)
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        # Cut for cut and paste, no toolbar for this
        cut_action = QAction("Cut", self)
        cut_action.setStatusTip("Cut selected text")
        cut_action.triggered.connect(self.editor.cut)
        
        # Adding only to the drop down menu
        edit_menu.addAction(cut_action)

        # Copy same as cut
        copy_action = QAction("Copy", self)
        copy_action.setStatusTip("Copy selected text")
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)

        # Paste will be on toolbar for easy pasting 
        paste_action = QAction("Paste", self)
        paste_action.setStatusTip("Paste from clipboard")           #Refine this, better font and design
        paste_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        # Nice little select all text for edit menu. No toolbar as it's only used for certain cases
        select_action = QAction("Select all", self)
        select_action.setStatusTip("Select all text")
        select_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_action)
        
#----------------------------------------Build Menu such as Compiler and other Dev tools--------------------------------        
        build_menu = self.menuBar().addMenu("Build")
        build_toolbar = QToolBar("Build")
        
        # This is what actually displays everything. Without this, no display on toolbar
        self.addToolBar(build_toolbar)
        
        # Set up for adding compiler to toolbar 
        compile_action = QAction("Compile", self)       
        compile_action.setStatusTip("Compile your program without running it")
        build_toolbar.addAction(compile_action)
        build_menu.addAction(compile_action)
        
        compile_run_action = QAction("Compile and Run", self)
        compile_run_action.setStatusTip("Compile and Run your Program")
        build_toolbar.addAction(compile_run_action)
        build_menu.addAction(compile_run_action)
        
#---------------------------------------Search menu for find & replace and other utils---------------------------------------------        
        search_menu = self.menuBar().addMenu("Search")
        search_toolbar = QToolBar("Search")
        self.addToolBar(search_toolbar)

#----------------------------------------Print Menu for the option printing---------------------------------------------        
        print_menu = self.menuBar().addMenu("Print")
        
        
  
  
#-------------------------------------------------Settings Menu-----------------------------------------------------------        
        settings_menu = self.menuBar().addMenu("Settings")



#--------------------------Untitled space TBD for linking to GitHub and other Version Control methods---------------------
        
        
        
        
#----------------------------------End of Menu options and Tool bar------------------------------------------------------
#---------------------------Below are functions and general QT setup for building the look------------------------------------------------------        
        # Displaying messages to status bar. This is the welcome message until replaced .
        self.status.showMessage("~~~~~~~~~~~~~~Welcome to The MultiLang IDE --- Share with Friends and Code Away!~~~~~~~~~~~~~~")
        #setStatusTip()
        
        # Redundant show window call 
        self.show()

        # Override Key Press event for allowing button presses such as ESC to exit
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.confirmExit()

    def confirmExit(self):
        # Creating a Yes/No message box for the user to confirm their exit. 
        reply = QMessageBox.question(self, "Exit", "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No)
                                     
        # If yes, quit application
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()
    
    
    def compileSetup(self, file):
    # Function from stack to understand the compiler call to other languages @AKX & @mousetail.
    # Modified by me to fit my uses
    
	# Splits filename into two parts focusing on ext. 1 grabs 2nd part of split (.ext) and lowercases it as it should be
        ext = os.path.splitext(file)[1].lower()
        if ext == ".py":
           return [(sys.executable, file)]		# Built in py command to execute .py files using built in interpreter
		# If its a CPP extension: 
        elif ext in (".c", ".cpp", ".h"):
			 # Tries to find the gcc compiler path
           gcc_path = shutil.which("gcc")
             # If it can't find it, raises an error
           if not gcc_path:
            raise EnvironmentError("GCC compiler not found")

        # Changes file name to proper executable based on Operating System. Tests and holds in variable below
        # On Windows, use '.exe'; on Linux/macOS, use '_out' suffix
           exe_file = (
               f"{os.path.splitext(file)[0]}.exe"		# Decide the name of the compiled executable based on the operating system
               if platform.system() == "Windows"		# Platform.system tests for OS name. Can also do architecture
               else f"{os.path.splitext(file)[0]}_out"
           )
           
        # Return two commands:
        # 1. The command to compile the source file
        # 2. The command to run the compiled executable
           return [
            (gcc_path, "-std=c11", file, "-o", exe_file),		# Then calls exe_file var from above holding which type
            (exe_file,),										# Variable changes based on the OS type
        ]
        # Tells if unsupported file type
        else: 
            raise ValueError(f"Unsupported file type: {ext}")

# Standard PyQT setup 
app = QApplication(sys.argv)    # Creates application object
window = MainWindow()           # Incorporates our custom window class from above as main window
app.exec_()                     # Event loop, keeps app running until exit



# GitHub Desktop didn't upload my clone I worked on incorporating saves and opening files. Will merge them when I access my other system. 

# TODO test compiler and see if it works before trying to add languages. Also better design.
# Bundle all compilers with the install of this so user can download and go without having to manually do it.
