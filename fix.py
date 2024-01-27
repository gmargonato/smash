import os
from PIL import Image

root_folder = '/Users/gabrielmargonato/Documents/Python Scripts/smash/SPRITES/RYU'

# Iterate through folders and files
for root, dirs, files in os.walk(root_folder):
    for file in files:
        if file.lower().endswith('.png'):  # Adjust the file extensions as needed
            file_path = os.path.join(root, file)

            # Open the image
            img = Image.open(file_path)
            img = img.convert("RGBA")

            # Get the image data
            datas = img.getdata()

            # Process the image data
            newData = []
            for item in datas:
                # If the pixel matches the specified color, make it transparent
                if item[0] == 248 and item[1] == 0 and item[2] == 248:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)

            # Update the image data
            img.putdata(newData)

            # Save the new image with transparency
            new_file_path = os.path.join(root, file)  # Appending '_t' to the original filename
            img.save(new_file_path, "PNG")

            print(f"Converted: {file}")
