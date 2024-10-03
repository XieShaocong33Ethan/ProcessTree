from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QTextBrowser, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
import markdown

class MarkdownView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.text_edit = QTextEdit()
        self.preview = QTextBrowser()
        
        # 添加保存按钮
        self.save_button = QPushButton("保存")
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        
        layout.addWidget(self.text_edit)
        layout.addLayout(button_layout)
        layout.addWidget(self.preview)

    def set_controller(self, controller):
        self.controller = controller
        self.controller.node_content_changed.connect(self.update_content)
        self.text_edit.textChanged.connect(self.content_changed)
        self.save_button.clicked.connect(self.save_content)

    def update_content(self, content):
        self.text_edit.setPlainText(content)
        self.update_preview(content)

    def content_changed(self):
        content = self.text_edit.toPlainText()
        self.update_preview(content)

    def update_preview(self, content):
        html = markdown.markdown(content)
        self.preview.setHtml(html)

    def save_content(self):
        content = self.text_edit.toPlainText()
        self.controller.save_node_content(content)