from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal, Qt  # 添加 Qt 的导入

class SearchResultsView(QWidget):
    item_selected = Signal(object, object)  # (tree, node)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        self.list_widget.itemClicked.connect(self.on_item_clicked)

    def update_results(self, results):
        self.list_widget.clear()
        for tree, node in results:
            if node:
                item = QListWidgetItem(f"{tree.name} > {node.name}")
            else:
                item = QListWidgetItem(f"{tree.name}")
            item.setData(Qt.UserRole, (tree, node))
            self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        tree, node = item.data(Qt.UserRole)
        self.item_selected.emit(tree, node)