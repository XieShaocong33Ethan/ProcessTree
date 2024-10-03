from PySide6.QtWidgets import (QMainWindow, QHBoxLayout, QWidget, QSplitter, 
                               QVBoxLayout, QLineEdit, QPushButton, QFrame, QToolBar, QApplication)
from PySide6.QtCore import Qt, QDir
from PySide6.QtGui import QFont, QFontDatabase
from .tree_view import TreeView
from .markdown_view import MarkdownView
from .tree_graph_view import TreeGraphView
from .search_results_view import SearchResultsView

class DatabaseSidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        
        self.tree_view = TreeView()
        layout.addWidget(self.tree_view)

        # 移除了 3x2 网格按钮

class SearchSidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        
        # 搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_button = QPushButton("搜索")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # 搜索结果视图
        self.search_results_view = SearchResultsView()
        layout.addWidget(self.search_results_view)

class MainWindow(QMainWindow):
    def __init__(self, font_path):
        super().__init__()
        self.setWindowTitle("决策树知识管理")
        self.setGeometry(100, 100, 1200, 800)

        # 加载自定义字体
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            custom_font = QFont(font_family, 9)
            QApplication.setFont(custom_font)
        else:
            print("Error: Failed to load custom font.")
            # 如果加载失败，使用系统默认字体
            custom_font = QFont("SimHei", 9)
            QApplication.setFont(custom_font)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # 创建左侧数据库边栏
        self.database_sidebar = DatabaseSidebar()
        self.database_sidebar.setMinimumWidth(250)  # 减小最小宽度
        self.database_sidebar.setMaximumWidth(350)  # 减小最大宽度
        self.database_sidebar.hide()  # 初始时隐藏侧边栏

        # 创建中央布局
        central_layout = QVBoxLayout()
        
        # 添加树形图视图
        self.tree_graph_view = TreeGraphView()
        central_layout.addWidget(self.tree_graph_view)

        # 创建中央 Markdown 视图
        self.markdown_view = MarkdownView()
        central_layout.addWidget(self.markdown_view)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        # 创建右侧搜索边栏
        self.search_sidebar = SearchSidebar()
        self.search_sidebar.setFixedWidth(250)  # 设置侧边栏宽度

        # 创建主分割器
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.database_sidebar)
        self.main_splitter.addWidget(central_widget)
        self.main_splitter.addWidget(self.search_sidebar)

        # 设置分割器的初始比例
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setStretchFactor(2, 0)

        main_layout.addWidget(self.main_splitter)

        # 创建工具栏
        self.create_toolbar()

    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)  # 使工具栏不可移动
        toolbar.setStyleSheet("""
            QToolBar {
                border: none;
                background: transparent;
            }
            QToolButton {
                background: transparent;
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #E0E0E0;
            }
        """)
        self.addToolBar(toolbar)

        # 添加切换数据库边栏的按钮到工具栏
        self.toggle_database_button = QPushButton("显示/隐藏数据库")
        self.toggle_database_button.clicked.connect(self.toggle_database_sidebar)
        toolbar.addWidget(self.toggle_database_button)
        
        # 添加切换搜索边栏的按钮到工具栏
        self.toggle_search_button = QPushButton("显示/隐藏搜索")
        self.toggle_search_button.clicked.connect(self.toggle_search_sidebar)
        toolbar.addWidget(self.toggle_search_button)

    def set_controller(self, controller):
        self.controller = controller
        self.database_sidebar.tree_view.set_controller(controller)
        self.markdown_view.set_controller(controller)
        controller.tree_changed.connect(self.tree_graph_view.update_graph)
        self.search_sidebar.search_button.clicked.connect(self.perform_search)
        controller.search_results.connect(self.show_search_results)
        self.search_sidebar.search_results_view.item_selected.connect(self.on_search_result_selected)
        # 加载初始数据
        controller.load_initial_data()

    def perform_search(self):
        query = self.search_sidebar.search_input.text()
        if query:
            self.controller.global_search(query)

    def show_search_results(self, results):
        self.search_sidebar.search_results_view.update_results(results)
        if self.search_sidebar.isHidden():
            self.toggle_search_sidebar()

    def on_search_result_selected(self, tree, node):
        self.controller.select_tree(tree)
        if node:
            self.controller.node_selected(node)
        self.database_sidebar.tree_view.highlight_node(node)
        self.tree_graph_view.highlight_node(node)

    def toggle_database_sidebar(self):
        if self.database_sidebar.isVisible():
            self.database_sidebar.hide()
        else:
            self.database_sidebar.show()

    def toggle_search_sidebar(self):
        if self.search_sidebar.isVisible():
            self.search_sidebar.hide()
        else:
            self.search_sidebar.show()