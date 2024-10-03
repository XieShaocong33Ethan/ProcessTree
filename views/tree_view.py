from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QPushButton, QGridLayout, QComboBox
from PySide6.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PySide6.QtCore import Qt

class TreeView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # 添加决策树选择下拉框
        self.tree_selector = QComboBox()
        layout.addWidget(self.tree_selector)

        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)

        layout.addWidget(self.tree_view)

        # 使用网格布局来组织按钮
        button_layout = QGridLayout()
        self.add_tree_button = self.create_button("添加决策树")
        self.remove_tree_button = self.create_button("删除决策树")
        self.rename_tree_button = self.create_button("重命名决策树")
        self.add_node_button = self.create_button("添加节点")
        self.remove_node_button = self.create_button("删除节点")
        self.edit_node_button = self.create_button("编辑节点")

        button_layout.addWidget(self.add_tree_button, 0, 0)
        button_layout.addWidget(self.remove_tree_button, 0, 1)
        button_layout.addWidget(self.rename_tree_button, 1, 0)
        button_layout.addWidget(self.add_node_button, 1, 1)
        button_layout.addWidget(self.remove_node_button, 2, 0)
        button_layout.addWidget(self.edit_node_button, 2, 1)

        layout.addLayout(button_layout)

    def create_button(self, text):
        button = QPushButton(text)
        button.setMinimumHeight(40)  # 设置按钮最小高度
        return button

    def set_controller(self, controller):
        self.controller = controller
        self.controller.trees_changed.connect(self.update_tree_selector)
        self.controller.tree_changed.connect(self.update_tree)
        self.tree_selector.currentIndexChanged.connect(self.on_tree_selected)
        self.add_tree_button.clicked.connect(self.controller.add_tree)
        self.remove_tree_button.clicked.connect(self.controller.remove_tree)
        self.rename_tree_button.clicked.connect(self.controller.rename_tree)
        self.add_node_button.clicked.connect(self.controller.add_node)
        self.remove_node_button.clicked.connect(self.controller.remove_node)
        self.edit_node_button.clicked.connect(self.controller.edit_node)
        self.tree_view.clicked.connect(self.on_item_clicked)

    def update_tree_selector(self, trees):
        self.tree_selector.clear()
        for tree in trees:
            self.tree_selector.addItem(tree.name, tree)

    def on_tree_selected(self, index):
        if index >= 0:
            selected_tree = self.tree_selector.itemData(index)
            self.controller.select_tree(selected_tree)

    def on_item_clicked(self, index):
        item = self.model.itemFromIndex(index)
        node = item.data(Qt.UserRole)
        self.controller.node_selected(node)

    def update_tree(self, tree):
        self.model.clear()
        if tree and tree.root:
            self._add_node(self.model.invisibleRootItem(), tree.root)

    def _add_node(self, parent_item, node):
        item = QStandardItem(node.name)
        item.setData(node, Qt.UserRole)
        if not node.enabled:
            item.setForeground(QBrush(QColor(80, 80, 80)))  # 深灰色文字
            item.setBackground(QBrush(QColor(200, 200, 200)))  # 浅灰色背景
        parent_item.appendRow(item)
        for child in node.children:
            self._add_node(item, child)

    def highlight_node(self, node):
        if node:
            self._highlight_node_recursive(self.model.invisibleRootItem(), node)

    def _highlight_node_recursive(self, parent_item, target_node):
        for row in range(parent_item.rowCount()):
            item = parent_item.child(row)
            node = item.data(Qt.UserRole)
            if node == target_node:
                item.setBackground(QBrush(QColor(255, 255, 0, 100)))  # 淡黄色背景
                self.tree_view.scrollTo(item.index())
                return True
            if self._highlight_node_recursive(item, target_node):
                return True
        return False