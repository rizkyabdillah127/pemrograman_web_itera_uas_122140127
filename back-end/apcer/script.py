import os

def extract_text_to_markdown(base_dir, output_file="context.md"):
    """
    Mengekstrak semua konten teks dari file-file dalam direktori tertentu
    dan menulisnya ke dalam file Markdown.

    Args:
        base_dir (str): Direktori dasar tempat pencarian file dimulai.
        output_file (str): Nama file Markdown tempat konten akan ditulis.
    """
    output_path = os.path.join(base_dir, output_file) 
    
    target_directories = [
        os.path.join(base_dir, "apcer", "alembic"),
        os.path.join(base_dir, "apcer", "models"),
        os.path.join(base_dir, "apcer", "scripts"),
        os.path.join(base_dir, "apcer", "views"),
        os.path.join(base_dir, "apcer")
    ]

    apcer_root = os.path.join(base_dir, "apcer")
    if not os.path.isdir(apcer_root):
        print(f"Error: Direktori '{apcer_root}' tidak ditemukan.")
        return

    print(f"Memulai ekstraksi teks ke '{output_path}'...")

    with open(output_path, 'w', encoding='utf-8') as outfile:
        for target_dir in target_directories:
            if not os.path.isdir(target_dir):
                print(f"Peringatan: Direktori '{target_dir}' tidak ditemukan, dilewati.")
                continue

            print(f"Memproses direktori: {target_dir}")
            
            for root, _, files in os.walk(target_dir):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            
                            outfile.write(f"## File: `{os.path.relpath(file_path, base_dir)}`\n\n")
                            outfile.write("```\n")
                            outfile.write(content)
                            outfile.write("\n```\n\n")
                            print(f"  - Diekstrak: {os.path.relpath(file_path, base_dir)}")
                    except UnicodeDecodeError:
                        print(f"  - Melewatkan file non-teks atau bermasalah encoding: {os.path.relpath(file_path, base_dir)}")
                    except Exception as e:
                        print(f"  - Terjadi kesalahan saat membaca file {os.path.relpath(file_path, base_dir)}: {e}")
        
        print(f"Memproses file-file langsung di direktori: {apcer_root}")
        for item in os.listdir(apcer_root):
            item_path = os.path.join(apcer_root, item)
            if os.path.isfile(item_path) and not item.startswith('.'):
                if any(target_dir in item_path for target_dir in target_directories[:-1]):
                    continue
                try:
                    with open(item_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(f"## File: `{os.path.relpath(item_path, base_dir)}`\n\n")
                        outfile.write("```\n")
                        outfile.write(content)
                        outfile.write("\n```\n\n")
                        print(f"  - Diekstrak: {os.path.relpath(item_path, base_dir)}")
                except UnicodeDecodeError:
                    print(f"  - Melewatkan file non-teks atau bermasalah encoding: {os.path.relpath(item_path, base_dir)}")
                except Exception as e:
                    print(f"  - Terjadi kesalahan saat membaca file {os.path.relpath(item_path, base_dir)}: {e}")


    print(f"Ekstraksi selesai. Konten disimpan di '{output_path}'.")

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    extract_text_to_markdown(current_directory, "context.md")