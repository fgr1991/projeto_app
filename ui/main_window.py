from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):

    def __init__(self, controller):
        super().__init__()

        # 🔹 guarda o controller
        self.controller = controller

        self.setWindowTitle("Aplicativo ML - Investment System")
        self.showMaximized()

        self.setup_ui()
        self.connect_signals()

    # ==========================================================
    # UI
    # ==========================================================

    def setup_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==============================
        # Barra superior
        # ==============================

        top_bar = QWidget()
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(5, 5, 5, 5)
        top_bar_layout.setSpacing(10)

        self.btn_file = QPushButton("File")
        self.btn_database = QPushButton("Database")
        self.btn_ml = QPushButton("Machine Learning")
        self.btn_viz = QPushButton("Data Visualization")

        for button in [
            self.btn_file,
            self.btn_database,
            self.btn_ml,
            self.btn_viz,
        ]:
            button.setFixedHeight(30)
            button.setMinimumWidth(120)
            top_bar_layout.addWidget(button)

        top_bar_layout.addStretch()
        top_bar.setLayout(top_bar_layout)

        # ==============================
        # Área de conteúdo
        # ==============================

        self.content_area = QWidget()

        main_layout.addWidget(top_bar)
        main_layout.addWidget(self.content_area)

        central_widget.setLayout(main_layout)

    # ==========================================================
    # Conexões
    # ==========================================================

    def connect_signals(self):
        self.btn_database.clicked.connect(self.on_database_clicked)
        self.btn_ml.clicked.connect(self.on_ml_clicked)
        self.btn_viz.clicked.connect(self.on_viz_clicked)

    # ==========================================================
    # Eventos
    # ==========================================================

    def on_database_clicked(self):
        self.controller.handle_database_action()

    def on_ml_clicked(self):
        self.controller.handle_ml_action()

    def on_viz_clicked(self):
        self.controller.handle_visualization_action()
