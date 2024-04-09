import json

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