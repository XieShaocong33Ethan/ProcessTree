from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont

class TreeGraphView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

    def update_graph(self, tree):
        self.scene.clear()
        if tree and tree.root:
            self._draw_node(tree.root, 0, 0, 150)  # 减小初始宽度
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def _draw_node(self, node, x, y, width):
        radius = 12  # 进一步减小节点半径
        rect = QRectF(x - radius, y - radius, 2 * radius, 2 * radius)
        
        ellipse = QGraphicsEllipseItem(rect)
        color = QColor(80, 80, 80) if not node.enabled else Qt.white  # 使用深灰色表示禁用状态
        ellipse.setBrush(QBrush(color))
        ellipse.setPen(QPen(Qt.black))
        ellipse.setData(Qt.UserRole, node)  # 存储节点数据
        self.scene.addItem(ellipse)

        # 在节点内显示名字，颜色根据启用状态改变
        text = QGraphicsTextItem(node.name)
        font = QFont()
        font.setPointSize(5)  # 进一步减小字体大小
        text.setFont(font)
        text.setDefaultTextColor(Qt.black if node.enabled else Qt.white)  # 根据启用状态改变文字颜色
        text_width = text.boundingRect().width()
        text_height = text.boundingRect().height()
        text.setPos(x - text_width / 2, y - text_height / 2)
        self.scene.addItem(text)

        if node.children:
            child_width = width / len(node.children)
            for i, child in enumerate(node.children):
                child_x = x - width / 2 + child_width * (i + 0.5)
                child_y = y + 40  # 进一步减小垂直间距
                line = QGraphicsLineItem(x, y + radius, child_x, child_y - radius)
                line_color = Qt.gray if not node.enabled or not child.enabled else Qt.black
                line.setPen(QPen(line_color))
                self.scene.addItem(line)
                self._draw_node(child, child_x, child_y, child_width)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        # 添加缩放功能
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.scale(1.1, 1.1)
            else:
                self.scale(0.9, 0.9)
        else:
            super().wheelEvent(event)

    def highlight_node(self, target_node):
        for item in self.scene.items():
            if isinstance(item, QGraphicsEllipseItem):
                node = item.data(Qt.UserRole)
                if node == target_node:
                    item.setBrush(QBrush(QColor(255, 255, 0, 100)))  # 淡黄色背景
                    self.centerOn(item)
                    return