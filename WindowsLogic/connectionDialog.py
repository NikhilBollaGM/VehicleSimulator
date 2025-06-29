from PyQt5.QtWidgets import QDialog
from PyQt5 import uic

class ConnectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/connectionDialogBox.ui", self)

    def get_values(self):
        return self.ip_address_input.text(), self.port_input.text()
    
    def set_values(self, ip, port):
        self.ip_address_input.setText(ip)
        self.port_input.setText(port)
