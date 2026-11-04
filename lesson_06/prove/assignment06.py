"""
Course: CSE 351
Assignment: 06
Author: [Your Name]

Instructions:

- see instructions in the assignment description in Canvas

""" 

import multiprocessing as mp
import os
import cv2
import numpy as np

from cse351 import *

# Folders
INPUT_FOLDER = "faces"
STEP1_OUTPUT_FOLDER = "step1_smoothed"
STEP2_OUTPUT_FOLDER = "step2_grayscale"
STEP3_OUTPUT_FOLDER = "step3_edges"

NUM_PROCESSES = 3

# Parameters for image processing
GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)
CANNY_THRESHOLD1 = 75
CANNY_THRESHOLD2 = 155

# Allowed image extensions
ALLOWED_EXTENSIONS = ['.jpg']

# ---------------------------------------------------------------------------
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

# ---------------------------------------------------------------------------
def task_convert_to_grayscale(image):
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        return image # Already grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# ---------------------------------------------------------------------------
def task_smooth_image(image, kernel_size):
    return cv2.GaussianBlur(image, kernel_size, 0)

# ---------------------------------------------------------------------------
def task_detect_edges(image, threshold1, threshold2):
    if len(image.shape) == 3 and image.shape[2] == 3:
        print("Warning: Applying Canny to a 3-channel image. Converting to grayscale first for Canny.")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 3 and image.shape[2] != 1 : # Should not happen with typical images
        print(f"Warning: Input image for Canny has an unexpected number of channels: {image.shape[2]}")
        return image # Or raise error
    return cv2.Canny(image, threshold1, threshold2)

# ---------------------------------------------------------------------------
def load_queue(input_folder, output_folder, que):
    for filename in os.listdir(input_folder):
            # Check extension
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                continue
    
            # Could I put these in the queue? 
            input_image_path = os.path.join(input_folder, filename)
            output_image_path = os.path.join(output_folder, filename) # Keep original filename

            que.put((input_image_path, output_image_path))
    for i in range(NUM_PROCESSES):
            que.put(None)

# ---------------------------------------------------------------------------
def process_images_in_folder(token_id,                  # Lets me select only one processer for each step
                             input_folder,              # input folder 
                             output_folder,             # output folder
                             processing_function,       # function to process the image (ie., task_...())
                             input_que,                 # Input queue with (input_file_path, output_file_path)
                             output_que=None,           # Output queue takes (input_file_path, output_file_path). Leave empty if photo is finished.
                             next_step_folder=None,          # The folder extension for the next queue
                             load_args=None,            # Optional args for cv2.imread
                             processing_args=None):     # Optional args for processing function

    create_folder_if_not_exists(output_folder)
    print(f"\nProcessing images from '{input_folder}' to '{output_folder}'...")

    processed_count = 0
    # for filename in os.listdir(input_folder):
    #     # Check extension
    #     file_ext = os.path.splitext(filename)[1].lower()
    #     if file_ext not in ALLOWED_EXTENSIONS:
    #         continue

    #     # Could I put these in the queue? 
    #     input_image_path = os.path.join(input_folder, filename)
    #     output_image_path = os.path.join(output_folder, filename) # Keep original filename
    while True:
        item = input_que.get()
        if item is not None:
            input_image_path, output_image_path = item
            try:
                # Read the image
                if load_args is not None:
                    img = cv2.imread(input_image_path, load_args)
                else:
                    img = cv2.imread(input_image_path)

                if img is None:
                    print(f"Warning: Could not read image '{input_image_path}'. Skipping.")
                    continue

                # Apply the processing function
                if processing_args:
                    processed_img = processing_function(img, *processing_args)
                else:
                    processed_img = processing_function(img)

                # Save the processed image
                cv2.imwrite(output_image_path, processed_img)

                processed_count += 1

                # This only runs if an output que is provided. 
                if output_que is not None:
                    filename = os.path.basename(output_image_path)
                    new_input_image_path = output_image_path
                    new_output_image_path = os.path.join(next_step_folder, filename)
                    output_que.put((new_input_image_path, new_output_image_path))


            except Exception as e:
                print(f"Error processing file '{input_image_path}': {e}")
        else:
            print(f"Finished processing. {processed_count} images processed into '{output_folder}'.")
            if output_que is not None:
                # only put sentinels if processor num 0
                if token_id == 0:   
                    for i in range(NUM_PROCESSES):
                        output_que.put(None)
                        print(f"Putting NONE for {input_folder} and {output_folder}")       
            return


# ---------------------------------------------------------------------------
def run_image_processing_pipeline():
    print("Starting image processing pipeline...")

    # TODO
    # - create queues
    # - create barriers
    # - create the three processes groups
    # - you are free to change anything in the program as long as you
    #   do all requirements.

    # QUEUES - maxsize to prevent memory problems
    q_smooth = mp.Queue()
    q_grey = mp.Queue(maxsize=100)
    q_edge = mp.Queue(maxsize=100)

    # STEPS:
    # 1. Create Queues (DONE)
    # 2. Create system to load queues?
    # 3. Change function to take input and output queues (DONE)
    # 4.   #

    # --- Step 0: Preload Queue ---
    print("Loading first que...")
    load_queue(INPUT_FOLDER, STEP1_OUTPUT_FOLDER, q_smooth)

    processors = []
    for i in range(NUM_PROCESSES):
        # --- Step 1: Smooth Images ---
        process_step_1 = mp.Process(target=process_images_in_folder, args=(i, INPUT_FOLDER, STEP1_OUTPUT_FOLDER, task_smooth_image, q_smooth, q_grey, STEP2_OUTPUT_FOLDER), kwargs={"processing_args": (GAUSSIAN_BLUR_KERNEL_SIZE,)})
        # --- Step 2: Convert to Grayscale ---
        process_step_2 = mp.Process(target=process_images_in_folder, args=(i, STEP1_OUTPUT_FOLDER, STEP2_OUTPUT_FOLDER, task_convert_to_grayscale, q_grey, q_edge, STEP3_OUTPUT_FOLDER))
        # --- Step 3: Detect Edges ---
        process_step_3 = mp.Process(target=process_images_in_folder, args=(i, STEP2_OUTPUT_FOLDER, STEP3_OUTPUT_FOLDER, task_detect_edges, q_edge), kwargs={"load_args": cv2.IMREAD_GRAYSCALE, "processing_args": (CANNY_THRESHOLD1, CANNY_THRESHOLD2)})
        
        processors.append(process_step_1)
        processors.append(process_step_2)
        processors.append(process_step_3)
        

    for process in processors:
        process.start()

    for process in processors:
        process.join()


    print("\nImage processing pipeline finished!")
    print(f"Original images are in: '{INPUT_FOLDER}'")
    print(f"Grayscale images are in: '{STEP1_OUTPUT_FOLDER}'")
    print(f"Smoothed images are in: '{STEP2_OUTPUT_FOLDER}'")
    print(f"Edge images are in: '{STEP3_OUTPUT_FOLDER}'")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer('Processing Images')

    # check for input folder
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The input folder '{INPUT_FOLDER}' was not found.")
        print(f"Create it and place your face images inside it.")
        print('Link to faces.zip:')
        print('   https://drive.google.com/file/d/1eebhLE51axpLZoU6s_Shtw1QNcXqtyHM/view?usp=sharing')
    else:
        run_image_processing_pipeline()

    log.write()
    log.stop_timer('Total Time To complete')
