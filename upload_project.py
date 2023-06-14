from supervisely_utils import get_team_members, get_dataset_names_from_project, \
    create_multiple_labeling_jobs_from_local_files, connect_to_project
from utils import extract_frames_from_video_per_rate
import config


def prepare_local_files_for_annotation():
    print("Frames extraction")
    extract_frames_from_video_per_rate(config.NEW_CROPPED_VIDEOS, config.SELECTED_FRAMES, config.FRAME_RATE)

    api, team, workspace, project = connect_to_project()
    team_members = get_team_members(api, team)

    dataset_names = get_dataset_names_from_project(api, project)

    print("Download data into supervisely...")
    create_multiple_labeling_jobs_from_local_files(api,
                                                   dataset_names,
                                                   project,
                                                   team,
                                                   team_members)
    print("Done!")


if __name__ == "__main__":
    prepare_local_files_for_annotation()
