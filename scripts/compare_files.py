import os
from pathlib import Path
import sys

def concat_directory_files(dir1, dir2):
    """Concatenate all files from each directory into single files, ignoring STL files."""
    dir1_path = Path(dir1)
    dir2_path = Path(dir2)
    output1=f"{dir1_path.stem}.txt"
    output2=f"{dir2_path.stem}.txt"

    
    if not dir1_path.exists() or not dir2_path.exists():
        print("One or both directories do not exist!")
        return

    # Get all files in both directories, excluding .stl and .yaml files
    files1 = set(f.relative_to(dir1_path) for f in dir1_path.rglob('*') 
                 if f.is_file() and f.suffix.lower() not in ['.stl', '.yaml'])
    files2 = set(f.relative_to(dir2_path) for f in dir2_path.rglob('*') 
                 if f.is_file() and f.suffix.lower() not in ['.stl', '.yaml'])

    # Rest of the code remains the same...
    all_files = sorted(files1.union(files2))

    # Concatenate files from directory 1
    with open(output1, 'w') as outfile1:
        for file in all_files:
            file_path = dir1_path / file
            if file_path.exists():
                outfile1.write(f"\n=== {file} ===\n")
                try:
                    with open(file_path, 'r') as infile:
                        outfile1.write(infile.read())
                except Exception as e:
                    outfile1.write(f"Error reading file: {str(e)}\n")
            else:
                outfile1.write(f"\n=== {file} ===\nFile does not exist in {dir1}\n")

    # Concatenate files from directory 2
    with open(output2, 'w') as outfile2:
        for file in all_files:
            file_path = dir2_path / file
            if file_path.exists():
                outfile2.write(f"\n=== {file} ===\n")
                try:
                    with open(file_path, 'r') as infile:
                        outfile2.write(infile.read())
                except Exception as e:
                    outfile2.write(f"Error reading file: {str(e)}\n")
            else:
                outfile2.write(f"\n=== {file} ===\nFile does not exist in {dir2}\n")

    print(f"Created concatenated files: {output1} and {output2}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_files.py <directory1> <directory2>")
        sys.exit(1)
    
    concat_directory_files(sys.argv[1], sys.argv[2])
