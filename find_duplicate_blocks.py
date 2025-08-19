import os

def find_block_in_files(directory, block_name):
    results = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if f'{{% block {block_name} %}}' in content:
                        count = content.count(f'{{% block {block_name} %}}')
                        results.append((filepath, count))
    
    return results

# Search in templates directory
template_dir = r'c:\Users\Acer\Desktop\patient\templates'
results = find_block_in_files(template_dir, 'page_title')

for filepath, count in results:
    if count > 1:
        print(f"File {filepath} contains {count} occurrences of block 'page_title'")
    else:
        print(f"File {filepath} contains 1 occurrence of block 'page_title'")