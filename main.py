import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from controllers.app_controller import AppController


def main():
    app = QApplication(sys.argv)

    # Cria o controller
    controller = AppController()

    # Cria a janela principal passando o controller
    window = MainWindow(controller)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
