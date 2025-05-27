import os

SRC_DIR = "./src"
OUTPUT_FILE = "context.md"

def extract_js_files_to_md(src_dir, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".js"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            relative_path = os.path.relpath(file_path, src_dir)
                            outfile.write(f"\n\n---\n### File: {relative_path}\n\n")
                            outfile.write(content)
                    except Exception as e:
                        print(f"Failed to read {file_path}: {e}")

    print(f"Extraction completed. Contents saved to '{output_file}'.")

if __name__ == "__main__":
    extract_js_files_to_md(SRC_DIR, OUTPUT_FILE)
