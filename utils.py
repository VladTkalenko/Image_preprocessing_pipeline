import json
import config
from typing import Dict, Union, List
import os
import yaml
from tqdm import tqdm
import cv2


def update_json_data(json_path: str, data: Dict[str, Union[int, List[str]]]):

    # Writing to sample.json
    with open(json_path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4)


def read_json_data(json_path: str) -> Dict[str, Union[int, List[str]]]:
    with open(json_path, 'r', encoding='utf-8') as json_data:
        try:
            data = json.load(json_data)
            return data
        except ValueError:
            return config.JSON_TEMPLATE


def get_classes():
    with open(config.PROJECT_YAML_FILE, 'r') as file:
        classes = yaml.load(file, Loader=yaml.FullLoader)['names']

    return classes


def convert_coordinates_from_supervisely_to_yolo(obj: List[Union[int, Dict[str, List[List[int]]]]],
                                                 img_size: Dict[str, int]):

    xmax, ymax = obj[1]['exterior'][1]
    xmin, ymin = obj[1]['exterior'][0]
    width, height = img_size['width'], img_size['height']
    yolo_data = {
        'class': obj[0],
        'x_center': (xmax+xmin)/(2*width),
        'y_center': (ymax+ymin)/(2*height),
        'width': (xmax-xmin)/width,
        'height': (ymax-ymin)/height
    }
    return yolo_data


def prepare_lines_for_writing(annotations: List[Dict[str, int]]) -> List[str]:
    lines = []
    for obj in annotations:
        lines.append(f"{obj['class']} {obj['x_center']} {obj['y_center']} {obj['width']} {obj['height']}")

    return lines


def create_text_file_for_yolo_annotations(dest_labels_dir: str, annotations: List[Dict[str, int]]):
    lines = prepare_lines_for_writing(annotations)
    with open(dest_labels_dir+'.txt', 'w') as file:
        file.write('\n'.join(lines))


def save_supervisely_annotation_as_yolo(annotations, dataset_name: str, image_names: List[str]):
    os.makedirs(os.path.join(config.FINAL_LABELS, dataset_name), exist_ok=True)

    classes = get_classes()
    object_list = [[annotation.annotation['objects'], annotation.annotation['size']] for annotation in annotations]
    for idx, (one_image_objects, image_size) in enumerate(object_list):
        label_file_name = os.path.splitext(image_names[idx])[0] + '.txt'
        yolo_annotation = []
        label_info_about_image = [[classes.index(obj['classTitle']), obj['points']] for obj in one_image_objects]
        for obj in label_info_about_image:
            yolo_annotation.append(convert_coordinates_from_supervisely_to_yolo(obj, image_size))
        create_text_file_for_yolo_annotations(os.path.join(config.FINAL_LABELS, dataset_name, label_file_name),
                                              yolo_annotation)


def extract_frames_from_video_per_rate(src_videos: str, output_folder: str, frame_rate: int):
    for video_name in tqdm(os.listdir(src_videos)):
        print(f"Processing {video_name}...")
        folder_name = os.path.join(output_folder, video_name)
        os.makedirs(folder_name, exist_ok=True)

        video_cap = cv2.VideoCapture(os.path.join(src_videos, video_name))
        success, image = video_cap.read()
        count = 0
        while success:
            if count % frame_rate == 0:
                cv2.imwrite(os.path.join(folder_name, f"{count:0>6d}.jpg"), image)
            success, image = video_cap.read()

            count += 1


if __name__ == "__main__":
    read_json_data(config.TEMP_JSON_FILE)