import supervisely as sly
from utils import update_json_data, read_json_data, save_supervisely_annotation_as_yolo
from tqdm import tqdm
import os
import config
from dotenv import load_dotenv
from typing import List


def connect_to_supervisely() -> sly.api.Api:
    load_dotenv(config.ENV_FILE)
    api = sly.Api.from_env()
    return api


def get_team(api: sly.api.Api):
    return api.team.get_info_by_name(config.TEAM_NAME)


def get_project(api: sly.api.Api, workspace):
    return api.project.get_info_by_name(workspace.id, config.PROJECT_NAME)


def get_workspace(api: sly.api.Api, team):
    return api.workspace.get_info_by_name(team.id, config.WORKSPACE_NAME)


def get_dataset(api: sly.api.Api, project, dataset_name: str):
    return api.dataset.get_info_by_name(project.id, dataset_name)


def get_team_members(api: sly.api.Api, team):
    team_members = api.user.get_team_members(team.id)
    return team_members


def connect_to_project():
    api = connect_to_supervisely()
    team = get_team(api)
    workspace = get_workspace(api, team)
    project = get_project(api, workspace)
    return api, team, workspace, project


def get_dataset_names_from_project(api: sly.api.Api, project) -> List[str]:
    dataset_names = [dataset.name for dataset in api.dataset.get_list(project.id)]
    return dataset_names


def create_dataset(api: sly.api.Api, name: str, dataset_names: List[str], project):
    img_names = os.listdir(os.path.join(config.SELECTED_FRAMES, name))
    img_paths = [os.path.join(config.SELECTED_FRAMES, name, img_name) for img_name in img_names]
    if name in dataset_names:
        print(f"Dataset {name} already exist!")
        return
    new_dataset = api.dataset.create(project.id, name)
    img_infos = api.image.upload_paths(new_dataset.id, names=img_names, paths=img_paths)
    return new_dataset


def download_dataset(api: sly.api.Api, project, dataset_name: str):
    os.makedirs(os.path.join(config.ANNOTATED_FRAMES, dataset_name), exist_ok=True)

    dataset = get_dataset(api, project, dataset_name)
    images = api.image.get_list(dataset.id)

    image_names = [image.name.split('_')[-1] for image in images]
    image_ids = [image.id for image in images]
    save_paths = [os.path.join(config.ANNOTATED_FRAMES, dataset_name, image_name) for image_name in image_names]

    api.image.download_paths(dataset.id, image_ids, save_paths)
    annotations = api.annotation.download_batch(dataset.id, image_ids)
    save_supervisely_annotation_as_yolo(annotations, dataset_name, image_names)


def create_labeling_job(api: sly.api.Api, name: str, project, dataset, user_id: List[int]):
    class_names = [class_['title'] for class_ in api.project.get_meta(project.id)['classes']]
    new_job = api.labeling_job.create(name, dataset.id, user_id, classes_to_label=class_names)
    return new_job


def create_multiple_labeling_jobs_from_local_files(api: sly.api.Api,
                                                   dataset_names: List[str],
                                                   project,
                                                   team,
                                                   team_members):
    json_data = read_json_data(config.TEMP_JSON_FILE)
    users = get_team_members(api, team)
    for name in tqdm(os.listdir(config.SELECTED_FRAMES)):
        new_dataset = create_dataset(api, name, dataset_names, project)
        if new_dataset is None:
            continue

        new_job = create_labeling_job(api, name, project, new_dataset, [users[json_data['last_member_idx']].id])
        json_data['datasets_for_annotation'].append(name)
        json_data['last_member_idx'] = json_data['last_member_idx'] + 1 \
            if json_data['last_member_idx'] != len(team_members) - 1 else 0

    update_json_data(config.TEMP_JSON_FILE, json_data)


if __name__ == "__main__":
    connect_to_supervisely()
