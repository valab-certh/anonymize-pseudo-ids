from __future__ import annotations  # noqa: EXE002

import json
import os
import random
import shutil
import warnings
from pathlib import Path

import pydicom as dicom
from tqdm import tqdm


def get_new_triplet(provider: str, mapping_json: Path, data_file: Path) -> str:
    # Load ID mapping from JSON file
    with Path.open(mapping_json) as infile:
        id_mapping = json.load(infile)

    # Load original data from JSON file
    with Path.open(data_file) as infile:
        data = json.load(infile)

    # Check if the provider exists in the data
    if provider in data:
        # Get the old ID for the provider
        old_id = data[provider]

        # Check if the old ID has a corresponding new ID
        if old_id in id_mapping:
            return str(id_mapping[old_id])
        return ""
    return ""


def get_new_id(old_id: str, mapping_json: Path) -> str:
    # Load ID mapping from JSON file
    with Path.open(mapping_json) as infile:
        id_mapping = json.load(infile)

    # Check if the old ID exists in the mapping
    if old_id in id_mapping:
        return str(id_mapping[old_id])
    return ""


# Function to generate a new unique random ID
def generate_unique_id(used_ids: set[str]) -> str:
    new_id = str(random.randint(100, 999))  # noqa: S311
    while new_id in used_ids:
        new_id = str(random.randint(100, 999))  # noqa: S311
    return new_id


def generate_new_dp_ids() -> None:
    # Load the existing JSON data from a file
    with Path.open(Path(r"prm/original.json")) as infile:
        data = json.load(infile)

    # Create a dictionary to store old IDs and corresponding new ones
    id_mapping = {}
    used_ids: set[str] = set()

    # Generate new IDs and update the data dictionary
    new_data = {}
    for key, old_id in data.items():
        new_id = generate_unique_id(used_ids)
        used_ids.add(new_id)
        new_data[key] = new_id
        id_mapping[old_id] = new_id

    # Write the updated data to a new JSON file
    new_json_path = r"prm/new_data.json"
    with Path.open(Path(new_json_path), "w") as outfile:
        json.dump(new_data, outfile, indent=4)

    # Write the ID mapping to a separate JSON file
    id_mapping_path = r"prm/id_mapping.json"
    with Path.open(Path(id_mapping_path), "w") as outfile:
        json.dump(id_mapping, outfile, indent=4)


# Function to generate a unique random ID
def generate_random_id(existing_ids: list[str]) -> str:
    while True:
        new_id = str(random.randint(100000, 999999))  # noqa: S311
        if new_id not in existing_ids:  # Check if the generated ID is unique
            return new_id


def generate_new_pf_ids() -> None:
    cancer_types = ["breast", "colorectal", "lung", "prostate"]

    dps = {
        "breast": ["dp1", "dp2"],
        "colorectal": ["dp1", "dp2"],
        "lung": ["dp1", "dp2"],
        "prostate": ["dp1", "dp2"],
    }

    for cancer_type in cancer_types:
        data_providers = dps[cancer_type]
        for data_provider in data_providers:
            input_dir_path = Path(rf"prm/incisive2/{cancer_type}/{data_provider}")

            Path.name(input_dir_path)
            parent_dir = Path.parent(input_dir_path)
            working_dir = Path(input_dir_path, "data")

            patient_folder_names = [
                Path(working_dir, filename)
                for filename in os.listdir(working_dir)
                if Path.is_dir(Path(working_dir, filename))
            ]
            patient_foder_basenames = [Path.name(pf) for pf in patient_folder_names]
            patient_ids = [
                basename.split("-")[-1] for basename in patient_foder_basenames
            ]

            # Path to the directory containing patient folders
            directory_path = working_dir

            # List of existing patient basenames
            existing_ids = patient_ids

            # Dictionary to store the mapping of old IDs to new IDs
            id_mapping = {}

            # Iterate through each patient folder
            for folder_name in os.listdir(directory_path):
                if Path.is_dir(Path(directory_path, folder_name)):
                    # Extract the patient ID from the folder name
                    old_id = folder_name.split("-")[-1]

                    # Generate a new unique random ID
                    new_id = generate_random_id(existing_ids)

                    # Add the mapping to the dictionary
                    id_mapping[old_id] = new_id

                    # Add the new ID to the list of existing IDs
                    existing_ids.append(new_id)

            # Write the mapping to a JSON file
            with Path.open(
                Path(
                    working_dir,
                    f"id_mapping_{Path.name(parent_dir)}.json",
                ),
                "w",
            ) as json_file:
                json.dump(id_mapping, json_file, indent=4)


def anonymize_ids(
    input_dir_path: Path,
    mapping_json: Path,
    original_json: Path,
) -> None:
    def rename_entity(entity_path: Path, new_name: str) -> Path:
        parent_dir = Path.parent(entity_path)
        new_entity_path = Path(parent_dir, new_name)
        Path.rename(entity_path, new_entity_path)
        return new_entity_path

    def rename_study(entity_path: Path, new_name: str) -> Path:
        parent_dir, basename = os.path.split(entity_path)
        basename = basename[11:]  # Assuming the first 11 characters are to be removed
        new_name = f"{new_name}_{basename}"
        new_entity_path = Path(parent_dir, new_name)
        Path.rename(entity_path, new_entity_path)
        return new_entity_path

    def anonymize_dicom_file(
        dicom_file: Path,
        new_dp_id: str,
        new_patient_id: str,
    ) -> None:
        warnings.filterwarnings("ignore")
        try:
            ds = dicom.dcmread(dicom_file)
            new_patient_name_tag = f"{new_dp_id}-{new_patient_id}"
            ds.PatientName = new_patient_name_tag
            ds.PatientID = new_patient_name_tag
            ds.save_as(dicom_file)
        except TypeError:
            pass

    input_data_path = Path(input_dir_path, "data")
    dp_name = Path.name(input_dir_path)
    cancer_type = Path.name(Path.parent(input_dir_path))

    new_dp_id = get_new_triplet(dp_name, mapping_json, original_json)
    patient_mapping_file = Path(
        input_data_path,
        f"id_mapping_{cancer_type}.json",
    )

    patient_names = [
        Path(input_data_path, filename)
        for filename in os.listdir(input_data_path)
        if Path.is_dir(Path(input_data_path, filename))
    ]

    for patient_name in tqdm(
        patient_names,
        total=len(patient_names),
        desc="Anonymizing patients",
    ):
        old_patient_id = Path.name(patient_name).split("-")[-1]
        new_patient_id = get_new_id(old_patient_id, patient_mapping_file)
        new_patient_name = f"{new_dp_id}-{new_patient_id}"
        new_patient_path = rename_entity(patient_name, new_patient_name)

        study_names = [
            Path(new_patient_path, filename)
            for filename in os.listdir(new_patient_path)
            if Path.is_dir(Path(new_patient_path, filename))
        ]

        for study_name in study_names:
            new_study_name = f"{new_dp_id}-{new_patient_id}"
            new_study_path = rename_study(study_name, new_study_name)

            series_names = [
                Path(new_study_path, filename)
                for filename in os.listdir(new_study_path)
                if Path.is_dir(Path(new_study_path, filename))
            ]

            for series_name in series_names:
                dicom_files = [
                    Path(series_name, filename)
                    for filename in os.listdir(series_name)
                    if filename.endswith(".dcm")
                ]
                for dicom_file in dicom_files:
                    anonymize_dicom_file(dicom_file, new_dp_id, new_patient_id)


def anonymize_pseudo_ids(
    input_dir: Path,
    mapping_json: Path = Path(r"prm/id_mapping.json"),
    original_json: Path = Path(r"prm/original.json"),
) -> None:
    cancer_types = ["breast", "colorectal", "lung", "prostate"]

    dps = {
        "breast": ["dp1", "dp2"],
        "colorectal": ["dp1", "dp2"],
        "lung": ["dp1", "dp2"],
        "prostate": ["dp1", "dp2"],
    }

    dst_dir_path = Path(r"tmp/incisive2")

    if Path.exists(dst_dir_path):  # Check if directory exists
        Path.rmdir(dst_dir_path)  # Remove directory
    else:
        pass

    shutil.copytree(input_dir, "tmp/incisive2", dirs_exist_ok=True)

    for cancer_type in cancer_types:
        data_providers = dps[cancer_type]
        for data_provider in data_providers:
            working_path = Path(f"{dst_dir_path}/{cancer_type}/{data_provider}")

            # Pseudo-IDs Anonymization
            anonymize_ids(working_path, mapping_json, original_json)

            # Excel Anonymization

            # Image Anonymization


def main_cli() -> None:
    import fire

    fire.Fire(anonymize_pseudo_ids)


if __name__ == "__main__":
    input_dir = Path(r"prm/incisive2")

    anonymize_pseudo_ids(input_dir)
