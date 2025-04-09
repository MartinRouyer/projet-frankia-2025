## Projet Printemps Master Bio-Informatique Lyon 1 

# Développement d'un pipeline pour identifier de nouveaux marqueurs génétiques et des amorces de PCR pour l'étude des bactéries Frankia dans le sol par metabarcoding.

---

## Données initiales
Un core génome extrait depuis Mage Genoscope : un fichier .fasta contenant le core génome ainsi que d'un fichier .csv avec les informations sur les différents CDS extraits. Les séquences sont regroupées en familles appelées "micfam".

---

## Étape 1 : Reformatage du FASTA

**Objectif :** Mettre les informations essentielles pour chaque séquence dans l'ID, notamment le numéro de cluster et de génome.

- **Script :** `1_fasta_core_genome_reformat.py`
- **Entrées :**
  - CSV avec la correspondance entre le nom de génome et le numéro de cluster/génome.
  - Fichier FASTA du core génome.
- **Sortie :** Fichier FASTA reformaté.

**Commande type :**
```
python3 scripts/1_fasta_core_genome_reformat.py <fichier_tab_genomes_clusters.csv> <input_genomes_core.fasta> <output_genomes_core_reform.fasta>
```

---

## Étape 2 : Filtrage des Micfam

**Objectif :** Ne garder que les micfam avec un seul gène et aucune duplication (41 séquences pour 41 génomes).

- **Script :** `2_fasta_core_genome_filtering_uniq_micfam.py`
- **Entrées :**
  - CSV filtré de Mage contenant uniquement les lignes des séquences dans une micfam avec 41 séquences.
  - Fichier FASTA du core génome reformaté.
- **Sortie :** Fichier FASTA du core génome reformaté et filtré.

**Commande type :**
```
python3 scripts/2_fasta_core_genome_filtering <input_genomes_core_reform.fasta> <output_genome_core_reform_filt.fasta>
```

---

## Étape 3 : Alignement et Génération d'Arbres Phylogénétiques

**Objectif :** Aligner et générer un arbre phylogénétique pour chaque gène/micfam. 

**Muscle :** Edgar, R.C., 2004. MUSCLE: multiple sequence alignment with high accuracy and high throughput. Nucleic Acids Res 32, 1792–1797. https://doi.org/10.1093/nar/gkh340

**PhyML :** Guindon, S., Dufayard, J.-F., Lefort, V., Anisimova, M., Hordijk, W., Gascuel, O., 2010. New algorithms and methods to estimate maximum-likelihood phylogenies: assessing the performance of PhyML 3.0. Syst Biol 59, 307–321. https://doi.org/10.1093/sysbio/syq010

- **Script :** `3_align_and_tree_core.py`
- **Entrée :** Fichier FASTA du core génome reformaté et filtré.
- **Sorties par micfam/gène :**
  - Fichier d'alignement en `.afa`.
  - Fichier d'alignement en `.phy`.
  - Fichier d'arbre `phyml_tree.txt`.
  - Fichier de statistiques d'arbre `phyml_stats.txt`.

**Commentaires :** Les séquences sont alignées avec MUSCLE, puis reformatées en `.phy` pour être utilisées par PhyML pour la création d'arbres phylogénétiques. Les fichiers de sorties sont générés dans le répertoire courant. Le mieux est de créer un nouveau répertoire dédié et s’y mettre pour exécuter la commande.

**Commande type :**
```
python3 scripts/3_align_and_tree_core.py <input_genome_core_reform_filt.fasta>
```

---

## Étape 4 : Design de Primers avec DeGenPrime

**Objectif :** Générer des primers qui amplifient le plus de séquences possibles dans l'alignement.

- **Script :** `4_degendprime_on_directory.py` (https://github.com/raw-lab/DeGenPrime)
- **Paramètres utilisés :**
  - `--min_primer_len:18`
  - `--max_primer_len:24`
  - `--min_temp:54`
  - `--max_temp:62`
  - `--max_primers:20`
  - `--amplicon:100`
  - `--degenerate`
- **Entrée :** Répertoire contenant des fichiers d'alignement en `.afa`.
- **Sortie :** Fichier CSV avec la liste des couples de primers par alignement.

**Commentaire :** L’outil fonctionne en cherchant des primers qui amplifient le plus de séquences possibles à partir du fichier d’alignement, mais il ne trouvera pas forcément de primers qui permettent d’amplifier tout.

**Commande type :**
```
python3 scripts/4_degendprime_on_directory.py <chemin_vers_repertoire_align_files>
```

**Format de sortie :**
```
Pair #,Forward,Reverse,Amplicon,Temp. Diff
1,GTCGGGCTGAACAACTCVACGAAC,GGCVTGCTCGAAGTCGTCCTTGAA,113,0.698456
2,TACGAGGAGGTGTCGVTCTC,CGCGTTCGTBGAGTTGTTC,272,0.518677
```

---

## Étape 5 : Concaténation et Reformatage des Primers

**Objectif :** Créer un fichier unique contenant tous les primers.

- **Script :** `5_primers_concat_reformat_from_directory.py`
- **Entrée :** Répertoire contenant les fichiers de sortie de Degenprime.
- **Sortie :** Fichier `.txt` unique contenant tous les couples de primers de tous les gènes/micfam.

**Commentaires :** Le fichier a ensuite été filtré pour ne conserver que les couples de primers avec une longueur d'amplicon inférieure à 700 (pour le séquencage illumina) et supérieure à 300 (seuil arbitraire qui sert a obtenir un amplicon suffisament résolutif). La colonne amp_length et l'entête du fichier ont également été retirés afin qu'il soit dans le bon format d'input de l'outil de PCR in silico. 

**Commande type :**
```
python3 scripts/5_primers_concat_reformat_from_directory.py <chemin_repertoire_primers> <output_all_primers_reformat>
```

**Format de sortie :**
Contient : primerForward primerReverse IDmicfam_Nprimer

```
ACGGCACCAAGAACTTCGTG	ATCATGTGCGACCAGAAGTCG	28729_2	
GACGGCACCAAGAACTTCGTG	CATCATGTGCGACCAGAAGTCG	28729_3	
```

---

## Étape 6 : PCR In Silico

**Objectif :** Effectuer une PCR in silico sur les génomes de Frankia et un échantillon de génomes bactériens du sol.

- **Script :** `perl in_silico_PCR.pl` (https://github.com/egonozer/in_silico_pcr)
- **Options utilisées :**
  - `-i` : Permet une indel.
  - `-m` : Permet un mismatch.
  - `-r` : Oriente la séquence de l'amplicon dans le même sens que les primers.
  - `-s` : Pour indiquer à la suite le fichier de génome en .fasta
  - `-p` : Pour indiquer à la suite le fichier de primers.

- **Entrées :**
  - Fichier FASTA des génomes.
  - Fichier des primers.
- **Sorties :**
  - Fichier FASTA contenant tous les amplicons.
  - Fichier `resume.txt` contenant les informations sur les amplicons.

**Commentaires :** Dans la version que nous avons utlisé (v0.5.1) l'option -i permet une indel et l'option -m permet un mismatch dans la PCR in silico, ce qui se rapproche davantage d'une PCR in vitro, bien que ce ne soit pas optimal. La nouvelle version de l'outil (v0.6) offre une plus grande liberté dans le nombre de mismatches et d'indels autorisés. L'option -r permet d'orienter la séquence de l'amplicon dans le même sens que les primers (option que nous n'avons malheureusement pas utilisée dans notre analyse). Ce script est relativement lent car il ne permet pas le multi-threading. Il faut compter environ 20 heures pour l'exécuter avec 1 000 couples de primers sur 41 génomes.

**Commande type :**
```
perl in_silico_PCR.pl -s <genomes.fasta> -p <primer_file.txt> -i -m > <resume_amplicons.txt> 2> <output_amplicons.fasta>
```

---

## Étape 7 : Traitement des Sorties de In Silico PCR

### 7.1 : Mise à Jour des En-têtes

**Objectif :** Mettre à jour les entêtes du fichier FASTA de sortie avec le cluster, l'ID du génome et l'ID de la séquence.

- **Script :** `7_1_reformat_output_fasta_in_silico_pcr.py`
- **Entrées :**
  - Fichier FASTA de sortie de in silico PCR contenant les amplicons.
  - Fichier `resume.txt` de in silico PCR.
- **Sortie :** Fichier FASTA avec en-têtes reformatées.

**Commande type :**
```
python3 7_1_reformat_output_fasta_in_silico_pcr.py <resume_amplicons.txt> <amplicons.fasta> <output_amplicons_reformat.fasta>
```

### 7.2 : Division du FASTA Reformaté

**Objectif :** Diviser le fichier FASTA reformaté en autant de fichiers FASTA que de couples de primers.

- **Script :** `7_2_split_output_fasta_in_silico_pcr_reformated.py`
- **Entrée :** Fichier FASTA avec en-têtes reformatées.
- **Sortie :** Fichiers FASTA divisés avec l'ID du primer comme nom de fichier.

**Commande type :**
```
python3 7_2_split_output_fasta_in_silico_pcr_reformated.py <input_amplicons_reformat.fasta> <output_divided_amplicons.fasta>
```

---

# Analyse de Données et Sélection des Couples de Primers

**Critères de Sélection des Couples de Primers :**

- **Amplification des 41 Génomes :** Les primers doivent amplifier les 41 génomes cibles.
- **Spécificité :** Aucune amplification des génomes des autres bactéries du sol.
- **Résolution Taxonomique :** Suffisante pour distinguer les clusters.
- **Taille des Amplicons :** Inférieure à 700 paires de bases.
- **Absence de Bases Dégénérées :** Critère bonus pour restreindre davantage la liste des candidats.

**Commentaires :** La résolution taxonomique a été évaluée en alignant les amplicons pour un primer (avec MAFFT option --adjustdirection qui permet de corriger les différentes orientations de nos amplicons comme l'option -r avec in_silico_pcr n'a pas été utilisée), puis en créant un arbre phylogénétique (avec PhyML sur Seaview, un logiciel pratique pour manipuler des séquences, les aligner puis faire des arbres).
La sortie de DeGenPrime contient le numéro de micfam du gène, ce numéro est attribué automatiquement par MaGe Genoscope lors de la création du fichier de core-genome. Se référer au fichier cité (data/genomes/core_50%aa_80%cov/41_frankia_core_filtered.tsv) pour faire la correspondance.

**MAFFT :** Katoh, K., Standley, D.M., 2013. MAFFT Multiple Sequence Alignment Software Version 7: Improvements in Performance and Usability. Mol Biol Evol 30, 772–780. https://doi.org/10.1093/molbev/mst010

**Seaview :** Gouy M., Guindon S. & Gascuel O. (2010) SeaView version 4 : a multiplatform graphical user interface for sequence alignment and phylogenetic tree building. Molecular Biology and Evolution 27(2):221-224.

---

## Logiciels et Dépendances Python Requises

### Logiciels
**Note :** Les exemples de commandes d'installation sont pour les systèmes d'exploitation Linux.

- **MaGe Genoscope** : Pour générer le core-genome
Trouvable au lien suivant :

https://mage.genoscope.cns.fr/microscope/home/index.php

(Onglet Comparative Genomics, Pan/Core-genome)

- **MUSCLE** : Pour l'alignement multiple des séquences.

Version utilisée : MUSCLE v5.2

Installation : 
```
sudo apt install muscle
```

- **PhyML** : Pour la construction des arbres phylogénétiques.

Version utilisée : PhyML 3.3.20220408

Installation : 
```
sudo apt install phyml
```

- **MAFFT** : Pour l'alignement des séquences avec correction d'orientation.

Version utilisée : mafft v7.505

Installation : 
```
sudo apt install mafft
```

- **SeaView** : Interface graphique pour l'alignement et la construction d'arbres phylogénétiques.

Version utilisée : seaview 5.0.5

Installation depuis : 
http://doua.prabi.fr/software/seaview

- **DeGenPrime** : Pour le design des primers avec possbilité de bases dégénérées.

Version utilisée : degenprime version 0.1.2

Installation depuis : 
https://github.com/raw-lab/DeGenPrime


- **in_silico_PCR** : Pour la simulation de PCR in silico.

Version utilisée : in_silico_pcr v0.5.1

Installation depuis : 
https://github.com/egonozer/in_silico_pcr


### Dépendances Python

- `pandas` : Pour la manipulation des fichiers CSV.
- `biopython` : Pour le traitement des fichiers FASTA et des séquences biologiques.
- `numpy` : Pour les opérations numériques.

Pour installer, écrire dans le terminal : 
```
pip install <nom_package_python_a_installer>
```

--- 



### Génomes Bactériens du Sol

**Liste des génomes bactériens utilisés pour évaluer la spécificité de nos amorces :**

- **Escherichia coli** : GCF_000005845.2
- **Klebsiella pneumoniae** : GCA_000240185.2
- **Pseudomonas aeruginosa** : GCA_000006765.1
- **Salmonella enterica** : GCA_000006945.2
- **Shigella sonnei** : GCA_002950395.1
- **Proteus mirabilis** : GCA_000069965.1
- **Bifidobacterium longum** : GCA_000196555.1
- **Bifidobacterium adolescentis** : GCA_000010425.1
- **Actinobacteria bacterium** : GCA_016700055.1
- **Mycobacterium tuberculosis** : GCA_000195955.2
- **Mycobacteroides abscessus** : GCA_000069185.1
- **Streptomyces scabiei** : GCA_000091305.1
- **Bacillus anthracis** : GCA_000008445.1
- **Listeria monocytogenes** : GCA_000196035.1
- **Staphylococcus aureus** : GCA_000013425.1
- **Streptococcus pneumoniae** : GCA_0001457635.1
- **Enterococcus faecalis** : GCA_000393015.1
- **Clostridia bacterium** : GCA_016887505.1

---

## Organisation du repertoire data/pcr_silico_results

Ce répertoire contient les résultats de l'analyse PCR in silico pour différents ensembles de données. Voici une explication de la structure des dossiers et de la nomenclature des fichiers.

### Structure des Dossiers

- **`700_300_frankia`** : Contient les résultats pour les amplicons de taille comprise entre 300 et 700 paires de bases pour les génomes de Frankia.
- **`700_300_non_target`** : Contient les résultats pour les amplicons de taille comprise entre 300 et 700 paires de bases pour les génomes non cibles.
- **`mlsa_frankia`** : Contient les résultats pour les analyses MLSA (Multi-Locus Sequence Analysis) sur les génomes de Frankia.
- **`mlsa_non_target`** : Contient les résultats pour les analyses MLSA sur les génomes non cibles.

### Nomenclature des Fichiers

- **`_i_m_`** : Indique que l'analyse a été réalisée avec les options `-i` (indel) et `-m` (mismatch) activées.
- **`_resume`** : Informations au niveau des amplicons trouvés par in_silico_pcr
- **`resume_summary_`** : Informations condensées par couple de primers testés avec in_silico_pcr, avec les calculs de % de génomes et de clusterts amplifiés
- **`_split_fastas`** : Dossier contenant les fichiers FASTA divisés par couple de primers.
- **`_aligned_oriented`** : Indique que les séquences ont été alignées et orientées dans le même sens avec MAFFT.
- **`_count_`** : Fichiers de comptage pour evaluer les couples de primers non spécifiques qui amplifie des bacteries du sol.


## Contact
Pipeline par :

- Martin ROUYER : martin.rouyer@etu.univ-lyon1.fr 
- Clara CENTA : clara.centa@etu.univ-lyon1.fr

Etudiants en M1 Bio-informatique, Université Claude Bernard Lyon 1

Réalisé dans le cadre d'un projet M1 de bio-informatique, Mars 2025

N'hésitez pas à nous poser des questions si besoin.








