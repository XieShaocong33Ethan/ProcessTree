from PySide6.QtCore import QObject, Signal, Property
from .node import Node

class DecisionTree(QObject):
    nameChanged = Signal(str)
    rootChanged = Signal(Node)

    def __init__(self, name="New Tree", parent=None):
        super().__init__(parent)
        self._name = name
        self._root = None
        self.id = None

    @Property(str, notify=nameChanged)
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._name != value:
            self._name = value
            self.nameChanged.emit(value)

    @Property(Node, notify=rootChanged)
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        if self._root != value:
            self._root = value
            self.rootChanged.emit(value)

    def add_node(self, parent, name, content="", enabled=True):
        new_node = Node(name, content, enabled, parent)
        if parent is None:
            self.root = new_node
        else:
            parent.add_child(new_node)
        return new_node

    def remove_node(self, node):
        if node == self.root:
            self.root = None
        else:
            parent = node.parent()
            if parent:
                parent.remove_child(node)

    def update_node(self, node, name=None, content=None, enabled=None):
        if name is not None:
            node.name = name
        if content is not None:
            node.content = content
        if enabled is not None:
            node.enabled = enabled