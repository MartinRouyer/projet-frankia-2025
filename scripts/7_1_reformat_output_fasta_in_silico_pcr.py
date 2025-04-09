import sys
import pandas as pd
from Bio import SeqIO

def update_fasta_headers(txt_file, fasta_file, output_fasta_file):
    """
    Updates the headers of a FASTA file based on a mapping provided in a tab-delimited text file.

    Args:
        txt_file (str): Path to the tab-delimited text file containing 'AmpId' and 'SequenceId' columns.
        fasta_file (str): Path to the input FASTA file whose headers need to be updated.
        output_fasta_file (str): Path to save the updated FASTA file.
    """

    df = pd.read_csv(txt_file, sep="\t")

    amp_id_to_cluster = df.set_index('AmpId')['SequenceId'].to_dict()

    sequences = list(SeqIO.parse(fasta_file, "fasta"))

    for seq in sequences:
        amp_id = seq.id
        if amp_id in amp_id_to_cluster:
            genome_cluster_id = amp_id_to_cluster[amp_id]
            seq.id = f"{genome_cluster_id}_{amp_id}"
            seq.description = ""

    with open(output_fasta_file, "w") as output_file:
        SeqIO.write(sequences, output_file, "fasta")

    print(f"Fichier FASTA mis à jour : {output_fasta_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python 7_1_reformat_output_fasta_in_silico_pcr.py <txt_file> <fasta_file> <output_fasta_file>")
        sys.exit(1)

    txt_file = sys.argv[1]
    fasta_file = sys.argv[2]
    output_fasta_file = sys.argv[3]

    update_fasta_headers(txt_file, fasta_file, output_fasta_file)
