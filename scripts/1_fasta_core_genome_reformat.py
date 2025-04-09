import pandas as pd
from Bio import SeqIO
import sys

def clean_organism_name(name):
    return name.replace(" ", "_")

def reformat_fasta(csv_file, fasta_input, fasta_output):
    """
    Reformats a FASTA file by updating sequence headers based on a mapping 
    derived from a CSV file.

    Args:
        csv_file (str): Path to the CSV file containing organism-to-cluster mapping.
        fasta_input (str): Path to the input FASTA file.
        fasta_output (str): Path to save the reformatted FASTA file.
    """
    df = pd.read_csv(csv_file, sep="\t")

    mapping = {clean_organism_name(row["Organism"]): row["Cluster"] for _, row in df.iterrows()}

    with open(fasta_output, "w") as out_fasta:
        for record in SeqIO.parse(fasta_input, "fasta"):
            header_parts = record.description.split("|")
            if len(header_parts) > 3:
                org_name = header_parts[-1].split("[")[-1].split("]")[0].strip()
                org_name_cleaned = clean_organism_name(org_name)
                if org_name_cleaned in mapping:
                    cluster_value = mapping[org_name_cleaned]
                    gene_name = header_parts[3].split("[")[0].strip()
                    genome_name = header_parts[2]
                    new_header = f"[{cluster_value}][{org_name_cleaned}][{header_parts[0]}][{header_parts[1]}][{genome_name}] {gene_name}"
                    record.description = new_header
                else:
                    print(f"Warning: Organism '{org_name}' not found in mapping.")
            else:
                org_name = header_parts[-1].split("[")[-1].split("]")[0].strip()
                org_name_cleaned = clean_organism_name(org_name) 
                if org_name_cleaned in mapping:
                    cluster_value = mapping[org_name_cleaned]  
                    new_header = f"[{cluster_value}][{org_name_cleaned}][{header_parts[0]}][{header_parts[1]}][{header_parts[2]}]"
                    record.description = new_header
                else:
                    print(f"Warning: Organism '{org_name}' not found in mapping.")
            record.id = ""  
            out_fasta.write(f">{record.description}\n{record.seq}\n")

    print(f"Reformatage terminé, fichier sauvegardé sous : {fasta_output}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python reformat_fasta.py <csv_file> <fasta_input> <fasta_output>")
        sys.exit(1)

    reformat_fasta(sys.argv[1], sys.argv[2], sys.argv[3])
