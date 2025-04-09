import os
import csv
import argparse
import sys

def reformat_primers(input_dir, output_file_1,):
    def reformat_primers(input_dir, output_file_1):
        """
        Reformats primer data from multiple CSV files in a directory and writes the results to an output file.

        Args:
            input_dir (str): Path to the directory containing input CSV files with primer data.
            output_file_1 (str): Path to the output file where reformatted primer data will be saved.
        """
    all_primers = []

    for filename in os.listdir(input_dir):
        if filename.endswith("_primers_output.csv"):
            micfam_id = filename.split("_")[1]
            file_path = os.path.join(input_dir, filename)

            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                try:
                    header = next(reader)
                    if not header:
                        print(f"Fichier vide ou mal formaté: {filename}")
                        continue
                except StopIteration:
                    print(f"Fichier vide ou mal formaté: {filename}")
                    continue

                pair_index = 1
                for row in reader:
                    if len(row) < 5:
                        continue
                    forward, reverse, amplicon = row[1], row[2], row[3]
                    primer_id = f"{micfam_id}_{pair_index}"

                    all_primers.append(f"{forward}\t{reverse}\t{primer_id}\t{amplicon}\n")
                    pair_index += 1

    with open(output_file_1, 'w') as out1:
        out1.write("forward\treverse\tid\tamp_length\n")
        out1.writelines(all_primers)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python 5_primers_concat_reformat_from_directory.py <input_dir> <output_file>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    reformat_primers(input_dir, output_file)
