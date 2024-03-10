from PIL import Image
import os

master_folder_path = "/Users/gabrielmargonato/Downloads/Venom-1"

def trim_images_in_folder(folder_path):
    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        # Check if the file is a directory (subfolder)
        if os.path.isdir(filepath):
            # If it's a directory, recursively call trim_images_in_folder
            trim_images_in_folder(filepath)
        elif filename.endswith(".png"):
            # If the file is a PNG image
            # Open the image
            img = Image.open(filepath)
            # Get the bounding box of the non-transparent area
            bbox = img.getbbox()
            # If there is a bounding box (i.e., image is not entirely transparent)
            if bbox:
                # Crop the image to the bounding box
                cropped_img = img.crop(bbox)
                # Save the cropped image, overwriting the original
                cropped_img.save(filepath)
                print(f"Trimmed {filename}")
            else:
                print(f"No content found in {filename}")

trim_images_in_folder(master_folder_path)
