from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox
)
from PyQt5 import uic
from utils.yaml_loader import load_signals_from_yaml
from models.signal_model import Signal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/main_window.ui", self)

        self.signals = {}
        self.active_signal = None

        self.file_selector_btn.clicked.connect(self.open_file_dialog)
        self.signal_list_dropdown.currentTextChanged.connect(self.display_signal_info)
        self.toolButton_2.clicked.connect(self.set_temp_value_int)
        self.toolButton_3.clicked.connect(self.set_temp_value_enum)
        self.toolButton_4.clicked.connect(self.set_temp_value_double)
        self.signal_true_radio.clicked.connect(lambda: self.set_temp_value_bool(True))
        self.signal_false_radio.clicked.connect(lambda: self.set_temp_value_bool(False))
        self.send_signal_button.clicked.connect(self.commit_value)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select YAML File", "", "YAML Files (*.yml *.yaml)")
        if file_path:
            self.file_name_container.setText(file_path)
            self.signals = load_signals_from_yaml(file_path)
            self.signal_list_dropdown.clear()
            self.signal_list_dropdown.addItems(self.signals.keys())

    def display_signal_info(self, signal_name):
        signal = self.signals.get(signal_name)
        if not signal:
            return

        self.save_temp_value()
        self.active_signal = signal
        self.signal_info_name.setText(signal.name)
        self.signal_info_type.setText(signal.data_type)

        type_map = {
            "bool": 0, "boolean": 0,
            "integer": 1, "int": 1, "uint8": 1,
            "enum": 2, "string": 2,
            "double": 3, "float": 3
        }

        index = type_map.get(signal.data_type.lower(), 0)
        self.stackedWidget.setCurrentIndex(index)

        if index == 0:
            self.signal_true_radio.setChecked(signal.temp_value is True)
            self.signal_false_radio.setChecked(signal.temp_value is False)

        elif index == 1:
            self.signal_value_int.setValue(signal.temp_value or 0)

        elif index == 2:
            self.signal_value_enum.clear()
            self.signal_value_enum.addItems(signal.allowed)
            if signal.temp_value:
                idx = self.signal_value_enum.findText(signal.temp_value)
                if idx >= 0:
                    self.signal_value_enum.setCurrentIndex(idx)

        elif index == 3:
            self.signal_value_double.setValue(signal.temp_value or 0.0)

    def save_temp_value(self):
        if not self.active_signal:
            return
        idx = self.stackedWidget.currentIndex()
        if idx == 0:
            self.active_signal.temp_value = self.signal_true_radio.isChecked()
        elif idx == 1:
            self.active_signal.temp_value = self.signal_value_int.value()
        elif idx == 2:
            self.active_signal.temp_value = self.signal_value_enum.currentText()
        elif idx == 3:
            self.active_signal.temp_value = self.signal_value_double.value()

    def set_temp_value_bool(self, value):
        if self.active_signal:
            self.active_signal.temp_value = value

    def set_temp_value_int(self):
        if self.active_signal:
            self.active_signal.temp_value = self.signal_value_int.value()

    def set_temp_value_enum(self):
        if self.active_signal:
            self.active_signal.temp_value = self.signal_value_enum.currentText()

    def set_temp_value_double(self):
        if self.active_signal:
            self.active_signal.temp_value = self.signal_value_double.value()

    def commit_value(self):
        if self.active_signal:
            self.active_signal.current_value = self.active_signal.temp_value
            QMessageBox.information(self, "Signal Committed", f"{self.active_signal.name} set to {self.active_signal.current_value}")
