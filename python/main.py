import os
from tqdm import tqdm
from anon_ids import anonymize_ids

cancer_dir_path = r"D:\anonymize_ids\incisive_anon_copy\breast"
id_mapping_file = 'id_mapping.json'
original_mapping = 'original.json'

dps = [os.path.basename(path) for path in os.listdir(cancer_dir_path)]

for dp in tqdm(dps, desc="Anonymizing Data Providers"):
    input_dir_path = os.path.join(cancer_dir_path, dp)
    print(f"\nAnonymizing data for {dp}")
    anonymize_ids(input_dir_path, id_mapping_file, original_mapping)
    