import pandas as pd
from Bio import SeqIO
import sys

def extract_unique_micfam_values(csv_file):
    df = pd.read_csv(csv_file, sep="\t")
    unique_micfam_values = set(df["MICFAM_Id"].dropna().astype(str))
    return unique_micfam_values

def filter_fasta_by_micfam(csv_file, fasta_input, fasta_output):
    """
    Filters a FASTA file to include only sequences with micfam numbers 
    present in a given CSV file.

    Args:
        csv_file (str): Path to the CSV file containing micfam numbers.
        fasta_input (str): Path to the input FASTA file.
        fasta_output (str): Path to save the filtered FASTA file.
    """
    unique_micfam_values = extract_unique_micfam_values(csv_file)

    with open(fasta_output, "w") as out_fasta:
        for record in SeqIO.parse(fasta_input, "fasta"):
            header_parts = record.description.split("]")
            if len(header_parts) > 3:
                micfam_number = header_parts[2].strip("[]")
                if micfam_number in unique_micfam_values:
                    out_fasta.write(f">{record.description}\n{record.seq}\n")

    print(f"Filtrage terminé, fichier sauvegardé sous : {fasta_output}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python 2_fasta_core_genome_filtering_uniq_micfam.py <csv_file> <fasta_input> <fasta_output>")
        sys.exit(1)

    filter_fasta_by_micfam(sys.argv[1], sys.argv[2], sys.argv[3])
