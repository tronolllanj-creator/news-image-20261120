import os
import shutil
import sys

def main():
    # 1. Locate source entry.png (in the repository/script directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(script_dir, "entry.png")
    
    if not os.path.exists(src_path):
        print(f"Error: source file not found at {src_path}", file=sys.stderr)
        sys.exit(1)

    # 2. Determine destination directory
    dest_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, "entry.png")
    
    # 3. Copy the file
    try:
        shutil.copy2(src_path, dest_path)
    except OSError as e:
        print(f"Error: failed to copy file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 4. Verify PNG magic bytes
    png_magic = b'\x89PNG\r\n\x1a\n'
    try:
        with open(dest_path, 'rb') as f:
            header = f.read(8)
    except OSError as e:
        print(f"Error: failed to read destination file: {e}", file=sys.stderr)
        sys.exit(1)
        
    if header != png_magic:
        print(f"Error: File {dest_path} does not start with valid PNG magic bytes.", file=sys.stderr)
        sys.exit(1)

    # 5. Compute size and print output
    size = os.path.getsize(dest_path)
    print(f"Output path: {dest_path}")
    print(f"File size: {size} bytes")

if __name__ == "__main__":
    main()
