from PySide6.QtCore import QObject, Signal, Property

class Node(QObject):
    nameChanged = Signal(str)
    contentChanged = Signal(str)
    enabledChanged = Signal(bool)

    def __init__(self, name, content="", enabled=True, parent=None):
        super().__init__(parent)
        self._name = name
        self._content = content
        self._enabled = enabled
        self._children = []

    @Property(str, notify=nameChanged)
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._name != value:
            self._name = value
            self.nameChanged.emit(value)

    @Property(str, notify=contentChanged)
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if self._content != value:
            self._content = value
            self.contentChanged.emit(value)

    @Property(bool, notify=enabledChanged)
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    def add_child(self, child):
        self._children.append(child)
        child.setParent(self)

    def remove_child(self, child):
        self._children.remove(child)
        child.setParent(None)

    @property
    def children(self):
        return self._children

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value