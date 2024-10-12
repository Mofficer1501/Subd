import sys  # sys нужен для передачи argv в QApplication
import os  # Отсюда нам понадобятся методы для отображения содержимого директорий
import sqlite3
import pandas as pd

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QStandardItemModel, QStandardItem

import MainForm  # Это наш конвертированный файл дизайна

class MainWindow(QtWidgets.QMainWindow, MainForm.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowState(Qt.WindowState.WindowFullScreen)


        '''-------------------Пропорциональное размещение виджетов-------------------------------------------'''
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        self.model = QStandardItemModel()
        self.tableView.setModel(self.model)

        '''-------------------Привязка таблиц к виджету-------------------------------------------'''
        self.kontrakti_data = self.get_table('Kontrakti')
        self.statistics_data = self.get_table('Statistika')

        self.Kontrakti.triggered.connect(lambda: self.load_table_from_db('Kontrakti'))
        self.Statistika.triggered.connect(lambda: self.load_table_from_db('Statistika'))
        self.Union.triggered.connect(self.to_update_or_create_union_table)

        '''-------------------Компоновка элементов главного окна-------------------------------------------'''
        # Создаем центральный виджет
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        # Создаем вертикальный layout и устанавливаем его в центральный виджет
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        # Создаем QTableView
        self.tableView = QtWidgets.QTableView()
        self.layout.addWidget(self.tableView)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.EditButton)
        self.button_layout.addWidget(self.AddButton)
        self.button_layout.addWidget(self.DeleteButton)
        self.layout.addLayout(self.button_layout)



    def get_table(self, table_name):
        conn = sqlite3.connect('Subd.db')
        data = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return data
    def get_column_names(self, table_name):
        # Подключаемся к базе данных
        conn = sqlite3.connect('Subd.db')

        # Выполняем SQL-запрос для получения названий столбцов
        query = f"PRAGMA table_info({table_name})"
        columns_info = pd.read_sql_query(query, conn)

        # Извлекаем названия столбцов
        column_names = columns_info['name'].tolist()

        conn.close()
        return column_names
    def to_update_or_create_union_table(self):
        # Объединяем данные
        merged_data = pd.merge(self.kontrakti_data, self.statistics_data, on='name', how='outer')

        # Переименовываем столбцы для новой таблицы
        merged_data.columns = ['name'] + [f'{col}' for col in self.get_column_names('Statistika') if col != 'name'] + \
                              [f'{col}' for col in self.get_column_names('Kontrakti') if col != 'name']

        # Сохраняем объединенные данные в новую таблицу
        conn = sqlite3.connect('Subd.db')
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS Union_table")
        conn.commit()
        merged_data.to_sql('Union_table', conn, if_exists='replace',
                           index=False)  # Если таблица существует, заменяем её
        conn.close()
        # Загружаем данные из новой таблицы в QTableWidget
        self.load_table_from_db('Union_table')
    def load_table_from_db(self, table_name):
        # Используем Pandas для загрузки данных
        conn = sqlite3.connect('Subd.db')
        data = pd.read_sql_query((f"SELECT * FROM {table_name}"), conn)
        conn.close()
        self.data_to_table(data)
    def data_to_table(self, data):
        self.model.clear()  # Очищаем предыдущие данные

        if not data.empty:
            # Устанавливаем заголовки столбцов
            self.model.setHorizontalHeaderLabels(data.columns.tolist())

            # Заполняем модель данными
            for row_index, row_data in data.iterrows():
                items = [QStandardItem(str(item)) for item in row_data]
                self.model.appendRow(items)

            self.tableView.setModel(self.model)


#       '''-------------------Привязка таблиц к виджету-------------------------------------------'''

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()  # Используем ваш класс MainWindow
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()



    '''def data_to_table(self, data):
        # Очистка текущих данных в таблице
        self.table_widget.clear()

        # Проверка, что данные не пустые
        if data.empty:
            print("Данные пустые.")
            return

        # Заполнение таблицы данными
        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(data.columns))
        self.table_widget.setHorizontalHeaderLabels(data.columns.tolist())

        for row_idx, row in data.iterrows():
            for col_idx, value in enumerate(row):
                self.table_widget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(value)))'''

'''def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())'''