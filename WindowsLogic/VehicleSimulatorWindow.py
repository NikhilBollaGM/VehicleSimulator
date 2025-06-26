import sys
from kuksa_send_receive_vss import * 
from DataBrokerHandler import (check_kuksa_connection, establishKuskaConnection)
from PyQt5.QtWidgets import (
    QDialog, QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QRadioButton,
    QTextEdit, QStackedWidget, QSpinBox, QDoubleSpinBox, QGroupBox, QGridLayout
)
from PyQt5 import uic
from Util.yaml_loader import load_signals_from_yaml
from enum import Enum


 
 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/mainWindow.ui",self)

        self.signals= {} 
        self.actionBrowse_file.triggered.connect(self.open_file_dialog) 
        self.signal_list_dropdown.currentTextChanged.connect(self.on_signal_selected) #when clicked on any item in dropdown
        self.actionEstablish_connection_2.triggered.connect(self.showConnectionDialog)
        self.toolButton_2.clicked.connect(self.set_temp_value_int)
        self.toolButton_3.clicked.connect(self.set_temp_value_enum)
        self.toolButton_4.clicked.connect(self.set_temp_value_double)
        self.signal_true_radio.clicked.connect(lambda: self.set_temp_value_bool(True))
        self.signal_false_radio.clicked.connect(lambda: self.set_temp_value_bool(False))
        self.send_signal_button.clicked.connect(self.commit_value)

    #function to show connection dialog box
    def showConnectionDialog(self):
        dialog = uic.loadUi("UI/connectionDialogBox.ui")
        dialog.databroker_connect_button.clicked.connect(lambda: self.onEstablishConnection(dialog)) #lambda 

        print("action clicked")
        dialog.exec_()

    # when clickedon connect button   
    def onEstablishConnection(self, dialog):
        print("Executing")
        port=dialog.port_input.text()
        ip=dialog.ip_address_input.text()
        kuksaconnector =KuksaConnector()
        kuksaconnector.connect
        # establishKuskaConne(ip,port)

    # function to open file dialog box
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select YAML File", "", "YAML Files (*.yml *.yaml)")
        if file_path:
            self.file_name_container.setText(file_path)
            self.signals = load_signals_from_yaml(file_path)
            self.signal_list_dropdown.clear() # clearing previous loaded signals
            self.signal_list_dropdown.addItems(self.signals.keys()) #adding all signals stored in signal array to dropdown list

 
    #function when an signal item is clicked:based on signal signal info 
    def on_signal_selected(self, signal_name):
        signal = self.signals.get(signal_name)
        if not signal:
            return
        
        # self.sav_temp_value()

        self.signal_info_name.setText(signal.name)
        self.signal_info_type.setText(signal.data_type)
 
        # Switch stacked widget page based on type
        type_map = {
            "empty":0,
            "bool": 1, "boolean": 1,
            "integer": 2, "int": 2, "uint8": 2,
            "enum": 3, "string": 3,
            "double": 4, "float": 4
        }
        index = type_map.get(signal.data_type, 0)
        self.stackedWidget.setCurrentIndex(index) #based on type particular input widget will be shown

        # logic to show the previous value in the input
        match index:
            case 1:
                self.signal_true_radio.setChecked(signal.temp_value is True)
                self.signal_false_radio.setChecked(signal.temp_value is False)
            case 2:
                self.signal_value_int.setValue(signal.temp_value or 0)
            case 3:
                self.signal_value_enum.clear()
                self.signal_value_enum.addItems(signal.allowed)
                if signal.temp_value:
                    idx = self.signal_value_enum.findText(signal.temp_value)
                    if idx >= 0:
                        self.signal_value_enum.setCurrentIndex(idx)
            case 4:
                self.signal_value_double.setValue(signal.temp_value or 0.0)

    #function to set the current(already present value) in the inpput 
    def set_temp_value_bool(self, value):
        if self.active_signal:
            self.active_signal.temp_value = value
    #function to set the current(already present value) in the inpput         
    def set_temp_value_int(self):
        if self.active_signal:
            self.active_signal.temp_value = self.signal_value_int.value()
    #function to set the current(already present value) in the inpput 
    def set_temp_value_enum(self):
        if self.active_signal:
            self.active_signal.temp_value = self.signal_value_enum.currentText()
    #function to set the current(already present value) in the inpput 
    def set_temp_value_double(self):
        if self.active_signal:
            self.active_signal.temp_value = self.signal_value_double.value()
    # to show the entered value when clicked on send button
    def commit_value(self):
        if self.active_signal:
            self.active_signal.current_value = self.active_signal.temp_value
            QMessageBox.information(self, "Signal Committed", f"{self.active_signal.name} set to {self.active_signal.current_value}")
