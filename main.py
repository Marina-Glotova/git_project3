import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QWidget, QMessageBox
import main_form, addEditCoffeeForm


class MyWidget(QMainWindow, main_form.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect("data/coffee.sqlite")
        self.select_id = ''
        self.btn.clicked.connect(self.result)
        self.create.clicked.connect(self.run_form)
        self.update.clicked.connect(self.check)

    def result(self):
        cur = self.con.cursor()
        result = cur.execute("""SELECT Coffee.ID, 
                                       Coffee.title, 
                                       roast.title,
                                       Coffee.grind,
                                       Coffee.taste,
                                       Coffee.price, 
                                       Coffee.volume FROM Coffee
                                       LEFT JOIN roast ON Coffee.roasting = roast.ID""").fetchall()
        try:
            titles = ["ID", "название сорта", "степень обжарки", "молотый/в зернах", "описание вкуса", "цена",
                           "объем упаковки"]
            self.tableWidget.setColumnCount(len(result[0]))
            self.tableWidget.setRowCount(len(result))
            self.tableWidget.setHorizontalHeaderLabels(titles)
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.statusBar().showMessage("")
        except Exception:
            self.statusBar().showMessage("По этому запросу ничего не найдено")

    def check(self):
        if self.tableWidget.selectedIndexes():
            rs = list(set([i.row() for i in self.tableWidget.selectedItems()]))
            ids = [self.tableWidget.item(i, 0).text() for i in rs][-1]
            valid = QMessageBox.question(self, '',
                                         "Действительно заменить элемент с id " + ids, QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                self.select_id = ids
                self.run_form()
        else:
            valid = QMessageBox.question(self, '',
                                         "Необходимо выделить элемент для его изменения", QMessageBox.Yes)

    def run_form(self):
        self.add_form = MyWidget2(self, self.sender().text(), self.select_id)
        self.add_form.show()


class MyWidget2(QWidget, addEditCoffeeForm.Ui_Form):
    def __init__(self, *args):
        super().__init__()
        self.action, self.id = args[-2], args[-1]
        self.setupUi(self)
        self.radioButton_2.setChecked(True)
        self.buttonGroup.buttonClicked.connect(self.format)
        self.form_coffee = ''
        self.con = sqlite3.connect("data/coffee.sqlite")
        self.roast = []
        self.add_roasting()
        self.run.clicked.connect(self.add_edit)

    def add_roasting(self):
        cur = self.con.cursor()
        result = cur.execute("""SELECT title FROM roast""").fetchall()
        for el in result:
            self.roast.append(el[0])
        self.comboBox.addItems(sorted(self.roast))

    def format(self, rb):
        self.form_coffee = rb.text()

    def add_edit(self):
        try:
            if self.type_coffee.toPlainText() == '':
                raise ValueError("Не заполнено поле с названием сорта кофе")
            elif self.taste.toPlainText() == '':
                raise ValueError("Не заполнено поле с описанием вкуса")
            elif not self.price.toPlainText().isdigit() or self.price.toPlainText() == '':
                raise ValueError("Не заполнено поле с ценой или неверный формат")
            elif not self.volume.toPlainText().isdigit() or self.volume.toPlainText() == '':
                raise ValueError("Не заполнено поле с объемом упаковки или неверный формат")
            else:
                self.info.setText('')
                type_coffee = self.type_coffee.toPlainText().strip()
                degree_roast = self.comboBox.currentText()
                taste = ' '.join(self.taste.toPlainText().strip().split('\n'))
                price = int(self.price.toPlainText().strip())
                volume = int(self.volume.toPlainText().strip())
                data = (type_coffee, degree_roast, self.form_coffee, taste, price, volume)
                cur = self.con.cursor()
                res = cur.execute("""SELECT id FROM roast WHERE title = ?""", (degree_roast, )).fetchone()
                data = (type_coffee, res[0], self.form_coffee, taste, price, volume)
                if self.action == 'Создать':
                    cur.execute("""INSERT INTO Coffee(title, roasting, grind, taste, price, volume) 
                                          VALUES(?, ?, ?, ?, ?, ?)""", data)
                else:
                    data = (type_coffee, res[0], self.form_coffee, taste, price, volume, self.id)
                    cur.execute("""UPDATE Coffee SET 
                             title = ?, roasting = ?, grind = ?, taste = ?, price = ?, volume = ? WHERE id = ?""", data)
            self.con.commit()
            self.close()
            self.con.close()
        except (ValueError, TypeError) as e:
            self.info.setText(f'{e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())