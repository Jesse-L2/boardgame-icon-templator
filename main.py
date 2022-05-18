"""boardgame-icon-templator uses Python and the Pillow library to dynamically resize art and place icons on an image.
 This project was born to save time as a game I was working on, Aviation Wars, has 48 parts with up to 7 icons that
 needed to be consistently placed as well as handle instances of not having an icon. """
import os
import textwrap
import pandas as pd
from math import isnan
from PIL import Image, ImageChops, ImageFont, ImageDraw


# Chops = channel operations module
def trim_whitespace(image):
    """Takes an image, defines a background by looking at the upper-left most pixel and then forms a rectangular
    crop around the image moving in until there is a difference between the color of
    the background and the image itself"""
    bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 1, 0)
    # bbox is a tuple defining pixel coordinates of the bounding box of the image vs the background
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)


def make_white_transparent(image):
    """Takes an image, Loops through each pixel in the image and if they are white, makes them transparent,
    thus allowing for clean placement on the final parts"""
    image = image.convert('RGBA')  # Convert all pixels from RGB to RGBA
    # image_data = image.getdata()

    new_image = []
    # Loop through each pixel in the image and change the alpha value to 0 as long as pixel is true white
    for pixel in image.getdata():
        if pixel[:3] == (255, 255, 255):
            new_image.append((255, 255, 255, 0))  # 0 on 4th is for alpha
        else:
            new_image.append(pixel)
    image.putdata(new_image)
    return image


# Creating variables for the size of the plane art to ensure a consistent start point
X, Y = 2400, 2720
part_font = ImageFont.truetype('assets/fonts/monofonto.ttf', 70)

GRAY_PLANE_TEMPLATE = Image.open('assets/plane_parts/Gray_Plane.png')
gray_w, gray_h = GRAY_PLANE_TEMPLATE.size
GRAY_PLANE_TEMPLATE = GRAY_PLANE_TEMPLATE.resize((X, Y))
GRAY_PLANE_TEMPLATE.save('assets/plane_parts/resized_Gray_Plane.png')
BLUE_PLANE_TEMPLATE = Image.open('assets/plane_parts/Blue_Plane.png')
blue_w, blue_h = BLUE_PLANE_TEMPLATE.size
BLUE_PLANE_TEMPLATE = BLUE_PLANE_TEMPLATE.resize((X, Y))
BLUE_PLANE_TEMPLATE.save('assets/plane_parts/resized_Blue_Plane.png')
GREEN_PLANE_TEMPLATE = Image.open('assets/plane_parts/Green_Plane.png')
green_w, green_h = GREEN_PLANE_TEMPLATE.size
GREEN_PLANE_TEMPLATE = GREEN_PLANE_TEMPLATE.resize((X, Y))
GREEN_PLANE_TEMPLATE.save('assets/plane_parts/resized_Green_Plane.png')
RED_PLANE_TEMPLATE = Image.open('assets/plane_parts/Red_Plane.png')
red_w, red_h = GRAY_PLANE_TEMPLATE.size
RED_PLANE_TEMPLATE = RED_PLANE_TEMPLATE.resize((X, Y))
RED_PLANE_TEMPLATE.save('assets/plane_parts/resized_Red_Plane.png')


# Create a copy of each full plane template
# Resize each plane part to ensure everything is the exact same size for later templating

def main():
    os.chdir('assets/plane_parts')
    for filename in os.listdir('.'):
        if filename.endswith('.png'):
            im = Image.open(filename)
            im_copy = im.copy()
            im_copy = im_copy.resize((X, Y))
            im_copy.save(f'resized_{filename}')
            # all pieces are now 2400 x 2720
    print(f"Resized template images to {X}x{Y}")

    # Cut the pieces into 4 pieces by height (with dynamic sizing)
    part_name_key = {
        0: "engine",
        int(0.25 * Y): "wings",
        int(0.5 * Y): "body",
        int(0.75 * Y): "tail",
    }
    # Create a copy of each image to do the actual work on preventing overwriting original images
    for filename in os.listdir('.'):
        if filename.startswith('resized'):
            for index, top in enumerate(range(0, Y, int(Y * 0.25))):
                im = Image.open(filename)
                im_copy = im.copy()
                cropped_im = im_copy.crop((0, top, X, int(top + (Y / 4))))
                cropped_im.save(f'{part_name_key[top]}_{filename}')
    # Trim the white space and make any remaining surrounding white space transparent
    os.chdir('assets/part_icons')
    for filename in os.listdir('.'):
        # Checking only for files ending with .png
        if filename.endswith('.png'):
            im = Image.open(filename)
            im_copy = im.copy()
            im_copy.resize((3840, 2160))
            # im_copy = trim_whitespace(im_copy)
            if 'Pop' not in filename:  # Skipping popularity icon due to white center and it is already square
                im_copy = make_white_transparent(im_copy)
        # Setting the final size of the icons in pixels (width, height)
        if filename.startswith('Lucky'):
            new_size = (300, 100)
        elif filename.startswith('Fly'):
            new_size = (400, 100)
        else:
            new_size = (150, 150)
        im_copy = im_copy.resize(new_size)
        print(f"Creating and saving resized_{filename}")
        im_copy.save(f'resized_{filename}')

    os.chdir('../part_icons')

    # Create a dataframe from planeparts.csv with pandas, allows for customizing stats for individual pieces
    data = pd.read_csv('planeparts.csv')
    plane_df = pd.DataFrame(data)
    # Iterate through each row of plane_df

    # change directory to new Final Parts and Icons
    os.chdir('assets/Final Parts and Icons')
    print('CWD: ', os.getcwd())
    # Establish which icon will go on each part by assigning to variables from planeparts.csv
    for i in range(0, len(plane_df)):
        number = plane_df['Number'][i]
        name = plane_df['Part Name'][i]
        part_type = str(plane_df['Type'][i])
        color = plane_df['Color'][i]
        cost = plane_df['Cost'][i]
        fly = plane_df['Fly'][i]
        money = plane_df['Money'][i]
        popularity = plane_df['Pop'][i]
        lucky = plane_df['Lucky'][i]
        vp = plane_df['VP'][i]
        part_image = Image.open(f'{part_type}_resized_{color.capitalize()}_Plane.png')
        im_copy = part_image.copy()
        width, height = im_copy.size
        # im_copy.show()
        # Add the title text to each piece, formatting it to center the text and place it in proper location
        draw = ImageDraw.Draw(im_copy)
        title = f'{name}'
        wrapper = textwrap.TextWrapper(
            width=12, max_lines=2, break_long_words=False, break_on_hyphens=False
        )
        string = wrapper.fill(text=title)

        draw.multiline_text(
            (250, 85), string, (255, 255, 255), align='center', anchor='mm', font=part_font
        )
        # Add the part reward for money (icon)
        if not isnan(money):
            money_icon = Image.open(f'resized_$_{int(money)}.png')
            im_copy.paste(
                im=money_icon, box=(int(0.03 * width), int(0.525 * height)), mask=money_icon
            )
        # Add the part reward for popularity (icon)
        if not isnan(popularity):
            pop_icon = Image.open(f'resized_Pop_Green_{int(popularity)}.png')
            im_copy.paste(
                im=pop_icon,
                box=(int(0.11 * width), int(0.525 * height)),
            )
        # Add the cost to purchase the part (icon)
        if not isnan(cost):
            cost_icon = Image.open(f'resized_Cost_{int(cost)}.png')
            im_copy.paste(
                im=cost_icon, box=(int(0.85 * width), int(0.02 * height)), mask=cost_icon
            )
        # Add the flying value to the part (icon)
        if not isnan(fly):
            fly_icon = Image.open(f'resized_Fly_{int(fly)}.png')
            im_copy.paste(
                im=fly_icon, box=(int(0.02 * width), int(0.28 * height)), mask=fly_icon
            )
        # Add any lucky icons to the part (icon)
        if not isnan(lucky):
            if lucky == 1:
                lucky_icon = Image.open(f'resized_LuckyText.png')
            elif lucky == 2:
                lucky_icon = Image.open(f'resized_LuckyTextx2.png')
            im_copy.paste(lucky_icon, (int(0.035 * width), int(0.8 * height)), lucky_icon)
        # Add any end of game bonus victory points for owning the part (icon)
        if not isnan(vp):
            vp_icon = Image.open('resized_VP_2.png')
            im_copy.paste(
                im=vp_icon, box=(int(0.925 * width), int(0.02 * height)), mask=vp_icon
            )
        # Print out the Final file name and stats for the part and save those in a separate file for final_parts
        print(f'Saving Final_{color}_{part_type}_{number}.png')
        print(number, name, cost, fly, money, popularity, lucky, vp)  # Print out of stats on the piece
        im_copy.save(f'Final_{color}_{part_type}_{number}.png')


if __name__ == "__main__":
    main()
