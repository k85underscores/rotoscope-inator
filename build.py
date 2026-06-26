import os
import zipfile
import subprocess

DIST_DIR = "dist"
SOURCE_DIR = os.path.join(DIST_DIR, "rotoscope-inator")
OUTPUT_ZIP = os.path.join(DIST_DIR, "rotoscope-inator-win64.zip")


def zip_directory(source_dir, output_zip):
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                archive_name = os.path.relpath(
                    file_path,
                    os.path.dirname(source_dir)
                )

                zipf.write(file_path, archive_name)


if __name__ == "__main__":
    subprocess.run(["pyinstaller", "rotoscope-inator.spec", "-y"])

    if not os.path.isdir(SOURCE_DIR):
        raise FileNotFoundError(f"Directory not found: {SOURCE_DIR}")

    print("Zipping...")
    zip_directory(SOURCE_DIR, OUTPUT_ZIP)
    print(f"Created: {OUTPUT_ZIP}")