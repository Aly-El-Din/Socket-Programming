import os
import random
import string

def generate_text_file(filename, size_kb):
    """Generates a text file with random content."""
    content = ''.join(random.choices(string.ascii_letters + string.digits, k=1024))  # 1 KB chunk
    with open(filename, 'w') as f:
        for _ in range(size_kb):
            f.write(content)

def create_test_files(num_files=10, min_size_kb=1, max_size_kb=100):
    """Creates a specified number of text files with random sizes."""
    if not os.path.exists("test_files"):
        os.makedirs("test_files")

    for i in range(1, num_files + 1):
        size_kb = random.randint(min_size_kb, max_size_kb)
        filename = f"test_files/file_{i}_{size_kb}KB.txt"
        generate_text_file(filename, size_kb)
        print(f"Generated {filename} with size {size_kb} KB")

# Generate 10 test files with sizes ranging from 1 KB to 100 KB
create_test_files(num_files=10, min_size_kb=1, max_size_kb=100)
