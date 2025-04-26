from PyQt6.QtWidgets import QMainWindow
from src.gui.buttons import ButtonsUI  

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Manager")
        self.setGeometry(100, 100, 1000, 700)
        
        self.buttons_ui = ButtonsUI() 
        self.setCentralWidget(self.buttons_ui)