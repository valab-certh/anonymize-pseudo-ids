import os
import random
import json
import warnings
import pydicom as dicom
import argparse
import shutil

from tqdm import tqdm

def get_new_triplet(provider, id_mapping_file, data_file):
    # Load ID mapping from JSON file
    with open(id_mapping_file, 'r') as infile:
        id_mapping = json.load(infile)

    # Load original data from JSON file
    with open(data_file, 'r') as infile:
        data = json.load(infile)

    # Check if the provider exists in the data
    if provider in data:
        # Get the old ID for the provider
        old_id = data[provider]

        # Check if the old ID has a corresponding new ID
        if old_id in id_mapping:
            new_id = id_mapping[old_id]
            return new_id
        else:
            return "Error: No new ID found for the provided old ID"
    else:
        return "Error: Provider not found in the data"
    
def get_new_id(old_id, id_mapping_file):
    # Load ID mapping from JSON file
    with open(id_mapping_file, 'r') as infile:
        id_mapping = json.load(infile)

    # Check if the old ID exists in the mapping
    if old_id in id_mapping:
        return id_mapping[old_id]
    else:
        return "Error: No new ID found for the provided old ID"

# Function to generate a new unique random ID
def generate_unique_id(used_ids):
    new_id = str(random.randint(100, 999))  # Adjust the range as needed
    while new_id in used_ids:
        new_id = str(random.randint(100, 999))
    return new_id

def generate_new_dp_ids():

    # Load the existing JSON data from a file
    with open(r'prm/original.json', 'r') as infile:
        data = json.load(infile)

    # Create a dictionary to store old IDs and corresponding new ones
    id_mapping = {}
    used_ids = set()

    # Generate new IDs and update the data dictionary
    new_data = {}
    for key, old_id in data.items():
        new_id = generate_unique_id(used_ids)
        used_ids.add(new_id)
        new_data[key] = new_id
        id_mapping[old_id] = new_id

    # Write the updated data to a new JSON file
    new_json_path = r'prm/new_data.json' 
    with open(new_json_path, 'w') as outfile:
        json.dump(new_data, outfile, indent=4)

    # Write the ID mapping to a separate JSON file
    id_mapping_path = r"prm/id_mapping.json"
    with open(id_mapping_path, 'w') as outfile:
        json.dump(id_mapping, outfile, indent=4)

    print(f"New JSON file created with updated IDs: {new_json_path}")
    print(f"ID mapping file created: {id_mapping_path}")

# Function to generate a unique random ID
def generate_random_id(existing_ids):
    while True:
        new_id = str(random.randint(100000, 999999))  # Generate a 6-digit random number
        if new_id not in existing_ids:  # Check if the generated ID is unique
            return new_id

def generate_new_pf_ids():

    cancer_types = ["breast", "colorectal", "lung", "prostate"]

    dps = {"breast": ["dp1", "dp2"],
        "colorectal": ["dp1", "dp2"],
        "lung": ["dp1", "dp2"],
        "prostate": ["dp1", "dp2"]}



    for cancer_type in cancer_types:
        data_providers = dps[cancer_type]
        for data_provider in data_providers:

            input_dir_path = rf"prm/incisive2/{cancer_type}/{data_provider}"

            dp = os.path.basename(input_dir_path)
            parent_dir = os.path.dirname(input_dir_path)
            working_dir = os.path.join(input_dir_path, "data")

            patient_folder_names = [os.path.join(working_dir, filename) for filename in os.listdir(working_dir) if os.path.isdir(os.path.join(working_dir, filename))]
            patient_foder_basenames = [os.path.basename(pf) for pf in patient_folder_names]
            patient_ids = [basename.split('-')[-1] for basename in patient_foder_basenames]

            # Path to the directory containing patient folders
            directory_path = working_dir

            # List of existing patient basenames
            existing_ids = patient_ids

            # Dictionary to store the mapping of old IDs to new IDs
            id_mapping = {}

            # Iterate through each patient folder
            for folder_name in os.listdir(directory_path):
                if os.path.isdir(os.path.join(directory_path, folder_name)):
                    # Extract the patient ID from the folder name
                    old_id = folder_name.split('-')[-1]

                    # Generate a new unique random ID
                    new_id = generate_random_id(existing_ids)

                    # Add the mapping to the dictionary
                    id_mapping[old_id] = new_id

                    # Add the new ID to the list of existing IDs
                    existing_ids.append(new_id)

            # Write the mapping to a JSON file
            with open(os.path.join(working_dir, f"id_mapping_{os.path.basename(parent_dir)}.json"), 'w') as json_file:
                json.dump(id_mapping, json_file, indent=4)

def anonymize_ids(input_dir_path, id_mapping_file, original_mapping):

    def rename_entity(entity_path, new_name):
        parent_dir = os.path.dirname(entity_path)
        new_entity_path = os.path.join(parent_dir, new_name)
        os.rename(entity_path, new_entity_path)
        return new_entity_path
    
    def rename_study(entity_path, new_name):
        parent_dir, basename = os.path.split(entity_path)
        basename = basename[11:] # Assuming the first 11 characters are to be removed
        new_name = f"{new_name}_{basename}"
        new_entity_path = os.path.join(parent_dir, new_name)
        os.rename(entity_path, new_entity_path)
        return new_entity_path
    
    def anonymize_dicom_file(dicom_file, new_dp_id, new_patient_id):
        warnings.filterwarnings("ignore")
        try:
            ds = dicom.dcmread(dicom_file)
            new_patient_name_tag = f"{new_dp_id}-{new_patient_id}"
            ds.PatientName = new_patient_name_tag
            ds.PatientID = new_patient_name_tag
            ds.save_as(dicom_file)
        except Exception as e:
            print(e)

    input_data_path = os.path.join(input_dir_path, "data")
    dp_name = os.path.basename(input_dir_path)
    cancer_type = os.path.basename(os.path.dirname(input_dir_path))

    new_dp_id = get_new_triplet(dp_name, id_mapping_file, original_mapping)
    patient_mapping_file = os.path.join(input_data_path, f"id_mapping_{cancer_type}.json")
    
    patient_names = [
    os.path.join(input_data_path, filename)
    for filename in os.listdir(input_data_path)
    if os.path.isdir(os.path.join(input_data_path, filename))
    ]
    
    for patient_name in tqdm(patient_names, total=len(patient_names), desc="Anonymizing patients"):
        old_patient_id = os.path.basename(patient_name).split('-')[-1]
        new_patient_id = get_new_id(old_patient_id, patient_mapping_file)
        new_patient_name = f"{new_dp_id}-{new_patient_id}"
        new_patient_path = rename_entity(patient_name,  new_patient_name)

        study_names = [
        os.path.join(new_patient_path, filename)
        for filename in os.listdir(new_patient_path)
        if os.path.isdir(os.path.join(new_patient_path, filename))
        ]

        for study_name in study_names:
            new_study_name = f"{new_dp_id}-{new_patient_id}"
            new_study_path = rename_study(study_name, new_study_name)

            series_names = [
            os.path.join(new_study_path, filename)
            for filename in os.listdir(new_study_path)
            if os.path.isdir(os.path.join(new_study_path, filename))
            ]

            for series_name in series_names:
                dicom_files = [
                os.path.join(series_name, filename)
                for filename in os.listdir(series_name)
                if filename.endswith(".dcm")
                ]
                for dicom_file in dicom_files:
                    anonymize_dicom_file(dicom_file, new_dp_id, new_patient_id)

def pseudo_ids_anonymization(args):
    
    input_dir_path, id_mapping_file, original_mapping = args.input_dir_path, args.mapping_json, args.original_json

    cancer_types = ["breast", "colorectal", "lung", "prostate"]

    dps = {"breast": ["dp1", "dp2"],
        "colorectal": ["dp1", "dp2"],
        "lung": ["dp1", "dp2"],
        "prostate": ["dp1", "dp2"]}

    dst_dir_path = r"tmp/incisive2"

    if os.path.exists(dst_dir_path):  # Check if directory exists
        os.rmdir(dst_dir_path)        # Remove directory
        print(f"Directory '{dst_dir_path}' deleted successfully.")
    else:
        print(f"Directory '{dst_dir_path}' does not exist.")

    shutil.copytree(input_dir_path, "tmp/incisive2", dirs_exist_ok=True)
    
    for cancer_type in cancer_types:
        data_providers = dps[cancer_type]
        for data_provider in data_providers:

            working_path = f"{dst_dir_path}/{cancer_type}/{data_provider}"
            print(f"Anonymizing {cancer_type}-{data_provider}")
        
            # Pseudo-IDs Anonymization
            anonymize_ids(working_path, id_mapping_file, original_mapping)

            # Excel Anonymization

            # Image Anonymization

def main_cli() -> None:
    import fire

    fire.Fire(pseudo_ids_anonymization)

if __name__ == "__main__":

    # Initialize ArgumentParser
    parser = argparse.ArgumentParser(description='Anonymize IDs Script')
    parser.add_argument('--input_dir_path', type=str, default=r"prm/incisive2", help='Path to apply IDs anonymization to')
    parser.add_argument('--mapping_json', type=str, default=r"prm/id_mapping.json", help='Path to mapping json file')
    parser.add_argument('--original_json', type=str, default=r"prm/original.json", help='Path to original mapping json file')
    # Parse the arguments
    args = parser.parse_args()

    pseudo_ids_anonymization(args)