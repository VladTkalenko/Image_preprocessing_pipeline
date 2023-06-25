import os.path
from tqdm import tqdm
import numpy as np
import config
import shutil
from moviepy.editor import *
import cv2 as cv
from itertools import islice


def get_video_crop(start_time: float, end_time: float, src_path: str, dest_path: str):
    clip = VideoFileClip(src_path)
    clip = clip.subclip(start_time, end_time)
    clip.write_videofile(dest_path)


def play_frames_from_video(src_video: str,
                           folder_with_clips: str,
                           img_width: int = 1080,
                           img_height: int = 720):
    clip = VideoFileClip(src_video)

    iter_frames = clip.iter_frames(with_times=True)

    times = []
    num_of_frames = 0

    for time, frame in iter_frames:
        times.append(time)
        num_of_frames += 1


    counter = 0
    num_of_clips = 1
    start_clip_time = 0
    end_clip_time = 0
    times = [item[0] for item in clip.iter_frames(with_times=True)]
    while True:
        try:
            frame = clip.get_frame(times[counter])
            frame = cv.resize(frame, (img_width, img_height))
            frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
        except:
            print('Last frame is opened!')

        cv.imshow('Frame', frame)

        k = cv.waitKey(0)
        print(counter)
        if k == ord('q'):
            break

        elif k == ord('o'):
            start_clip_time = times[counter]
        elif k == ord('p'):
            end_clip_time = times[counter]

        elif k == ord(' '):
            old_file_name = os.path.basename(src_video)
            new_file_name = os.path.splitext(old_file_name)[0]+"-crop-{:0>5d}".format(num_of_clips) + \
                            os.path.splitext(old_file_name)[1]
            get_video_crop(start_time=start_clip_time,
                           end_time=end_clip_time,
                           src_path=src_video,
                           dest_path=os.path.join(folder_with_clips, new_file_name))
            num_of_clips += 1

        elif k == ord('s'):
            if counter < num_of_frames-1:
                counter += 1
            else:
                continue

        elif k == ord('a'):
            if counter > 0:
                counter -= 1
            else:
                continue


def trim_several_videos(src_path: str, folder_with_clips: str):
    video_paths = [os.path.join(src_path, video_name) for video_name in os.listdir(src_path)]
    for video_path in tqdm(video_paths):
        play_frames_from_video(video_path, folder_with_clips)


if __name__ == "__main__":
    trim_several_videos(config.NEW_FULL_VIDEOS, config.NEW_CROPPED_VIDEOS)
