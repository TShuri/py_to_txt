import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QRadioButton,
    QLabel, QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from converter import convert_py_to_txt, convert_txt_to_py


class ConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Py ↔ Txt Конвертер")
        self.resize(600, 450)

        layout = QVBoxLayout(self)

        # Выбор способа загрузки
        layout.addWidget(QLabel("Выберите способ загрузки файлов:"))

        self.rb_manual = QRadioButton("Через кнопку")
        self.rb_drag = QRadioButton("Перетаскиванием")
        self.rb_manual.setChecked(True)

        source_layout = QHBoxLayout()
        source_layout.addWidget(self.rb_manual)
        source_layout.addWidget(self.rb_drag)
        layout.addLayout(source_layout)

        self.rb_manual.toggled.connect(self.update_input_mode)

        # Режим конвертации
        layout.addWidget(QLabel("Режим конвертации:"))

        self.rb_py_to_txt = QRadioButton("py → txt")
        self.rb_txt_to_py = QRadioButton("txt → py")
        self.rb_py_to_txt.setChecked(True)

        convert_layout = QHBoxLayout()
        convert_layout.addWidget(self.rb_py_to_txt)
        convert_layout.addWidget(self.rb_txt_to_py)
        layout.addLayout(convert_layout)

        # Чекбокс на удаление
        self.delete_checkbox = QCheckBox("Удалить исходные файлы после конвертации")
        layout.addWidget(self.delete_checkbox)

        # Кнопка выбора файлов
        self.select_button = QPushButton("Выбрать файлы")
        self.select_button.clicked.connect(self.on_select_button)
        layout.addWidget(self.select_button)

        # Кнопка конвертации
        self.convert_button = QPushButton("Конвертировать")
        self.convert_button.clicked.connect(self.on_convert_button)
        layout.addWidget(self.convert_button)

        # Кнопка сброса
        self.reset_button = QPushButton("Сбросить")
        self.reset_button.clicked.connect(self.on_reset_button)
        layout.addWidget(self.reset_button)

        # Поле вывода (и drag-and-drop зона)
        self.text_output = QTextEdit(readOnly=True)
        self.text_output.setAcceptDrops(True)
        self.text_output.installEventFilter(self)
        layout.addWidget(self.text_output)

        self.setLayout(layout)
        self.update_input_mode()

    def update_input_mode(self):
        """Обновить отображение UI в зависимости от выбранного режима"""
        if self.rb_manual.isChecked():
            self.select_button.setEnabled(True)
            self.text_output.setPlaceholderText("Сюда будет выведен список выбранных файлов")
        else:
            self.select_button.setEnabled(False)
            self.text_output.setPlaceholderText("Перетащите сюда файлы .py или .txt")

    def on_select_button(self):
        if self.rb_py_to_txt.isChecked():
            file_filter = "Python Files (*.py)"
        else:
            file_filter = "Text Files (*.txt)"

        files, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы", "", file_filter)

        if files:
            all_files = set(self.selected_files)
            all_files.update(files)
            self.selected_files = list(all_files)

            self.text_output.setPlainText("Выбранные файлы:\n" + "\n".join(self.selected_files))
            self.select_button.setText("Добавить файлы")
        else:
            if not self.selected_files:
                self.text_output.setPlainText("Файлы не выбраны.")

    def on_convert_button(self):
        if not self.selected_files:
            QMessageBox.information(self, "Нет файлов", "Сначала выберите или перетащите файлы.")
            return

        delete_original = self.delete_checkbox.isChecked()

        try:
            if self.rb_py_to_txt.isChecked():
                converted = convert_py_to_txt(self.selected_files, delete_original)
            else:
                converted = convert_txt_to_py(self.selected_files, delete_original)

            if converted:
                msg = "Сконвертированы файлы:\n" + "\n".join(converted)
            else:
                msg = "Нет подходящих файлов для конвертации."

            self.text_output.setPlainText(msg)
            self.selected_files = []
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def on_reset_button(self):
        self.selected_files = []
        self.text_output.clear()
        self.rb_py_to_txt.setChecked(True)
        self.delete_checkbox.setChecked(False)
        self.select_button.setText("Выбрать файлы")

    # === Drag and drop ===
    def eventFilter(self, source, event):
        if source == self.text_output:
            if event.type() == event.Type.DragEnter:
                return self.dragEnterEvent(event)
            elif event.type() == event.Type.Drop:
                return self.dropEvent(event)
        return super().eventFilter(source, event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if self.rb_drag.isChecked() and event.mimeData().hasUrls():
            event.acceptProposedAction()
            return True
        return False

    def dropEvent(self, event: QDropEvent):
        if not self.rb_drag.isChecked():
            return False

        urls = event.mimeData().urls()
        new_files = []

        for url in urls:
            path = url.toLocalFile()
            if path.endswith(".py") and self.rb_py_to_txt.isChecked():
                new_files.append(path)
            elif path.endswith(".txt") and self.rb_txt_to_py.isChecked():
                new_files.append(path)

        if new_files:
            all_files = set(self.selected_files)
            all_files.update(new_files)
            self.selected_files = list(all_files)

            self.text_output.setPlainText("Выбранные файлы:\n" + "\n".join(self.selected_files))
        else:
            QMessageBox.information(self, "Нет подходящих файлов", "Перетащите .py или .txt в соответствии с режимом.")
        return True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConverterApp()
    window.show()
    sys.exit(app.exec())
