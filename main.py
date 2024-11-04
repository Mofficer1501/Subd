import sys  # sys нужен для передачи argv в QApplication
import os  # Отсюда нам понадобятся методы для отображения содержимого директорий
import sqlite3
import pandas as pd

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QStandardItemModel, QStandardItem

import MainForm  # Это наш конвертированный файл дизайна

class MainWindow(QtWidgets.QMainWindow, MainForm.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        db_name = 'Subd2.db'
        
        self.table_name = None

        '''-------------------Пропорциональное размещение виджетов-------------------------------------------'''
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        self.model = QStandardItemModel()
        self.tableView.setModel(self.model)
        self.tableView.hideColumn(0)
        '''-----------------------------------------------------------------------------------------'''

        # start_date, name, exec_date, price, min_price, max_price, contacts_quantity


        '''-------------------Привязка таблиц к виджету-------------------------------------------'''
        self.kontrakti_data = self.get_table('contractss', db_name)
        self.statistics_data = self.get_table('stat', db_name)

        self.Kontrakti.triggered.connect(lambda: self.load_table_from_db('contractss', db_name))
        self.Statistika.triggered.connect(lambda: self.load_table_from_db('stat', db_name))
        self.Union.triggered.connect(lambda: self.update_summary_table(db_name))
        '''-----------------------------------------------------------------------------------------'''
        
        


        '''-------------------Компоновка элементов главного окна-------------------------------------------'''
        # Создаем центральный виджет
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        # Создаем вертикальный layout и устанавливаем его в центральный виджет
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        # Создаем QTableView
        self.tableView = QtWidgets.QTableView()
        
        self.tableView.verticalHeader().setVisible(True)

        # Выделение всей строки при наведении 

        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)

        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        self.tableView.setFocus()
        self.layout.addWidget(self.tableView)
        

        # Кнопки
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.EditButton)
        self.button_layout.addWidget(self.AddButton)
        self.button_layout.addWidget(self.DeleteButton)
        self.DeleteButton.clicked.connect(self.confirmAndDeleteSelectedRows)
        self.EditButton.clicked.connect(self.editRecord)
        self.AddButton.clicked.connect(self.addRecord)
        self.layout.addLayout(self.button_layout)
        # self.layout.addWidget(self.formWidget)
        # self.layout.addWidget(self.formTypeLabel)
        '''-----------------------------------------------------------------------------------------'''
    
    def editRecord(self): # ----------------
        self.open_popup()
        print('table_name=',self.table_name)
        selectedIndexes = self.tableView.selectionModel().selectedRows()
        if not selectedIndexes:
            return
        index = selectedIndexes[0].row()

        if self.table_name == 'contractss':
            self.nameEdit.setText(self.model.item(index, 1).text())
            self.codeEdit.setText(self.model.item(index, 2).text())
            self.dateEdit.setDate(QDate.fromString(self.model.item(index, 3).text(), "dd-MMM-yy"))
            self.idEdit.setText(self.model.item(index, 0).text()) 
        elif self.table_name == 'stat':
            self.nameEdit.setText(self.model.item(index, 1).text())
            self.start_dateEdit.setDate(QDate.fromString(self.model.item(index, 2).text(), "dd-MMM-yy"))
            self.dateEdit.setDate(QDate.fromString(self.model.item(index, 3).text(), "dd-MMM-yy"))
            self.idEdit.setText(self.model.item(index, 0).text())
            self.priceEdit.setText(self.model.item(index, 4).text())
            self.min_priceEdit.setText(self.model.item(index, 5).text())
            self.max_priceEdit.setText(self.model.item(index, 6).text())
            self.quantEdit.setText(self.model.item(index, 7).text())
        else :
            return

        self.formWidget.show()
        # self.formTypeLabel.setText("Редактирование записи")
        # self.formTypeLabel.show()
        # self.toggleButtons(False)
        self.currentRow = index
    

    # Добавление записи
    def addRecord(self):
        self.open_popup()
        self.nameEdit.clear()
        self.priceEdit.clear()
        self.start_dateEdit.clear()
        self.max_priceEdit.clear()
        self.min_priceEdit.clear()
        self.quantEdit.clear()
        self.codeEdit.clear()
        self.idEdit.clear()
        self.dateEdit.setDate(QDate.currentDate())
        # self.formWidget.show()
        self.currentRow = None
    
    def saveRecord(self):
        db_name = 'Subd2.db' # ----------------
        table_name = self.table_name 
        # self.open_popup()
        if table_name == 'contractss':
            name = self.nameEdit.text()
            code = self.codeEdit.text()
            date = self.dateEdit.date().toString("dd-MMM-yy")
        elif table_name == 'stat':
            name = self.nameEdit.text()   
            start_date = self.start_dateEdit.text()
            day_end = self.dateEdit.text()
            price = self.priceEdit.text()
            min_price = self.min_priceEdit.text()
            max_price = self.max_priceEdit.text()
            quant = self.quantEdit.text()

        if self.currentRow != None:
            id = self.idEdit.text()


        # if not self.validateInput(name, code):
        #     QtWidgets.QMessageBox.warning(self, "Ошибка", "Некорректный ввод данных.")
        #     return

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        if self.currentRow is None:
            if table_name == 'contractss':
                cursor.execute(f"INSERT INTO {table_name} (name, base, exec_date) VALUES (?, ?, ?)", (name, code, date))
                new_id = cursor.lastrowid
                print("newId=",new_id)
                self.model.insertRow(0, [
                    QStandardItem(str(new_id)),
                    QStandardItem(name),
                    QStandardItem(code),
                    QStandardItem(date)
                ])
            elif table_name == 'stat':
                cursor.execute(f"INSERT INTO {table_name} (name, start_date, day_end,price,min_price,max_price,contracts_quantity) VALUES (?, ?, ?, ?, ?, ?,?)", (name, start_date, day_end,price,min_price,max_price,quant))
                new_id = cursor.lastrowid
                print("newId=",new_id)
                self.model.insertRow(0, [
                    QStandardItem(str(new_id)),
                    QStandardItem(name),
                    QStandardItem(start_date),
                    QStandardItem(day_end),
                    QStandardItem(price),
                    QStandardItem(min_price),
                    QStandardItem(max_price),
                    QStandardItem(quant)
                ])
                print('stat')   
            self.tableView.selectRow(0)
        else:
            if table_name == 'contractss':
                cursor.execute(f"UPDATE {table_name} SET name=?, base=?, exec_date=? WHERE id=?", (name, code, date, id))
                print(id)
                self.model.setItem(self.currentRow, 0, QStandardItem(id))
                self.model.setItem(self.currentRow, 1, QStandardItem(name))
                self.model.setItem(self.currentRow, 2, QStandardItem(code))
                self.model.setItem(self.currentRow, 3, QStandardItem(date))
                self.tableView.selectRow(self.currentRow)
            elif table_name == 'stat':
                cursor.execute(f"UPDATE {table_name} SET name=?, start_date=?, day_end=?, price=?, min_price=?, max_price=?,contracts_quantity=? WHERE id=?", (name, start_date, day_end,price,min_price,max_price,quant, id))
                print(id)
                self.model.setItem(self.currentRow, 0, QStandardItem(id))
                self.model.setItem(self.currentRow, 1, QStandardItem(name))
                self.model.setItem(self.currentRow, 2, QStandardItem(start_date))
                self.model.setItem(self.currentRow, 3, QStandardItem(day_end))
                self.model.setItem(self.currentRow, 4, QStandardItem(price))
                self.model.setItem(self.currentRow, 5, QStandardItem(min_price))
                self.model.setItem(self.currentRow, 6, QStandardItem(max_price))
                self.model.setItem(self.currentRow, 7, QStandardItem(quant))
                self.tableView.selectRow(self.currentRow)  
            
        conn.commit()
        conn.close()
        
        self.nameEdit.clear()
        self.priceEdit.clear()
        self.start_dateEdit.clear()
        self.max_priceEdit.clear()
        self.min_priceEdit.clear()
        self.quantEdit.clear()
        self.codeEdit.clear()
        self.idEdit.clear()
        self.dateEdit.clear()
        # self.formWidget.show()
        self.currentRow = None
        self.formWidget.reject()
        QtWidgets.QMessageBox.information(self, "Сохранено", "Запись успешно сохранена.")
        # self.formWidget.hide()
        # self.formTypeLabel.hide()
        # self.toggleButtons(True)
        # self.formWidget.setParent(None)
        # self.layout.removeWidget(self.formWidget)
    
    def open_popup(self):
        # self.saveButton = QtWidgets.QPushButton("Сохранить")
        # self.saveButton.clicked.connect(self.saveRecord)
        self.formLayout = QtWidgets.QFormLayout()
        self.nameEdit = QtWidgets.QLineEdit()
        self.nameEdit.setInputMask("00000-0000")
        self.priceEdit = QtWidgets.QLineEdit()
        self.priceEdit.setPlaceholderText("Цена фьючерса")
        self.min_priceEdit = QtWidgets.QLineEdit()
        self.min_priceEdit.setPlaceholderText("минимальная цена фьючерса")
        self.max_priceEdit = QtWidgets.QLineEdit()
        self.max_priceEdit.setPlaceholderText("максимальная цена фьючерса")
        self.quantEdit = QtWidgets.QLineEdit()
        
        self.codeEdit = QtWidgets.QLineEdit()
        self.codeEdit.setPlaceholderText("код фьючерса")
        self.idEdit = QtWidgets.QLineEdit()
        self.dateEdit = QtWidgets.QDateEdit(calendarPopup=True)
        self.dateEdit.setDisplayFormat("dd-MMM-yy")

        self.start_dateEdit = QtWidgets.QDateEdit(calendarPopup=True)
        self.start_dateEdit.setDisplayFormat("dd-MMM-yy")

        if self.table_name == 'contractss':
            self.formLayout.addRow("Название:", self.nameEdit)
            self.formLayout.addRow("Код:", self.codeEdit)
            self.formLayout.addRow("Дата исполнения:", self.dateEdit)
            # self.formLayout.addRow(self.saveButton)
        elif self.table_name == 'stat':
            self.formLayout.addRow("Название:", self.nameEdit)
            self.formLayout.addRow("Дата начала:", self.start_dateEdit)
            self.formLayout.addRow("Дата исполнения:", self.dateEdit)
            self.formLayout.addRow("Цена:", self.priceEdit)
            self.formLayout.addRow("Минимальная цена:", self.min_priceEdit)
            self.formLayout.addRow("Максимальная цена:", self.max_priceEdit)
            self.formLayout.addRow("Количество:", self.quantEdit)
            # self.formLayout.addRow(self.saveButton)
        self.formWidget = QtWidgets.QDialog()
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.formLayout.addRow(buttonBox)
        buttonBox.accepted.connect(self.saveRecord)
        buttonBox.rejected.connect(self.formWidget.reject)
        # self.formWidget = QtWidgets.QWidget()
        

        self.formWidget.setLayout(self.formLayout)
        self.formWidget.open()
        # self.formWidget.hide()
        # self.layout.addWidget(self.formWidget)
        return 
    # Валидация ввода
    def validateInput(self, name, code):
        if not name or not code:
            return False
        if not name.split('-')[0].isdigit() or len(name.split('-')[0]) != 5:
            return False
        if not name.split('-')[1].isdigit() or len(name.split('-')[1]) != 4:
            return False
        return True     

    def confirmAndDeleteSelectedRows(self): # ----------------
        db_name = 'Subd2.db' # ----------------
        table_name = self.table_name
        # selectionModel = self.tableView.selectionModel()
        # selectedRows = selectionModel.selectedRows()
        selectedRows = self.tableView.selectionModel().selectedRows()
        
        ids = [self.model.item(index.row(), 0).text() for index in selectedRows]
        # print(selectedRows[0].model)

        # if not selectedRows:
        #     return

        rowIndices = sorted(index.row() for index in selectedRows)
        print(rowIndices)
        # ids = [self.model.data(index.siblingAtColumn(0)) for index in selectedRows]
        ranges = self.formatRanges(rowIndices)

        reply = QtWidgets.QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить следующие строки: {ranges}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            for index in ids:
                cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (index,))
                # self.model.removeRow(index)

            for i in reversed(rowIndices):
                self.model.removeRow(i)
            conn.commit()
            conn.close()            

    # Форматирование диапазонов
    def formatRanges(self, indices):
        if not indices:
            return ""

        ranges = []
        start = indices[0]
        end = indices[0]

        for i in range(1, len(indices)):
            if indices[i] == end + 1:
                end = indices[i]
            else:
                if start == end:
                    ranges.append(f"{start+1}")
                else:
                    ranges.append(f"{start+1}-{end+1}")
                start = end = indices[i]

        # Добавляем последний диапазон
        if start == end:
            ranges.append(f"{start+1}")
        else:
            ranges.append(f"{start+1}-{end+1}")
        return ", ".join(ranges)    

    def get_table(self, table_name, db_name):
        conn = sqlite3.connect(db_name)
        data = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return data
    
    def get_column_names(self, table_name, db_name):
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_name)

        # Выполняем SQL-запрос для получения названий столбцов
        query = f"PRAGMA table_info({table_name})"
        columns_info = pd.read_sql_query(query, conn)

        # Извлекаем названия столбцов
        column_names = columns_info['name'].tolist()

        conn.close()
        return column_names
    
    # def to_update_or_create_union_table(self, db_name):
    #     # Объединяем данные
    #     merged_data = pd.merge(self.kontrakti_data, self.statistics_data, on='name', how='outer')

    #     # Переименовываем столбцы для новой таблицы
    #     merged_data.columns = ['name'] + [f'{col}' for col in self.get_column_names('stat', db_name) if col != 'name'] + \
    #                           [f'{col}' for col in self.get_column_names('contractss', db_name) if col != 'name']

    #     # Сохраняем объединенные данные в новую таблицу
    #     conn = sqlite3.connect(db_name)
    #     cursor = conn.cursor()
    #     cursor.execute("DROP TABLE IF EXISTS Union_table")
    #     conn.commit()
    #     merged_data.to_sql('Union_table', conn, if_exists='replace',
    #                        index=False)  # Если таблица существует, заменяем её
    #     conn.close()
    #     # Загружаем данные из новой таблицы в QTableWidget
    #     self.load_table_from_db('Union_table', db_name)


    # def create_summary_table():
    #     
    #     """Создает сводную таблицу, если она еще не существует."""
    #     create_table_sql = """
    #     CREATE TABLE IF NOT EXISTS summary (
    #         id INTEGER PRIMARY KEY,
    #         contractss_id INTEGER,
    #         stat_id INTEGER,
    #         name TEXT,
    #         other_contractss_columns TEXT,
    #         other_stat_columns TEXT
    #     );
    #     """
    #     conn.execute(create_table_sql)
    #     conn.commit()

    def update_summary_table(self,db_name):
        
        conn = sqlite3.connect(db_name)
        """Обновляет сводную таблицу."""
        # Удаляем все записи из сводной таблицы
        conn.execute("DELETE FROM summary")
        
        # Вставляем обновленные данные
        insert_sql = """
        INSERT INTO summary (name,start_date,day_end,price,min_price,max_price,contracts_quantity,exec_date,base)
        SELECT s.name, s.start_date,s.day_end,s.price,s.min_price,s.max_price,s.contracts_quantity,c.exec_date,c.base
        FROM contractss c
        JOIN stat s ON c.name = s.name;
        """
        conn.execute(insert_sql)
        conn.commit()
        conn.close()
        self.load_table_from_db('summary',db_name )




    def load_table_from_db(self, table_name, db_name):
        self.table_name = table_name
        # Используем Pandas для загрузки данных
        conn = sqlite3.connect(db_name)
        data = pd.read_sql_query((f"SELECT * FROM {table_name}"), conn)
        flag = table_name
        conn.close()
        self.data_to_table(data)

    def data_to_table(self, data):
        self.model.clear()  # Очищаем предыдущие данные

        if not data.empty:
            # Устанавливаем заголовки столбцов
            self.model.setHorizontalHeaderLabels(data.columns.tolist())
            li = ['Название','Название','Название',]

            # Заполняем модель данными
            for row_index, row_data in data.iterrows():
                items = [QStandardItem(str(item)) for item in row_data]
                self.model.insertRow(0,items)

            # for row_index, row_data in data.iterrows():
            #     items = [QStandardItem(str(item)) for item in row_data]
            #     self.model.appendRow(items)

            self.tableView.setModel(self.model)
            # self.tableView.hideColumn(0) # Раскоментировать при production

    def toggleButtons(self, show):
        self.EditButton.setVisible(show)
        self.AddButton.setVisible(show)
        self.DeleteButton.setVisible(show)        

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