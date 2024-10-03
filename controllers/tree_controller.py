from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QInputDialog, QMessageBox
from models.tree import DecisionTree
from models.node import Node
from models.database import Database
from views.edit_node_dialog import EditNodeDialog
from utils.file_manager import save_markdown, rename_markdown, delete_markdown, get_markdown_path, search_markdown_content

class TreeController(QObject):
    trees_changed = Signal(list)
    tree_changed = Signal(object)
    node_content_changed = Signal(str)
    content_saved = Signal()
    search_results = Signal(list)  # 新增信号

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.trees = self.db.load_trees()
        self.current_tree = None
        self.current_node = None

    def load_initial_data(self):
        self.trees_changed.emit(self.trees)
        if self.trees:
            self.select_tree(self.trees[0])

    def select_tree(self, tree):
        self.current_tree = tree
        self.current_node = None
        self.tree_changed.emit(tree)
        if tree and tree.root:
            self.node_selected(tree.root)

    def add_tree(self):
        name, ok = QInputDialog.getText(None, "添加决策树", "请输入决策树名称:")
        if ok and name:
            new_tree = DecisionTree(name)
            root_node = Node("Root", None, True)  # 根节点的 content_path 设为 None
            new_tree.root = root_node
            self.trees.append(new_tree)
            self.db.save_tree(new_tree)
            self.trees_changed.emit(self.trees)
            self.select_tree(new_tree)

    def remove_tree(self):
        if self.current_tree:
            self.db.delete_tree(self.current_tree.id)
            self.trees.remove(self.current_tree)
            self.current_tree = None
            self.current_node = None
            self.trees_changed.emit(self.trees)
            if self.trees:
                self.select_tree(self.trees[0])
            else:
                self.tree_changed.emit(None)
                self.node_content_changed.emit("")

    def rename_tree(self):
        if self.current_tree:
            old_name = self.current_tree.name
            name, ok = QInputDialog.getText(None, "重命名决策树", "请输入新名称:", text=old_name)
            if ok and name and name != old_name:
                self._rename_tree_files(old_name, name)
                self.current_tree.name = name
                self.db.save_tree(self.current_tree)
                self.trees_changed.emit(self.trees)

    def _rename_tree_files(self, old_name, new_name):
        for node in self._get_all_nodes(self.current_tree.root):
            rename_markdown(old_name, node.name, new_name, node.name)

    def _get_all_nodes(self, node):
        nodes = [node]
        for child in node.children:
            nodes.extend(self._get_all_nodes(child))
        return nodes

    def add_node(self):
        if not self.current_tree:
            return
        parent = self.current_node if self.current_node else self.current_tree.root
        name, ok = QInputDialog.getText(None, "添加节点", "请输入节点名称:")
        if ok and name:
            content_path = get_markdown_path(self.current_tree.name, name)
            new_node = self.current_tree.add_node(parent, name, content_path, True)
            save_markdown(self.current_tree.name, name, "")
            self.db.save_tree(self.current_tree)
            self.tree_changed.emit(self.current_tree)

    def remove_node(self):
        if not self.current_node or self.current_node == self.current_tree.root:
            QMessageBox.warning(None, "警告", "不能删除根节点！")
            return

        parent = self.current_node.parent()
        delete_markdown(self.current_tree.name, self.current_node.name)
        self.current_tree.remove_node(self.current_node)
        self.current_node = None
        self.db.save_tree(self.current_tree)
        self.tree_changed.emit(self.current_tree)
        if parent:
            self.node_selected(parent)
        else:
            self.node_content_changed.emit("")

    def edit_node(self):
        if self.current_node:
            old_name = self.current_node.name
            dialog = EditNodeDialog(self.current_node)
            if dialog.exec_():
                data = dialog.get_data()
                if data["name"] != old_name:
                    new_content_path = rename_markdown(self.current_tree.name, old_name, self.current_tree.name, data["name"])
                    self.current_node.content = new_content_path  # 更新节点的 content 属性
                self.current_tree.update_node(self.current_node, name=data["name"], enabled=data["enabled"])
                self.db.save_tree(self.current_tree)
                self.tree_changed.emit(self.current_tree)

    def node_selected(self, node):
        self.current_node = node
        if self.current_node and self.current_node.content:
            try:
                with open(self.current_node.content, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.node_content_changed.emit(content)
            except FileNotFoundError:
                QMessageBox.warning(None, "文件未找到", f"无法找到文件: {self.current_node.content}")
                self.node_content_changed.emit("")
        else:
            self.node_content_changed.emit("")

    def update_node_content(self, content):
        if self.current_node:
            self.current_node.content = content
            self.db.save_tree(self.current_tree)

    def save_node_content(self, content):
        if self.current_node and self.current_node.content:
            path = save_markdown(self.current_tree.name, self.current_node.name, content)
            self.current_node.content = path
            self.db.save_tree(self.current_tree)
            self.content_saved.emit()
            QMessageBox.information(None, "保存成功", f"节点内容已保存到 {path}")
        elif self.current_node and self.current_node == self.current_tree.root:
            QMessageBox.information(None, "保存成功", "根节点内容已更新（不保存为文件）")
        else:
            QMessageBox.warning(None, "保存失败", "没有选中的节点或节点没有关联的文件路径。")

    def close(self):
        self.db.close()

    def global_search(self, query):
        results = []
        for tree in self.trees:
            if query.lower() in tree.name.lower():
                results.append((tree, None))
            for node in self._search_nodes(tree.root, query):
                results.append((tree, node))
        
        # 搜索 Markdown 文件内容
        markdown_results = search_markdown_content(query)
        for tree_name, node_name in markdown_results:
            tree = next((t for t in self.trees if t.name == tree_name), None)
            if tree:
                node = self._find_node_by_name(tree.root, node_name)
                if node:
                    results.append((tree, node))
        
        self.search_results.emit(results)

    def _search_nodes(self, node, query):
        if query.lower() in node.name.lower():
            yield node
        for child in node.children:
            yield from self._search_nodes(child, query)

    def _find_node_by_name(self, node, name):
        if node.name == name:
            return node
        for child in node.children:
            result = self._find_node_by_name(child, name)
            if result:
                return result
        return None