import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import config
import mimetypes


def authentication():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive


def create_folder_on_google_drive(drive, parent_folder_id: str, name: str):
    gdrive_folder = drive.CreateFile({
        "title": name,
        "parents": [{"id": parent_folder_id}],
        "mimeType": "application/vnd.google-apps.folder"
    })
    gdrive_folder.Upload()

    return gdrive_folder


def upload_files_to_folder(drive, gdrive_folder_id, src_path: str):
    file_paths = [os.path.join(src_path, file) for file in os.listdir(src_path)]
    for file_path in file_paths:
        mime_type = mimetypes.guess_type(file_path)[0]
        f = drive.CreateFile({
            'title': os.path.basename(file_path),
            "parents": [{"id": gdrive_folder_id}],
            'mimeType': mime_type})
        f.SetContentFile(file_path)
        f.Upload()


def upload_folder_on_google_drive(drive, parent_gdrive_folder_id: str, src_path: str):
    folder_name = os.path.basename(src_path)
    new_folder = create_folder_on_google_drive(drive, parent_gdrive_folder_id, folder_name)
    upload_files_to_folder(drive, new_folder['id'], src_path)


if __name__ == "__main__":
    upload_folder_on_google_drive(config.IMAGES_GOOGLE_DRIVE_FOLDER_ID,
                                  "/home/vlad/Videos/Project 1-20230401T062938Z-001/test_images/test_folder")




