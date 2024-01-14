import os

def rename_gif_to_png(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(".gif"):
            old_path = os.path.join(directory_path, filename)
            new_filename = os.path.splitext(filename)[0] + ".png"
            new_path = os.path.join(directory_path, new_filename)

            os.rename(old_path, new_path)
            print(f"Renamed: {filename} to {new_filename}")

# Specify the directory path where your files are located
directory_path = "/Users/gabrielmargonato/Documents/Python Scripts/2DP/SPRITES/VENOM/CROUCH"

# Call the function to rename .gif files to .png
rename_gif_to_png(directory_path)
