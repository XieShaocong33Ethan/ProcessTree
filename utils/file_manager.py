import os
import shutil

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_markdown(tree_name, node_name, content):
    directory = sanitize_filename(tree_name)
    filename = sanitize_filename(node_name) + ".md"
    path = os.path.join(directory, filename)
    ensure_dir(directory)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
    return path

def rename_markdown(old_tree_name, old_node_name, new_tree_name, new_node_name):
    old_directory = sanitize_filename(old_tree_name)
    old_filename = sanitize_filename(old_node_name) + ".md"
    old_path = os.path.join(old_directory, old_filename)

    new_directory = sanitize_filename(new_tree_name)
    new_filename = sanitize_filename(new_node_name) + ".md"
    new_path = os.path.join(new_directory, new_filename)

    ensure_dir(new_directory)
    if os.path.exists(old_path):
        shutil.move(old_path, new_path)
    
    return new_path  # 返回新的文件路径

def delete_markdown(tree_name, node_name):
    directory = sanitize_filename(tree_name)
    filename = sanitize_filename(node_name) + ".md"
    path = os.path.join(directory, filename)
    if os.path.exists(path):
        os.remove(path)

def sanitize_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ']).rstrip()

def get_markdown_path(tree_name, node_name):
    directory = sanitize_filename(tree_name)
    filename = sanitize_filename(node_name) + ".md"
    return os.path.join(directory, filename)

def search_markdown_content(query):
    results = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            tree_name = os.path.basename(root)
                            node_name = os.path.splitext(file)[0]
                            results.append((tree_name, node_name))
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
    return results