import sys
from PyQt6.QtSql import QSqlTableModel, QSqlQuery
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QTableView
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtWidgets import QHeaderView
from numba.np.arraymath import ov_np_where_x_y


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


# Основное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.menu_bar = self.menuBar()

        '''first menu button'''
        self.db_menu_db_table = self.menu_bar.addMenu("Таблицы")

        '''self.db_action = QAction("Подключить БД", self)
        self.db_action.triggered.connect(self.show_db_tables)'''

        self.other_action_1_1 = QAction("Статистика торгов", self)
        self.other_action_1_1.triggered.connect(lambda: self.load_table("f_zb.csv"))

        self.other_action_2_1 = QAction("Контракты", self)
        self.other_action_2_1.triggered.connect(lambda: self.load_table("Zb.csv"))

        self.other_action_3_1 = QAction("Объединенная таблица", self)
        self.other_action_3_1.triggered.connect(lambda: self.load_table("union.csv"))

        #self.db_menu_db_table.addAction(self.db_action)
        self.db_menu_db_table.addAction(self.other_action_1_1)
        self.db_menu_db_table.addAction(self.other_action_2_1)
        self.db_menu_db_table.addAction(self.other_action_3_1)
        '''--------------------------'''



        '''second menu button'''
        self.db_menu_help = self.menu_bar.addMenu("Справка")

        ''' self.db_action = QAction("Подключить БД", self)
            self.db_action.triggered.connect(self.show_db_tables)'''

        ''' self.other_action_1_2 = QAction("f_zb.csv", self)
            self.other_action_1_2.triggered.connect(lambda: self.load_table("f_zb.csv"))
    
            self.other_action_2_2 = QAction("Zb.csv", self)
            self.other_action_2_2.triggered.connect(lambda: self.load_table("Zb.csv"))
    
            #self.db_menu_help.addAction(self.db_action)
            self.db_menu_help.addAction(self.other_action_1_2)
            self.db_menu_help.addAction(self.other_action_2_2)'''
        '''--------------------------'''




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

    '''def show_db_tables(self):
        # Здесь можно добавить код для выбора таблиц
        QMessageBox.information(self, "Информация", "Показать таблицы из БД")'''

    #def add_row(self):

    #def edit_table(self):

    '''def delete_row(self):
        current_index = self.table_view.currentIndex()
        if current_index.isValid():'''


    def load_table(self, file_name):
        # Загружаем данные из CSV-файла
        try:
            data = pd.read_csv(file_name)  # Загружаем CSV-файл в DataFrame
            model = PandasModel(data)  # Создаём модель для отображения
            self.table_view.setModel(model)  # Устанавливаем модель в QTableView
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def show_table(self, table_name):
        self.model = QSqlTableModel(self, self.db)
        self.model.setTable(table_name)

        # Получение названий столбцов из БД
        query = QSqlQuery(self.db)
        query.exec(f"SELECT * FROM {table_name} LIMIT 1")
        column_names = [query.record().fieldName(i) for i in range(query.record().count())]

        # Установка заголовков столбцов модели
        '''self.model.setHeaderData(0, Qt.Orientation.Horizontal, column_names[0])
        self.model.setHeaderData(1, Qt.Orientation.Horizontal, column_names[1])'''

        # ... добавить установку заголовков для всех столбцов ...
        for i, name in enumerate(column_names):
            self.model.setHeaderData(i, Qt.Orientation.Horizontal, name)

        self.model.select()
        self.table_view.setModel(self.model)

        # Устанавливаем свойство horizontalHeader для отображения заголовков
        self.table_view.horizontalHeader().setVisible(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


# Запуск приложения
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())