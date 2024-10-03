import sqlite3
import os
from .tree import DecisionTree
from .node import Node
from utils.file_manager import get_markdown_path  # 添加这行导入

class Database:
    def __init__(self, db_name="decision_trees.db"):
        db_exists = os.path.exists(db_name)
        self.conn = sqlite3.connect(db_name)
        if not db_exists:
            self.create_tables()
        else:
            self.update_tables()
        self.current_tree_name = None  # 添加这行

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trees (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY,
                tree_id INTEGER,
                name TEXT,
                content_path TEXT,
                enabled INTEGER,
                parent_id INTEGER,
                FOREIGN KEY (tree_id) REFERENCES trees (id)
            )
        ''')
        self.conn.commit()

    def update_tables(self):
        cursor = self.conn.cursor()
        # Check if content_path column exists
        cursor.execute("PRAGMA table_info(nodes)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'content_path' not in columns:
            cursor.execute('ALTER TABLE nodes ADD COLUMN content_path TEXT')
        self.conn.commit()

    def save_tree(self, tree):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO trees (id, name) VALUES (?, ?)', (tree.id, tree.name))
        tree_id = cursor.lastrowid if tree.id is None else tree.id
        tree.id = tree_id  # 确保树对象有正确的 ID
        self._clear_nodes(tree_id)
        if tree.root:
            self._save_node(tree.root, tree_id, None)
        self.conn.commit()

    def _clear_nodes(self, tree_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM nodes WHERE tree_id = ?', (tree_id,))

    def _save_node(self, node, tree_id, parent_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO nodes (tree_id, name, content_path, enabled, parent_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (tree_id, node.name, node.content, int(node.enabled), parent_id))
        node_id = cursor.lastrowid
        node.id = node_id  # 确保节点对象有正确的 ID
        for child in node.children:
            self._save_node(child, tree_id, node_id)

    def load_trees(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM trees")
        trees = []
        for tree_id, name in cursor.fetchall():
            tree = DecisionTree(name)
            tree.id = tree_id
            self.current_tree_name = name  # 设置当前树名
            root_node = self._load_tree_nodes(tree_id)
            if root_node:
                tree.root = root_node
            trees.append(tree)
        self.current_tree_name = None  # 重置当前树名
        return trees

    def _load_tree_nodes(self, tree_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, content_path, enabled, parent_id FROM nodes WHERE tree_id = ? AND parent_id IS NULL", (tree_id,))
        root_data = cursor.fetchone()
        if root_data:
            root_node = self._create_node(root_data)
            self._load_children(root_node, tree_id)
            return root_node
        return None

    def _load_children(self, parent_node, tree_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, content_path, enabled, parent_id FROM nodes WHERE tree_id = ? AND parent_id = ?", (tree_id, parent_node.id))
        children_data = cursor.fetchall()
        for child_data in children_data:
            child_node = self._create_node(child_data)
            parent_node.add_child(child_node)
            self._load_children(child_node, tree_id)

    def _create_node(self, node_data):
        id, name, content_path, enabled, parent_id = node_data
        if parent_id is None:  # 这是根节点
            content_path = None
        elif content_path is None and self.current_tree_name:
            content_path = get_markdown_path(self.current_tree_name, name)
        node = Node(name, content_path, bool(enabled))
        node.id = id
        return node

    def delete_tree(self, tree_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM nodes WHERE tree_id = ?", (tree_id,))
        cursor.execute("DELETE FROM trees WHERE id = ?", (tree_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()