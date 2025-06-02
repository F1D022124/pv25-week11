import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QVBoxLayout, QFormLayout, QLineEdit, 
                             QPushButton, QWidget, QScrollArea, QStatusBar, QTextEdit, 
                             QComboBox, QDockWidget, QHBoxLayout, QFileDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QClipboard


class BookApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Week 11 - Ida Ayu Vinaya Anindya (F1D022124)")
        self.setGeometry(100, 100, 800, 600)
        self.clipboard = QApplication.clipboard()

        self.init_db()
        self.init_ui()
        self.set_style()

    def init_db(self):
        self.conn = sqlite3.connect('books.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    def set_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f2f5; }
            QLineEdit, QComboBox { padding: 8px; border: 1px solid #dcdcdc; border-radius: 5px; background-color: white; }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #4CAF50; }
            QPushButton { padding: 8px 16px; border: none; border-radius: 5px; background-color: #4CAF50; color: white; font-weight: bold; }
            QPushButton:hover { background-color: #45a049; }
            QTableWidget { border: 1px solid #dcdcdc; border-radius: 5px; background-color: white; gridline-color: #ececec; }
            QTextEdit { border: 1px solid #dcdcdc; border-radius: 5px; background-color: white; }
            QTabWidget::pane { border: 1px solid #dcdcdc; border-radius: 5px; background-color: white; }
        """)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title or author")
        self.search_input.setFixedWidth(200)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_books)
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.search_button)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        books_widget = QWidget()
        books_layout = QVBoxLayout(books_widget)

        form_widget = QWidget()
        form_layout = QFormLayout()

        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.year_input = QComboBox()
        self.year_input.setEditable(True)
        self.populate_years()

        self.paste_button = QPushButton("Paste Title from Clipboard")
        self.paste_button.clicked.connect(self.paste_from_clipboard)

        self.add_button = QPushButton("Add Book")
        self.update_button = QPushButton("Update Book")
        self.delete_button = QPushButton("Delete Book")
        self.add_button.clicked.connect(self.add_book)
        self.update_button.clicked.connect(self.update_book)
        self.delete_button.clicked.connect(self.delete_book)

        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow(self.paste_button)
        form_layout.addRow("Author:", self.author_input)
        form_layout.addRow("Year:", self.year_input)
        form_layout.addRow(self.add_button)
        form_layout.addRow(self.update_button)
        form_layout.addRow(self.delete_button)

        form_widget.setLayout(form_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidget(form_widget)
        scroll_area.setWidgetResizable(True)
        books_layout.addWidget(scroll_area)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Title", "Author", "Year"])
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.clicked.connect(self.select_book)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        books_layout.addWidget(self.table)
        self.load_books()

        export_widget = QWidget()
        export_layout = QVBoxLayout(export_widget)
        self.export_text = QTextEdit()
        self.export_text.setReadOnly(True)
        export_button = QPushButton("Export to Text")
        export_button.clicked.connect(self.export_to_text)
        export_csv_button = QPushButton("Export to CSV")
        export_csv_button.clicked.connect(self.export_to_csv)
        export_layout.addWidget(self.export_text)
        export_layout.addWidget(export_button)
        export_layout.addWidget(export_csv_button)

        self.tabs.addTab(books_widget, "Books")
        self.tabs.addTab(export_widget, "Export")

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("")

        dock = QDockWidget("Help", self)
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setText("""
        Book Manager Help:
        - Add: Enter title, author, select or type year, and click 'Add Book'
        - Update: Select a book, modify details, click 'Update Book'
        - Delete: Select a book and click 'Delete Book'
        - Search: Enter title or author in the search bar above tabs and click 'Search'
        - Export: Go to Export tab and click 'Export to Text' or 'Export to CSV'
        - Paste: Use clipboard button to paste title or press Ctrl + Shift + V
        """)
        dock.setWidget(help_text)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text(mode=clipboard.Clipboard)

        if text:
            first_line = text.strip().splitlines()[0]
            cleaned = ''.join(c for c in first_line if c.isprintable())
            self.title_input.setText(cleaned)
            self.statusBar.showMessage("Pasted from clipboard.", 3000)
        else:
            self.statusBar.showMessage("Clipboard is empty or not text.", 3000)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier | Qt.ShiftModifier and event.key() == Qt.Key_V:
            self.paste_from_clipboard()
            event.accept()
        else:
            super().keyPressEvent(event)

    def populate_years(self):
        current_year = QDate.currentDate().year()
        for year in range(current_year, 1899, -1):
            self.year_input.addItem(str(year))

    def search_books(self):
        term = self.search_input.text().strip()
        self.table.setRowCount(0)
        if not term:
            self.load_books()
            self.statusBar.showMessage("Displaying all books", 5000)
            return
        self.cursor.execute("SELECT id, title, author, year FROM books WHERE title LIKE ? OR author LIKE ?", (f"%{term}%", f"%{term}%"))
        rows = self.cursor.fetchall()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            item = QTableWidgetItem(row[1])
            item.setData(Qt.UserRole, row[0])
            self.table.setItem(i, 0, item)
            self.table.setItem(i, 1, QTableWidgetItem(row[2]))
            self.table.setItem(i, 2, QTableWidgetItem(str(row[3])))
        self.table.resizeColumnsToContents()
        self.statusBar.showMessage(f"Found {len(rows)} book(s)", 5000)

    def add_book(self):
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        year = self.year_input.currentText().strip()
        if not title or not author or not year:
            self.statusBar.showMessage("All fields must be filled!", 5000)
            return
        try:
            year_int = int(year)
            if not 1900 <= year_int <= QDate.currentDate().year():
                raise ValueError
        except ValueError:
            self.statusBar.showMessage("Year must be valid and between 1900 - current year!", 5000)
            return
        self.cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", (title, author, year_int))
        self.conn.commit()
        self.load_books()
        self.clear_inputs()
        self.statusBar.showMessage("Book added successfully!", 5000)

    def update_book(self):
        selected = self.table.currentRow()
        if selected < 0:
            self.statusBar.showMessage("Please select a book to update!", 5000)
            return
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        year = self.year_input.currentText().strip()
        try:
            year_int = int(year)
        except ValueError:
            self.statusBar.showMessage("Year must be valid!", 5000)
            return
        id_ = int(self.table.item(selected, 0).data(Qt.UserRole))
        self.cursor.execute("UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?", (title, author, year_int, id_))
        self.conn.commit()
        self.load_books()
        self.clear_inputs()
        self.statusBar.showMessage("Book updated successfully!", 5000)

    def delete_book(self):
        selected = self.table.currentRow()
        if selected < 0:
            self.statusBar.showMessage("Please select a book to delete!", 5000)
            return
        id_ = int(self.table.item(selected, 0).data(Qt.UserRole))
        self.cursor.execute("DELETE FROM books WHERE id = ?", (id_,))
        self.conn.commit()
        self.load_books()
        self.clear_inputs()
        self.statusBar.showMessage("Book deleted successfully!", 5000)

    def select_book(self):
        row = self.table.currentRow()
        if row >= 0:
            self.title_input.setText(self.table.item(row, 0).text())
            self.author_input.setText(self.table.item(row, 1).text())
            self.year_input.setCurrentText(self.table.item(row, 2).text())

    def load_books(self):
        self.table.setRowCount(0)
        self.cursor.execute("SELECT id, title, author, year FROM books")
        rows = self.cursor.fetchall()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            item = QTableWidgetItem(row[1])
            item.setData(Qt.UserRole, row[0])
            self.table.setItem(i, 0, item)
            self.table.setItem(i, 1, QTableWidgetItem(row[2]))
            self.table.setItem(i, 2, QTableWidgetItem(str(row[3])))
        self.table.resizeColumnsToContents()

    def export_to_text(self):
        self.cursor.execute("SELECT title, author, year FROM books")
        rows = self.cursor.fetchall()
        content = "List of Books:\n\n" + "\n\n".join([f"Title: {t}\nAuthor: {a}\nYear: {y}" for t, a, y in rows])
        self.export_text.setText(content)
        self.statusBar.showMessage("Books exported to text!", 5000)

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "books.csv", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Title", "Author", "Year"])
                self.cursor.execute("SELECT title, author, year FROM books")
                writer.writerows(self.cursor.fetchall())
            self.statusBar.showMessage(f"Books exported to CSV at {path}!", 5000)

    def clear_inputs(self):
        self.title_input.clear()
        self.author_input.clear()
        self.year_input.setCurrentIndex(-1)

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BookApp()
    window.show()
    sys.exit(app.exec_())
