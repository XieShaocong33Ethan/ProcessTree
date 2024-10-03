from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QPushButton, QLabel

class EditNodeDialog(QDialog):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self.setWindowTitle("编辑节点")
        
        layout = QVBoxLayout(self)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("名称:"))
        self.name_edit = QLineEdit(node.name)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        self.enabled_checkbox = QCheckBox("启用")
        self.enabled_checkbox.setChecked(node.enabled)
        layout.addWidget(self.enabled_checkbox)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def get_data(self):
        return {
            "name": self.name_edit.text(),
            "enabled": self.enabled_checkbox.isChecked()
        }