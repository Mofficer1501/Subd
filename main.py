import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QComboBox, QLabel, QTableView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import pandas as pd  # Библиотека для работы с таблицами (вы можете использовать PyQt5 для работы с таблицами)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Устанавливаем окно на весь экран
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        # Создаем строку меню
        self.menu_bar = self.menuBar()
        self.db_menu = self.menu_bar.addMenu("БД")

        # Создаем действия для меню
        self.db_action = QAction("База данных", self)
        self.db_action.triggered.connect(self.show_db_tables)

        self.other_action_1 = QAction("Таблица f_zb", self)
        self.other_action_1.triggered.connect(lambda: self.show_other_info(1))

        self.other_action_2 = QAction("Таблица Zb", self)
        self.other_action_2.triggered.connect(lambda: self.show_other_info(2))

        self.other_action_3 = QAction("Объединенная", self)
        self.other_action_3.triggered.connect(lambda: self.show_other_info(3))

        # Добавляем действия в меню
        self.db_menu.addAction(self.db_action)
        self.db_menu.addAction(self.other_action_1)
        self.db_menu.addAction(self.other_action_2)
        self.db_menu.addAction(self.other_action_3)

        # Создаем основной виджет и устанавливаем его в качестве центрального
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Устанавливаем верстку
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Создаем элементы для отображения
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

        # Создаем список с данными (для примера)
        self.tables_list = ["table1", "table2", "table3"]  # Это список ваших таблиц из БД

    def show_db_tables(self):
        # Создаем всплывающее меню для выбора таблицы из БД
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(self.tables_list)
        self.combo_box.currentIndexChanged.connect(self.load_table)

        # Показываем всплывающее меню
        self.combo_box.show()

    def load_table(self):
        # Здесь можно добавить код для загрузки таблицы из БД и отображения её в QTableView
        selected_table = self.combo_box.currentText()
        # Загрузка данных из БД (пока что создаем пустую таблицу для примера)
        QMessageBox.information(self, "Загрузка таблицы", f"Загружаем таблицу: {selected_table}")

        # Здесь вы можете заменить этот код на загрузку данных из вашей БД
        # data = pd.read_sql(f"SELECT * FROM {selected_table}", your_database_connection)
        # self.table_view.setModel(PandasModel(data))

    def show_other_info(self, other_index):
        # Здесь можно добавлять логику или отображение информации для других действий
        QMessageBox.information(self, "Информация", f"Вы выбрали другой элемент {other_index}")

# Запуск приложения
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())