import sys
import os

def split_fasta_by_amp_id(fasta_file):
    """
    Splits a FASTA file into multiple files based on amplicon IDs extracted from sequence headers.

    Args:
        fasta_file (str): Path to the input FASTA file.
    """

    output_dir = "amplicon_sequences"
    os.makedirs(output_dir, exist_ok=True)

    amp_sequences = {}

    with open(fasta_file, "r") as infile:
        current_id = None
        current_header = None
        current_sequence = []

        for line in infile:
            if line.startswith(">"):
                if current_id:
                    amp_sequences[current_id].append((current_header, "".join(current_sequence)))

                current_header = line.strip()
                parts = current_header.split("_")
                if len(parts) >= 5:
                    amp_id = f"{parts[-4]}_{parts[-3]}"
                else:
                    amp_id = "UNKNOWN"

                current_id = amp_id
                current_sequence = []

                if amp_id not in amp_sequences:
                    amp_sequences[amp_id] = []
            else:
                current_sequence.append(line.strip())

        if current_id:
            amp_sequences[current_id].append((current_header, "".join(current_sequence)))

    for amp_id, sequences in amp_sequences.items():
        output_file = os.path.join(output_dir, f"{amp_id}_amplicon_sequences.fasta")
        with open(output_file, "w") as outfile:
            for header, sequence in sequences:
                outfile.write(f"{header}\n")
                outfile.write(f"{sequence}\n")

        print(f"Fichier FASTA créé : {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 7_2_split_output_fasta_in_silico_pcr_reformated.py <fasta_file>")
        sys.exit(1)

    fasta_file = sys.argv[1]
    split_fasta_by_amp_id(fasta_file)
