import os
import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from controllers.tree_controller import TreeController
from PySide6 import __file__ as pyside6_file

pyside6_dir = os.path.dirname(pyside6_file)
plugin_path = os.path.join(pyside6_dir, 'plugins')
os.environ['QT_PLUGIN_PATH'] = plugin_path

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for nuitka """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():

    print("Python version:", sys.version)
    print("Current working directory:", os.getcwd())
    print("sys.executable:", sys.executable)
    print("sys.prefix:", sys.prefix)
    print("sys._MEIPASS:", getattr(sys, '_MEIPASS', 'Not frozen'))
    print("QT_QPA_PLATFORM_PLUGIN_PATH:", os.environ.get('QT_QPA_PLATFORM_PLUGIN_PATH', 'Not set'))
    

    
    try:
        app = QApplication(sys.argv)
        
        # Set font file path
        font_path = os.path.join('utils', 'SourceHanSansHWSC-Regular.otf')
        
        controller = TreeController()
        main_window = MainWindow(font_path)
        main_window.set_controller(controller)
        
        main_window.show()
        
        exit_code = app.exec()
        controller.close()
        return exit_code
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())