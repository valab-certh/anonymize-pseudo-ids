import os
import argparse
import pydicom as dicom
from tqdm import tqdm
from utils import get_new_triplet, get_new_id
import warnings

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

if __name__ == "__main__":

    # Initialize ArgumentParser
    parser = argparse.ArgumentParser(description='Anonymize IDs Script')
    parser.add_argument('--input_dir_path', type=str, default=r"incisive_anon_copy\breast\auth", help='Path to apply IDs anonymization to')
    parser.add_argument('--mapping_json', type=str, default=r"id_mapping.json", help='Path to mapping json file')
    parser.add_argument('--original_json', type=str, default=r"original.json", help='Path to original mapping json file')
    # Parse the arguments
    args = parser.parse_args()

    anonymize_ids(input_dir_path=args.input_dir_path, id_mapping_file=args.mapping_json, original_mapping=args.original_json)
