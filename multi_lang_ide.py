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
        self.setGeometry(100, 100, 1800, 1000)
        
        self.setWindowTitle("CodeIDE")

        # Sets tab layout for GUI, allows for multiple documents to be open at once
        
        self.tabs = QTabWidget()

        # self.path holds the path of the currently open file.
        # If none, there is currently no file open or it is a new file.
        self.path = None
        
        # Adds these after to fit the layout: file label, text editor, console
        #layout.addWidget(self.editor)
        #layout.addWidget(self.output_console)

        
        # Sets tabs as Central Widget on screen, main focus
        self.setCentralWidget(self.tabs)

		# Calls our function below which creates IDE
        self.addNewTab()


        # Status bar for bottom of window, this allows for info to user ('File Saved', etc)
        self.status = QStatusBar()

        # Sets status bar to window 
        self.setStatusBar(self.status)
		
		# Setting bigger and smaller font
        largefont = self.status.font()
        smallfont = self.menuBar().font()
        largefont.setPointSize(14)
        smallfont.setPointSize(12)
        
        # Applying to elements
        self.status.setFont(largefont)
        self.menuBar().setFont(smallfont)

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
        open_file_action.triggered.connect(self.openFile)

        # This adds to the file dropdown menu 
        file_menu.addAction(open_file_action)

        # This adds the Open file option to the toolbar.
        file_toolbar.addAction(open_file_action)
        
        # Repeat above for each element. Only Specific elements will be on toolbar
        save_file_action = QAction ("Save File", self)
        save_file_action.setStatusTip("Save your hard work so you don't lose it")
        save_file_action.triggered.connect(self.saveFile)
        file_menu.addAction(save_file_action)
        file_toolbar.addAction(save_file_action)
        
        new_action = QAction ("New Document", self)
        new_action.setStatusTip("Start fresh or add on with a new file!")
        #new_action.triggered.connect(self.saveFileAs)
        file_menu.addAction(new_action)
        file_toolbar.addAction(new_action)
        
#-----------------------Editing features needed for a good text editor, copy and paste, undo, etc-----------------------
        # Edit menu same as above
        edit_menu = self.menuBar().addMenu("Edit")
        edit_toolbar = QToolBar("Edit")

        # Adding edit tools to the main window
        self.addToolBar(edit_toolbar)

        # Actions for toolbar when user clicks these
        undo_action = QAction("Undo", self)             # Undo
        undo_action.setStatusTip("Undo last change")
        
       # Lambda! Lambda is a temporary unnamed function that runs at time of creating. ------->     This is because by calling this without lambda, it will run on					
        undo_action.triggered.connect(lambda: self.getCurrentEditor().undo())				#    opening of the program. A Lambda function will only run when triggered
																							# We create a lambda and initialize it to the function below which grabs the 
																							# editor object for the active tab.				
        # This will add the undo to toolbar created above
        edit_toolbar.addAction(undo_action)
        edit_menu.addAction(undo_action)					
								
										
       # The lambda defers execution until the user clicks the Undo action.
										

        # Redo button - same as above
        redo_action = QAction("Redo", self)
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(lambda: self.getCurrentEditor().redo())
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        # Cut for cut and paste, no toolbar for this
        cut_action = QAction("Cut", self)
        cut_action.setStatusTip("Cut selected text")
        cut_action.triggered.connect(lambda: self.getCurrentEditor().cut())
        # Adding only to the drop down menu
        edit_menu.addAction(cut_action)

        # lambda use here allows for very modular function
        copy_action = QAction("Copy", self)
        copy_action.setStatusTip("Copy selected text")
        copy_action.triggered.connect(lambda: self.getCurrentEditor().copy())
        edit_menu.addAction(copy_action)

        # Paste will be on toolbar for easy pasting 
        paste_action = QAction("Paste", self)
        paste_action.setStatusTip("Paste from clipboard")           #Refine this, better font and design
        paste_action.triggered.connect(lambda: self.getCurrentEditor().paste())
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        # Nice little select all text for edit menu. No toolbar as it's only used for certain cases
        select_action = QAction("Select all", self)
        select_action.setStatusTip("Select all text")
        select_action.triggered.connect(lambda: self.getCurrentEditor().selectAll())
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
        compile_run_action.triggered.connect(self.compileSetup)
        build_toolbar.addAction(compile_run_action)
        build_menu.addAction(compile_run_action)
        
#---------------------------------------Search menu for find & replace and other utils---------------------------------------------        
        search_menu = self.menuBar().addMenu("Search")
        search_toolbar = QToolBar("Search")
        self.addToolBar(search_toolbar)

#----------------------------------------Print Menu for the option printing---------------------------------------------        
        print_menu = self.menuBar().addMenu("Print")
        
        print_action = QAction("Print Document", self)
        print_action.setStatusTip("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Don't forget to frame it!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print_action.triggered.connect(self.filePrint)
        print_menu.addAction(print_action)
  
#-------------------------------------------------Settings Menu-----------------------------------------------------------        
        settings_menu = self.menuBar().addMenu("Settings")



#--------------------------Untitled space TBD for linking to GitHub and other Version Control methods---------------------
        
        
        
    
#------------------------------------------End of Menu/Toolbar --------------------------------------------------------------------------------------    
        # Displaying messages to status bar. This is the welcome message until replaced .
        self.status.showMessage("~~~~~~~~~~~~~~Welcome to The MultiLang IDE --- Share with Friends and Code Away!~~~~~~~~~~~~~~")
        #setStatusTip()
        
        # Redundant show window call 
        self.show()    
    
        
        
        # setStyleSheet() method included with PyQT. Using my experience with CSS it actually was really simple to write. This is just starting code.
        # https://doc.qt.io/archives/qt-5.15/stylesheet-reference.html
        self.setStyleSheet("""
        /* Whole page*/
    QMainWindow {
        background-color: #2e2e2e;
    }

	/* Main text editor */
    QPlainTextEdit {
        background-color: #2b3e50;
        color: #e0e0e0;								/* This is the color of the text in the editor */	
        font-family: Consolas, monospace;
        font-size: 14px;							/* Font size and font type*/
        border: 1px solid #333;						/* Border size and type. Can be dotted, dashed, etc */
        padding: 6px;								/* Inner spacing */
    }

	/* File path label*/
    QLabel {
        color: #cccccc;
        font-size: 13px;
    }

	/* Tab container */
    QTabWidget::pane {
        border: 1px solid #444;
    }

	/* Individual tab styles */
    QTabBar::tab {
        background: #2a2a2a;
        color: #aaa;
        padding: 6px;
        border: 1px solid #444;
        border-bottom: none;
    }
	/* Selecting a specific tab */
    QTabBar::tab:selected {
        background: #3a3a3a;
        color: #fff;
    }

    QStatusBar {
        background-color: #111;
        border-top: 1px solid #444;
    }

    QMenuBar {
        background-color: #2b2b2b;				/* Dark gray menu bar*/
        color: #ddd;							/* White text for menu items*/
    }

    QMenuBar::item:selected {
        background-color: #444;					/* When an item is hovered background changes */
    }

    QToolBar {
        background-color: #2b2b2b;				
        border-bottom: 1px solid #444;
    }

    QToolButton {
        color: #ddd;
        background-color: #2b2b2b;
        border: none;
        padding: 4px 8px;
    }

    QToolButton:hover {						/* Same hover change for the toolbar */
        background-color: #444;
    }
""")
        
        
        
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------Below are functions and general QT setup for building the look-------------------------------------------------------------    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------

###

    def addNewTab(self, file_path=None):
		
		# Building editor object using QPlainTextEdit(). Adding line wrapping 
        editor = QPlainTextEdit()
        editor.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        # Label to show selected file path
        label = QLabel(file_path if file_path else "No file selected")
        #label.setFont(QFont("Arial", 12))

        # Console below main editor to capture/display output 
        # Creates a new text editor same as above but..
        output_console = QPlainTextEdit()
        
        # Read only overrides the text edit so it only displays added text
        output_console.setReadOnly(True)
        output_console.setStyleSheet("background-color: #111; color: #0f0; font-family: monospace;")

		# Vertical layout to stack label, editor, and console 
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(editor)
        layout.addWidget(output_console)
        
        # Container widget that holds everything
        container = QWidget()
        container.setLayout(layout)

		# Setting tab name based on file name or default
							# Basename extracts just the file name "/path/to/test.py" -> "test.py" which is what we want to display
        tab_name = os.path.basename(file_path) if file_path else "New File"
        
        # Adds this container as a new tab with this name 
        self.tabs.addTab(container, tab_name)

#-------------------------------------------------------------------------------------------------------------------------

       # Helper to get the current editor from the active tab
    def getCurrentEditor(self):
        current_widget = self.tabs.currentWidget()
        return current_widget.findChild(QPlainTextEdit)


###

        # Override Key Press event for allowing button presses such as ESC to exit
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.confirmExit()
        elif event.key() == Qt.Key_F5:
            self.compileSetup()
        elif event.key() == Qt.Key_F1:
            self.addNewTab()


###

    def confirmExit(self):
        # Creating a Yes/No message box for the user to confirm their exit. 
        reply = QMessageBox.question(self, "Exit", "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No)
                                                                          
        # If yes, quit application
        if reply == QMessageBox.Yes:
            QApplication.instance().quit()



###

    def openFile(self):
        options = QFileDialog.Options()
        
        # Opens dialog to select file, returns file path and file type.
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", 	# Show all possible file extensions to remind users they can run any language
                                                   "All Files (*);;Text Files (*.txt);;Python Files(*.py);;C++ Files(*.cpp, *.h);;JS Files (*.node)", 
                                                   options=options)			# This controls the dropdown in file manager itself
        if file_path:
            self.path = file_path
            
            with open(file_path, 'r') as f:
                self.editor.setPlainText(f.read())
            self.label.setText(f"Selected File: {file_path}")


###

    def saveFile(self):
        
        # If there is no save path set, ie haven't saved it yet
        if self.path is None:
                                # Calls the save as method from below and forces user to create save path
            return self.saveFileAs()
                                # Otherwise it saves to the path already set
        self.saveToPath()




        
    def saveFileAs(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", 			# Remove after txt to have default
                                                   "All Files (*);;Text Files (*.txt);;Python Files(*.py);;C++ Files(*.cpp, *.h);;JS Files (*.node)", 
                                                   options=options)
        if not self.path:
            return 

	

###
    
    def compileSetup(self):
    # Function from stack to understand the compiler call to other languages @AKX & @mousetail.
    # Modified by me to fit my uses
    
    # If file is not open produces error. This is filled in the openFile function
        if not self.path:
          QMessageBox.warning(self, "No File", "Please open a file first.")
          return
    
	# Splits current file path into two parts focusing on .ext. 1 grabs 2nd part of split (.ext) and lowercases it as it should be. 
        ext = os.path.splitext(self.path)[1].lower()
        if ext == ".py":							
           return [(sys.executable, self.path)]		# Built in py command to execute .py files using built in interpreter. Uses path var from above
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




###

    # For Print button if desired.
    def filePrint(self):

        # Creating a QPrintDialog
        export = QPrintDialog()

        # When you click Print executes 
        if export.exec_():

            # Print the text
            self.editor.print_(export.printer())

###


    

#--------------------------------------------------------------------------------------------------------------------
# Standard PyQT setup 
app = QApplication(sys.argv)    # Creates application object

window = MainWindow()           # Incorporates our custom window class from above as main window

app.exec_()                     # Event loop, keeps app running until exit

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~NOTES AND TODO~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TODO: test compiler and see if it works before trying to add languages - need to create a call to the compiler function. Also better design.
# 		Add multiple tabs so users can have multiple documents open at once. 
# Bundle all compilers with the install of this so user can download and go without having to manually do it.
