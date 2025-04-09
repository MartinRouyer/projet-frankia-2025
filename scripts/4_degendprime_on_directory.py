import os
import subprocess
import argparse
import sys

def run_degenprime_on_directory(directory_path):
    """
    Executes the degenprime tool on all .afa files in the specified directory.

    Args:
        directory_path (str): Path to the directory containing .afa files.
    """
    if not os.path.isdir(directory_path):
        print(f"Le répertoire {directory_path} n'existe pas.")
        return

    for filename in os.listdir(directory_path):
        if filename.endswith(".afa"):
            input_file = os.path.join(directory_path, filename)
            output_file = os.path.join(directory_path, f"{os.path.splitext(filename)[0]}_primers_output.csv")

            command = [
                "degenprime",
                "--min_primer_len:18",
                "--max_primer_len:24",
                "--min_temp:54",
                "--max_temp:62",
                "--max_primers:20",
                "--amplicon:100",
                "--degenerate",
                f"--input_file:{input_file}",
                f"--output_file:{output_file}"
            ]

            try:
                subprocess.run(command, check=True)
                print(f"Traitement terminé pour {filename}")
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors du traitement de {filename}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 4_degendprime_on_directory.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    run_degenprime_on_directory(directory)
