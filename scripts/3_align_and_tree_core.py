import os
import subprocess
from Bio import SeqIO, AlignIO
from Bio.Align import MultipleSeqAlignment
import argparse
import sys

def extract_unique_id(description):
    """Extrait l'ID unique sous la forme Cluster_Numéro."""
    header_parts = description.split("]")
    if len(header_parts) > 0:
        unique_id = header_parts[0].strip("[]")
        return unique_id
    return None

def align_and_tree(input_fasta):
    """
    Aligns gene sequences from a FASTA file and generates phylogenetic trees for each unique MICFAM group.

    Args:
        input_fasta (str): Path to the input FASTA file containing gene sequences.
    """
    gene_sequences = {}

    for record in SeqIO.parse(input_fasta, "fasta"):
        header_parts = record.description.split("]")
        if len(header_parts) > 3:
            micfam_number = header_parts[2].strip("[]")
            if micfam_number not in gene_sequences:
                gene_sequences[micfam_number] = []
            gene_sequences[micfam_number].append(record)

    for micfam_number, sequences in gene_sequences.items():
        aligned_fasta = f"micfam_{micfam_number}_aligned.afa"
        aligned_phylip = f"micfam_{micfam_number}_aligned.phy"
        tree_file = f"micfam_{micfam_number}_tree.txt"

        temp_input_fasta = "temp_input.fa"
        with open(temp_input_fasta, "w") as temp_fasta:
            SeqIO.write(sequences, temp_fasta, "fasta")

        if not os.path.exists(temp_input_fasta):
            print(f"Erreur : Le fichier temporaire {temp_input_fasta} n'a pas été créé.")
            continue

        try:
            muscle_command = ["muscle", "-align", temp_input_fasta, "-output", aligned_fasta]
            subprocess.run(muscle_command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de MUSCLE : {e}")
            continue

        if not os.path.exists(aligned_fasta):
            print(f"Erreur : Le fichier aligné {aligned_fasta} n'a pas été créé.")
            continue

        alignment = MultipleSeqAlignment(SeqIO.parse(aligned_fasta, "fasta"))
        for record in alignment:
            new_id = extract_unique_id(record.description)
            if new_id:
                record.id = new_id
                record.name = ""

        with open(aligned_phylip, "w") as phylip_file:
            AlignIO.write(alignment, phylip_file, "phylip")

        try:
            phyml_command = ["phyml", "-i", aligned_phylip, "-d", "nt","-m", "HKY85", "--quiet"]
            subprocess.run(phyml_command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de PhyML : {e}")
            continue

        phyml_output = aligned_phylip.replace(".phy", "_phyml_tree.txt")
        if os.path.exists(phyml_output):
            os.rename(phyml_output, tree_file)

        print(f"Alignement et arbre générés pour MICFAM {micfam_number}: {aligned_phylip}, {tree_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 3_align_and_tree_core.py <input_fasta>")
        sys.exit(1)

    input_fasta = sys.argv[1]
    align_and_tree(input_fasta)
