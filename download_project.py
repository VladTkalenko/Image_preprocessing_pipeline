import os
import shutil

from supervisely_utils import connect_to_project, download_dataset
from utils import read_json_data, update_json_data
import config
from tqdm import tqdm
from google_utils import upload_folder_on_google_drive, authentication, upload_files_to_folder


def download_annotated_photos_on_google_drive():
    drive = authentication()
    api, team, workspace, project = connect_to_project()
    json_data = read_json_data(config.TEMP_JSON_FILE)
    dataset_names = json_data['datasets_for_annotation']
    updated_dataset_names = dataset_names.copy()

    upload_files_to_folder(drive, config.CROPS_GOOGLE_DRIVE_FOLDER_ID, src_path=config.NEW_CROPPED_VIDEOS)
    upload_files_to_folder(drive, config.VIDEOS_GOOGLE_DRIVE_FOLDER_ID, src_path=config.NEW_FULL_VIDEOS)

    for dataset_name in tqdm(dataset_names):
        print(f"Download dataset {dataset_name}:")
        download_dataset(api, project, dataset_name)

        upload_folder_on_google_drive(drive, config.IMAGES_GOOGLE_DRIVE_FOLDER_ID,
                                      os.path.join(config.ANNOTATED_FRAMES, dataset_name))
        upload_folder_on_google_drive(drive, config.LABELS_GOOGLE_DRIVE_FOLDER_ID,
                                      os.path.join(config.FINAL_LABELS,
                                                   dataset_name))
        updated_dataset_names.remove(dataset_name)

        shutil.move(os.path.join(config.NEW_CROPPED_VIDEOS, dataset_name),
                    os.path.join(config.ALL_CROPPED_VIDEOS, dataset_name))
        shutil.rmtree(os.path.join(config.SELECTED_FRAMES, dataset_name))

    json_data['datasets_for_annotation'] = updated_dataset_names
    update_json_data(config.TEMP_JSON_FILE, json_data)

    print("Done!")


if __name__ == "__main__":
    download_annotated_photos_on_google_drive()
