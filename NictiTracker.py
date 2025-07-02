from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
import sys

def use_dynamo_safely():
    try:
        import torch._dynamo
        torch._dynamo.config.suppress_errors = True
    except TypeError as e:
        print("Torch Dynamo failed to import, continuing anyway:", e)

def main():
    use_dynamo_safely()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
