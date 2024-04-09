import os
import json
import random

input_dir_path = r"D:\anonymize_ids\incisive_anon_copy\breast\uns"

# Function to generate a unique random ID
def generate_random_id(existing_ids):
    while True:
        new_id = str(random.randint(100000, 999999))  # Generate a 6-digit random number
        if new_id not in existing_ids:  # Check if the generated ID is unique
            return new_id

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

