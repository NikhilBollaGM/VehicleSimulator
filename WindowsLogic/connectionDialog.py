import sys
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import os

class ConnectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        def resource_path(relative_path):
            base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
            return os.path.join(base_path, relative_path)
        
        ui_path = resource_path("UI/connectionDialogBox.ui")
        uic.loadUi(ui_path, self)

    def get_values(self):
        return self.ip_address_input.text(), self.port_input.text()
    
    def set_values(self, ip, port):
        self.ip_address_input.setText(ip)
        self.port_input.setText(port)
