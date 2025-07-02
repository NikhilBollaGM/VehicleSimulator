import sys
import logging
import os

from .connectionDialog import ConnectionDialog
from DataBrokerHandler import * 
# from DataBrokerHandler import (check_kuksa_connection, establishKuskaConnection)
from PyQt5.QtWidgets import (
    QDialog, QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QRadioButton,
    QTextEdit, QStackedWidget, QSpinBox, QDoubleSpinBox, QGroupBox, QGridLayout
)
from PyQt5 import uic
from PyQt5.QtCore import Qt
from enum import Enum
from datetime import datetime


logging.basicConfig(
filename='app.log',
level=logging.INFO,
format= '%(asctime)s - %(levelname)s - %(message)s'

)

class LogLevel(Enum):
    SUCCESS = "green"
    FAILED = "red"
    INFO = "black"


 
 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        
        def resource_path(relative_path):
            # When running as .exe, sys._MEIPASS is the temp folder where PyInstaller unpacks files
            base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
            return os.path.join(base_path, relative_path)
        
        ui_path = resource_path("UI/mainWindow.ui")
        uic.loadUi(ui_path, self)

        # Disable maximize button
        self.setWindowFlags(Qt.Window |
                            Qt.WindowMinimizeButtonHint |
                            Qt.WindowCloseButtonHint)

        # Optional: Prevent resizing
        self.setFixedSize(self.size())


        self.connection_dialog = None
        self.active_signal = None
        self.loading_yaml = False
        self.kuksaConnectorObj = None
        self.signals= {} 
        self.initialising = True
        self.isDatabrokerConnected = False
        self.signal_value_int.setMinimum(-999999) 
        self.signal_value_int.setMaximum(999999) #need to handle in designer and dynamically based min and max
        self.signal_value_double.setMaximum(999999)#need to handle in designer and 

        self.stackedWidget.setCurrentIndex(0) #default input area


        # logs visibility toggle
        self.groupBox_4.setVisible(False)  #default log area disable visibility
        self.actionLogs.setChecked(False)  #logs checkbox default
        self.actionLogs.triggered.connect(self.toggle_log_visibility)

        #
        self.signal_min_max_slider.valueChanged.connect(self.on_value_change)

        #signal dropdown widgets
        self.signal_list_widget.hide()
        self.signal_search_input.textChanged.connect(self.filter_signal_list)
        self.signal_dropdown_button.clicked.connect(self.toggle_signal_list)
        self.signal_list_widget.itemClicked.connect(self.select_signal_from_list)


       
        self.actionEstablish_connection_2.triggered.connect(self.showConnectionDialog)
        self.send_signal_button.clicked.connect(self.commit_value)

    # function to log message in log arrea
    def log_message(self,message: str, level: LogLevel =LogLevel.INFO):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = level.value
        formatted_message = f'<span style="color:{color}">[{timestamp}] [{level.name}] {message}</span>'
        self.log_output_area.append(formatted_message)

    # function to toggle log visibility
    def toggle_log_visibility(self, checked):
        self.groupBox_4.setVisible(checked) 


    #function to show connection dialog box
    def showConnectionDialog(self):
        print("calling show connection dialog")
        
        if not self.connection_dialog:
            self.connection_dialog = ConnectionDialog()

        # Always disconnect previous connection
        try:
            self.connection_dialog.databroker_connect_button.clicked.disconnect()
        except TypeError:
            pass  # No connection to disconnect

        if not self.isDatabrokerConnected:
            print("calling on establish")
            self.connection_dialog.databroker_connect_button.clicked.connect(lambda: self.onEstablishConnection(self.connection_dialog))
            self.connection_dialog.databroker_connect_button.setText("Connect")
        else:
            print("calling on disconnect")
            self.connection_dialog.databroker_connect_button.clicked.connect(self.onDisconnect)
            self.connection_dialog.databroker_connect_button.setText("Disconnect")

        print("connect button clicked")
        self.connection_dialog.exec_()


    # when clicked on disconnect button
    def onDisconnect(self):
        print("Disconnecting")
        self.kuksaConnectorObj.disconnect()
        self.isDatabrokerConnected = False
        self.actionEstablish_connection_2.setText("Connect")
        self.signals = {}
        self.signal_list_widget.clear()

        if(self.connection_dialog):
            self.connection_dialog.accept()


        self.log_message("Disconnected from databroker.", LogLevel.INFO)

    # when clickedon connect button   
    def onEstablishConnection(self, dialog):
        port=dialog.port_input.text()
        print(port)
        ip=dialog.ip_address_input.text()
        print(ip)

        # Connecting to kuksa
        self.kuksaConnectorObj = establishKuksaConnection(ip,port)

        
        
        if(not self.kuksaConnectorObj == None ):
            if(self.kuksaConnectorObj.connected ):
                self.isDatabrokerConnected = True
                logging.info("Connection Established")
                self.log_message(f"Conected to IP:{ip}, PORT:{port}")
                dialog.set_values(ip,port)
                self.connection_dialog.databroker_connect_button.setText("Disconnect")
                self.actionEstablish_connection_2.setText("Disconnect")
                dialog.accept()
            
            # fetching all the signals and storing it in signal objects
            signal_objects = self.kuksaConnectorObj.get_all_signal_objects()
            
            self.signals = {s.name: s for s in signal_objects}
            self.all_signals = list(self.signals.keys())

            #adding al signals into signal list
            self.signal_list_widget.clear() 
            self.signal_list_widget.addItems(self.all_signals)
            self.signal_search_input.clear()
        


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
            elif index == 5: #min and max
                print("sliding")
                value = int(self.signal_value_min_max.text())
            elif index == 6: #string
                value = self.signal_value_string.text() 

            else:  # No valid signal input page
                QMessageBox.warning(self, "Invalid Input", "No valid input widget found.")
                return

            # Attempt to send value to data broker
            success = self.kuksaConnectorObj.set_vss_signal(signal.name, value)

            if success:
                # signal.value = value
                self.log_message(f"Signal Sent {signal.name} set to {value}", LogLevel.SUCCESS)
                # QMessageBox.information(self, "Signal Sent", f"{signal.name} set to {value}")
            else:
                self.log_message(f"Failed to send value for {signal.name}", LogLevel.FAILED)
                # QMessageBox.critical(self, "Send Failed", f"Failed to send value for {signal.name}")

        except Exception as e:
            self.log_message(f"An error occurred:\n{e}", LogLevel.FAILED)
            # QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")

    
    def toggle_signal_list(self):
        if self.signal_list_widget.isVisible():
            self.signal_list_widget.hide()
        else:
            self.signal_list_widget.show()


# signal search function
    def filter_signal_list(self, text):
        if not hasattr(self, "all_signals"):
            return
        
        self.signal_list_widget.clear()

        filtered = [s for s in self.all_signals if text.lower() in s.lower()] if text.strip() else self.all_signals

        if not filtered:
            self.signal_list_widget.addItem("No match")
            self.signal_list_widget.item(0).setFlags(Qt.NoItemFlags)
        else:
            self.signal_list_widget.addItems(filtered)

        self.signal_list_widget.show()

    def select_signal_from_list(self, item):
        signal_name = item.text()
        if signal_name == "No match":
            return

        self.signal_search_input.setText(signal_name) #setting signal name in input
        self.signal_list_widget.hide()  # hide dropdown
        
        if not signal_name.strip() or signal_name not in self.signals:
            print("empty signal")
            self.active_signal = None
            self.signal_name_value_container.setText("")
            self.description_value_container.setText("")
            self.signal_type_value_container.setText("")
            self.datatype_value_container.setText("")
            self.unit_value_container.setText("")
            self.stackedWidget.setCurrentIndex(0)
            return
        
        signal = self.signals.get(signal_name)
        print("on signal select")
        print(signal)
        self.active_signal = signal
        if(self.active_signal != None):
            self.active_signal.value = self.kuksaConnectorObj.get_vss_signal(self.active_signal.name)
        
        # print(self.active_signal.name)
        if not signal:
            return
        
        # setting current signal info
        self.signal_name_value_container.setText(signal.name)
        self.description_value_container.setText(signal.description or "")
        self.signal_type_value_container.setText(signal.entry_type)
        self.datatype_value_container.setText(signal.data_type)
        self.unit_value_container.setText(signal.unit or "")
        

        # Switch stacked widget page based on type
        type_map = {
            "empty":0,
            "BOOL": 1, "BOOLEAN": 1,
            "INTEGER": 2, "INT": 2, "INT32":2, "UINT8": 2, "INT8" "UINT8": 2, "UINT16": 2, "UINT32": 2,
            "ENUM": 3, "STRING": 3,
            "DOUBLE": 4, "FLOAT": 4
        }
        index = type_map.get(signal.data_type, 0)
        print(index)

        if(not signal.is_enum and index == 3):
            index = 6 #to display string input
        elif((signal.min_value != None) and (signal.max_value != None) ):
            index=5
            print(signal.min_value)
            print(signal.max_value)

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
                self.signal_value_enum.addItems(signal.allowed_values)
                if signal.value:
                     idx = self.signal_value_enum.findText(signal.value)
                     if idx >= 0:
                        self.signal_value_enum.setCurrentIndex(idx)
            case 4:
                self.signal_value_double.setValue(signal.value or 0.0)
            case 5:
                self.signal_min_max_slider.setMinimum(signal.min_value)
                self.signal_min_max_slider.setMaximum(signal.max_value)
                self.min_label.setText(f"{signal.min_value}")
                self.max_label.setText(f"{signal.max_value}")
                print("Need to slider") 
            case 6:
                self.signal_value_string.setText(signal.value)
                print("need to enter string") 



# slider setting and showing
    def set_slider_range(self,min_value,max_value):
        try:
            min_text = self.min_label.text()
            max_text = self.max_label.text()

            is_float = '.' in min_text or '.' in max_text

            if is_float:
                min_val = float(min_text)
                max_val = float(max_text)
                self.multiplier = 100  # for 2 decimal precision
                self.float_mode = True
            else:
                min_val = int(min_text)
                max_val = int(max_text)
                self.multiplier = 1
                self.float_mode = False

            if min_val >= max_val:
                self.value_label.setText("Error: Min must be < Max")
                return

            self.true_min = min_val

            self.slider.setMinimum(int(min_val * self.multiplier))
            self.slider.setMaximum(int(max_val * self.multiplier))
            self.slider.setValue(int(min_val * self.multiplier))

        except ValueError:
            self.value_label.setText("Invalid input")

    def on_value_change(self, value):
        # if self.float_mode:
        #     val = value / self.multiplier
        #     self.value_label.setText(f"Value: {val:.2f}")
        # else:
        self.signal_value_min_max.setText(f"{value}")
# 
  
