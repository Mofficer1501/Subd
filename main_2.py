import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QTableView
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex

# Модель для отображения данных в QTableView
class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent: QModelIndex = None) -> int:
        return self._data.shape[0]

    def columnCount(self, parent: QModelIndex = None) -> int:
        return self._data.shape[1]

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            else:
                return self._data.index[section]
        return None


# Основное окно приложения
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
        QMessageBox.information(self, "Информация", "Показать таблицы из БД")

    def load_table(self, file_name):
        # Загружаем данные из CSV-файла
        try:
            data = pd.read_csv(file_name)  # Загружаем CSV-файл в DataFrame
            model = PandasModel(data)  # Создаём модель для отображения
            self.table_view.setModel(model)  # Устанавливаем модель в QTableView
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


# Запуск приложения
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
