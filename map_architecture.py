import os

# Folders and files to ignore to keep the map clean
IGNORE_DIRS = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', '.pytest_cache'}
IGNORE_EXTS = {'.pyc', '.pyo', '.pyd', '.sqlite3', '.db'}

def generate_tree(dir_path, prefix=''):
    tree_str = ''
    try:
        items = sorted(os.listdir(dir_path))
    except PermissionError:
        return ''

    # Filter out ignored items
    items = [i for i in items if i not in IGNORE_DIRS and not any(i.endswith(ext) for ext in IGNORE_EXTS)]

    for i, item in enumerate(items):
        path = os.path.join(dir_path, item)
        is_last = (i == len(items) - 1)
        connector = '└── ' if is_last else '├── '
        
        tree_str += f"{prefix}{connector}{item}\n"
        
        if os.path.isdir(path):
            extension = '    ' if is_last else '│   '
            tree_str += generate_tree(path, prefix + extension)
            
    return tree_str

if __name__ == '__main__':
    root_dir = os.getcwd()
    output_file = 'architecture_map.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"ChainPulse Architecture (Root: {root_dir})\n")
        f.write("="*50 + "\n")
        f.write(".\n")
        f.write(generate_tree(root_dir))
        
    print(f"Architecture map successfully saved to {output_file}")
