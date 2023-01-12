from ui_Project import *
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.setupUI() 
    ui.show() 

    sys.exit(app.exec_())
