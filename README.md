# Image_preprocessing_pipeline

Python scripts, which automate the preparation of images to annotations.

There are three main scripts:
1. trim_video.py - creates cuts from video by specifying start and end frame time.
2. upload_project.py - crops created cuts on frames and prepare them for downloading on Supervisely - annotation tool.
3. download_project.py - download annotated data from Supervisely and uploaded them on GDrive folder. 
