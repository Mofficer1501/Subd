class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.menu_bar = self.menuBar()
        self.db_menu = self.menu_bar.addMenu("БД")

        self.db_action = QAction("Подключить БД", self)
        self.db_action.triggered.connect(self.show_db_tables)

        self.other_action_1 = QAction("f_zb.csv", self)
        self.other_action_1.triggered.connect(lambda: self.load_table("f_zb.csv"))

        self.other_action_2 = QAction("Zb.csv", self)
        self.other_action_2.triggered.connect(lambda: self.load_table("Zb.csv"))

        self.db_menu.addAction(self.db_action)
        self.db_menu.addAction(self.other_action_1)
        self.db_menu.addAction(self.other_action_2)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)

        self.button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Редактировать")
        self.add_button = QPushButton("Добавить")
        self.delete_button = QPushButton("Удалить")
        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.button_layout)

    def show_db_tables(self):
        # Здесь можно добавить код для выбора таблиц

    def load_table(self, file_name):
        # Загружаем данные из CSV-файла

    def show_table(self, table_name):

        # Получение названий столбцов из БД

        # Установка заголовков столбцов модели

        # Устанавливаем свойство horizontalHeader для отображения заголовков