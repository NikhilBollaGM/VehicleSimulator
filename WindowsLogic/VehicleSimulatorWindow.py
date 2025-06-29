import sys
import logging

from .connectionDialog import ConnectionDialog
from DataBrokerHandler import * 
# from DataBrokerHandler import (check_kuksa_connection, establishKuskaConnection)
from PyQt5.QtWidgets import (
    QDialog, QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QRadioButton,
    QTextEdit, QStackedWidget, QSpinBox, QDoubleSpinBox, QGroupBox, QGridLayout
)
from PyQt5 import uic
from enum import Enum


logging.basicConfig(
filename='app.log',
level=logging.INFO,
format= '%(asctime)s - %(levelname)s - %(message)s'

)


 
 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/mainWindow.ui",self)

        self.connection_dialog = None

        self.active_signal = None

        self.loading_yaml = False
        self.kuksaConnectorObj = KuksaConnector()

        self.signals= {} 
        self.initialising = True
        self.signal_list_dropdown.addItem("")
        # self.actionBrowse_file.triggered.connect(self.open_file_dialog) 
        self.signal_list_dropdown.lineEdit().textEdited.connect(self.search_signal)
        self.signal_list_dropdown.currentTextChanged.connect(self.on_signal_selected) #when clicked on any item in dropdown
        self.actionEstablish_connection_2.triggered.connect(self.showConnectionDialog)
        # self.signal_true_radio.clicked.connect(lambda: self.set_temp_value_bool(True))
        # self.signal_false_radio.clicked.connect(lambda: self.set_temp_value_bool(False))
        self.send_signal_button.clicked.connect(self.commit_value)

    def log_message(self,message: str):
        self.log_output_area.append(message)

    #function to show connection dialog box
    def showConnectionDialog(self):
        if not self.connection_dialog:
            self.connection_dialog = ConnectionDialog()
            # dialog = uic.loadUi()
            self.connection_dialog.databroker_connect_button.clicked.connect(lambda: self.onEstablishConnection(self.connection_dialog)) #lambda 

        print("action clicked")
        self.connection_dialog.exec_()

    # when clickedon connect button   
    def onEstablishConnection(self, dialog):
        port=dialog.port_input.text()
        print(port)
        ip=dialog.ip_address_input.text()
        print(ip)

        # Connecting to kuksa
        establishKuskaConnection(ip,port)
        
        if(self.kuksaConnectorObj.connected):
            logging.info("Connection Established")
            dialog.set_values(ip,port)

        # fetching all the signals and storing it in signal objects
        signal_objects = self.kuksaConnectorObj.get_all_signal_objects()

        self.signals = {s.name: s for s in signal_objects}
        self.all_signals = list(self.signals.keys())

        self.signal_list_dropdown.clear()
        self.signal_list_dropdown.addItems(self.all_signals)
        self.signal_list_dropdown.setCurrentIndex(-1)
        self.signal_list_dropdown.lineEdit().clear()
 
    #function when an signal item is clicked:based on signal signal info 
    def on_signal_selected(self, signal_name):
        if(self.signal_list_dropdown.currentIndex() > -1):
            signal = self.signals.get(signal_name)
            self.active_signal = signal
            self.active_signal.value = self.kuksaConnectorObj.get_vss_signal(self.active_signal.name)
            
            # print(self.active_signal.name)
            if not signal:
                return
            
            # self.sav_temp_value()

            self.signal_name_value_container.setText(signal.name)
            self.description_value_container.setText(signal.description or "")
            self.signal_type_value_container.setText(signal.entry_type)
            self.datatype_value_container.setText(signal.data_type)
            self.unit_value_container.setText(signal.unit or "")
            
    
            # Switch stacked widget page based on type
            type_map = {
                "empty":0,
                "BOOL": 1, "BOOLEAN": 1,
                "INTEGER": 2, "INT": 2, "INT8" "UINT8": 2, "UINT16": 2, "UINT32": 2,
                "ENUM": 3, "STRING": 3,
                "DOUBLE": 4, "FLOAT": 4
            }
            index = type_map.get(signal.data_type, 0)

            self.stackedWidget.setCurrentIndex(index) #based on type particular input widget will be shown


            # logic to show the previous value in the input
            match index:
                case 1:
                    self.signal_true_radio.setChecked(signal.value is True)
                    self.signal_false_radio.setChecked(signal.value is False)
                case 2:
                    self.signal_value_int.setValue(signal.value or 0)
                case 3:
                    self.signal_value_enum.clear()
                    # self.signal_value_enum.addItems(signal.allowed)
                    # if signal.temp_value:
                    #     idx = self.signal_value_enum.findText(signal.temp_value)
                        # if idx >= 0:
                            # self.signal_value_enum.setCurrentIndex(idx)
                case 4:
                    self.signal_value_double.setValue(signal.value or 0.0)

    
    # def set_temp_value_bool(self, value):
    #     if self.active_signal:
    #         self.active_signal.value = value

    
    # def set_temp_value_int(self):
    #     if self.active_signal:
    #         value = self.signal_value_int.value()
    #         self.active_signal.value = value

    # def set_temp_value_double(self):
    #     if self.active_signal:
    #         value = self.signal_value_double.value()
    #         self.active_signal.value = value

    # def set_temp_value_enum(self):
    #     if self.active_signal:
    #         value = self.signal_value_enum.currentText()
    #         self.active_signal.value = value

    def commit_value(self):
        if not self.active_signal:
            self.log_message("No Signal Please select a signal before sending.")
            QMessageBox.warning(self, "No Signal", "Please select a signal before sending.")
            return

        signal = self.active_signal
        index = self.stackedWidget.currentIndex()

        try:
            if index == 1:  # BOOL
                # If neither radio is selected, warn the user
                if not self.signal_true_radio.isChecked() and not self.signal_false_radio.isChecked():
                    QMessageBox.warning(self, "Missing Input", "Please select either True or False.")
                    return
                # If True radio is selected → True, else → False
                value = self.signal_true_radio.isChecked()

            elif index == 2:  # INTEGER
                value = self.signal_value_int.value()

            elif index == 3:  # ENUM / STRING
                value = self.signal_value_enum.currentText()
                if not value.strip():
                    QMessageBox.warning(self, "Missing Input", "Please select or enter a valid enum value.")
                    return

            elif index == 4:  # DOUBLE
                value = self.signal_value_double.value()

            else:  # No valid signal input page
                QMessageBox.warning(self, "Invalid Input", "No valid input widget found.")
                return

            # Attempt to send value to data broker
            success = self.kuksaConnectorObj.set_vss_signal(signal.name, value)

            if success:
                # signal.value = value
                self.log_message(f"Signal Sent {signal.name} set to {value}")
                QMessageBox.information(self, "Signal Sent", f"{signal.name} set to {value}")
            else:
                QMessageBox.critical(self, "Send Failed", f"Failed to send value for {signal.name}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")


  
   

    # function to search a signal i dropdown
    # def search_signal(self, text):
    #     # Skip search if we're already searching or loading YAML (to prevent recursion)
    #     if getattr(self, 'searching', False) or getattr(self, 'loading_yaml', False):
    #         return

    #     self.searching = True

    #     line_edit = self.signal_list_dropdown.lineEdit()
    #     cursor_position = line_edit.cursorPosition()

    #     self.signal_list_dropdown.blockSignals(True)
    #     self.signal_list_dropdown.clear()

    #     if text.strip() == "":
    #         filtered = self.all_signals
    #     else:
    #         filtered = [s for s in self.all_signals if text.lower() in s.lower()]

    #     if not filtered:
    #         self.signal_list_dropdown.addItem("No match")
    #         item = self.signal_list_dropdown.model().item(0)
    #         item.setEnabled(False)
    #     else:
    #         self.signal_list_dropdown.addItems(filtered)

    #     # Reset the text and cursor position so user can continue typing smoothly
    #     line_edit.setText(text)
    #     line_edit.setCursorPosition(cursor_position)

    #     self.signal_list_dropdown.blockSignals(False)
    #     self.signal_list_dropdown.showPopup()

    #     self.searching = False
    
    def search_signal(self, text):
        if not hasattr(self, "all_signals") or not self.all_signals:
            return

        # Preserve cursor and focus
        line_edit = self.signal_list_dropdown.lineEdit()
        cursor_position = line_edit.cursorPosition()
        had_focus = line_edit.hasFocus()

        self.signal_list_dropdown.blockSignals(True)

        # Temporarily block signals so we don’t fire currentTextChanged etc.
        current_text = line_edit.text()

        # Save match results
        if text.strip():
            filtered = [s for s in self.all_signals if text.lower() in s.lower()]
        else:
            filtered = self.all_signals

        # Clear and repopulate dropdown
        self.signal_list_dropdown.clear()

        if not filtered:
            self.signal_list_dropdown.addItem("No match")
            item = self.signal_list_dropdown.model().item(0)
            item.setEnabled(False)
        else:
            self.signal_list_dropdown.addItems(filtered)

        # Restore user-typed text and cursor
        line_edit.setText(current_text)
        line_edit.setCursorPosition(cursor_position)

        # Restore focus if lost
        if had_focus:
            line_edit.setFocus()

        self.signal_list_dropdown.blockSignals(False)

        self.signal_list_dropdown.showPopup()





    


