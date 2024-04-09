import json
import random

# Function to generate a new unique random ID
def generate_unique_id(used_ids):
    new_id = str(random.randint(100, 999))  # Adjust the range as needed
    while new_id in used_ids:
        new_id = str(random.randint(100, 999))
    return new_id

# Load the existing JSON data from a file
with open('original.json', 'r') as infile:
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
with open('new_data.json', 'w') as outfile:
    json.dump(new_data, outfile, indent=4)

# Write the ID mapping to a separate JSON file
with open('id_mapping.json', 'w') as outfile:
    json.dump(id_mapping, outfile, indent=4)

print("New JSON file created with updated IDs: new_data.json")
print("ID mapping file created: id_mapping.json")
