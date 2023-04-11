#img2map.py
#Copyright Luka Beg (PsychoCoffeee)
#Personal use only
#CC BY-NC-ND 4.0
#Release v1.6 - April 12th of 2023, 1:32 AM
import numpy as np #Necessary imports and libraries
from PIL import Image
import os
import time
import cv2
import random
allowLooping = True #Should the program loop or not?
successful = True #Did the program leave sucessfully?
def clearscreen(): #Clearing the whole screen for aesthetic reasons
    os.system('cls')
def helpscreen(): #Helping screen
    clearscreen()
    print("|------------------------------------------------------|")
    print("|                   img2map.exe                        |")
    print("|                      HELP                            |")
    print("|------------------------------------------------------|")
    print(" ")
    print("img2map.exe is a tool created for generating roughness and metalness maps. Version 1.6 (12/April/2023)")
    print("Made with the CC BY-NC-ND 4.0 license for private noncommercial use!")
    print("")
    print("\n(1) Roughness Maps\nRoughness maps define the roughness of the material/image used in a map/game engine.")
    print("The darker the image is, the more reflective it is. The lighter the image is, the less reflective it is.")
    print("\n(2) Metallic Maps\nMetallic maps define the metallic shine of a material/image used in a map/game engine.")
    print("This means that some parts of the image using metallic maps will be darker in some angles.")
    print("\n(3) Displacement Maps\nDisplacement maps are opposite of normal maps. Instead of giving the illusion")
    print("of a material being 3D, it actually changes the geometry of the material to look better.")
    print("\n(4) Opacity Maps\nOpacity maps are images that determine the transparency or opacity of")
    print("corresponding pixels in another image. For example: railings, ladders windows that have transparent parts.")
    print(" ")
    print("(5) Bump Maps\nBump maps are same as normal maps. But while outdated still useful in some applications.")
    ask_for_looping(False, True)

def convertimage_to(importpath, convertto):
    print("\nOpening directory...")
    if '"' in importpath:
        importpath = importpath.replace('"', '') #Remove quotes if they are present as they mess up the code
    mkdirpath = importpath
    mkdirpath.replace(os.path.splitext(os.path.basename(importpath))[0], '') #This took too long! Working from 11pm to 2am. (12/4/2023)
    mkdirpath += '\\'
    mkdirpath += convertto
    mkdirpath += str(random.randint(0, 4294967295)) #Put a random number (max number is size of uint32) so the folders don't replace each other
    print(mkdirpath)
    os.mkdir(mkdirpath) #create folder with mkdirpath string
    mkdirpath += '\\'

    for filename in os.listdir(importpath):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')):
            print("\nConverting", filename, "to", convertto)
            finalpath = mkdirpath
            finalpath += filename
            
            filepath = os.path.join(importpath, filename)
            img = cv2.imread(filepath)

            exportpath = os.path.splitext(finalpath)[0] + '.' + convertto 

            cv2.imwrite(exportpath, img)
            if os.path.isfile(exportpath):
                print("Successfully saved! - ", exportpath)
            else:
                print("Failed to save! - ", exportpath)
                successful = False
        else:
            print("\n",filename, "skipped - not an image file")
            
def convert_images_ask():
    clearscreen()
    allowLooping = False
    
    importpath = input("File path of import images: ")
    importfiletype = os.path.splitext(os.path.basename(importpath))[1]
    finalimportfiletype = importfiletype.lower()
    
    print("\nThe imported image file type is:", finalimportfiletype,". What is the file type you want to export these images as?")
    print("")
    print("(1) - .jpg")
    print("(2) - .png")
    print("(3) - .tif")
    print("(4) - .bmp")

    filetype_to = int(input(""))

    if(filetype_to == 1):
        convertimage_to(importpath, "jpg")
    elif(filetype_to == 2):
        convertimage_to(importpath, "png")
    elif(filetype_to == 3):
        convertimage_to(importpath, "tif")
    elif(filetype_to == 4):
        convertimage_to(importpath, "bmp")
    else:
        convert_images_ask()

    ask_for_looping(True, successful)
    
def create_roughnessmap(image_original, final_image): #Roughness map generation
    allowLooping = False
    print("Opening image...")
    img = Image.open(image_original)
    print("Turning image into array...")
    img = img.convert('L')
    img_arr = np.asarray(img)
    print("Applying filter...")
    roughness = np.zeros_like(img_arr, dtype=np.float32)
    height, width = img_arr.shape
    for y in range(height):
        for x in range(width):
            values = []
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    value = img_arr[(y+dy)%height, (x+dx)%width]
                    values.append(value)
            std_dev = np.std(values)
            roughness[y, x] = std_dev
    print("Converting the texture...")
    roughness /= np.max(roughness)
    out_img = Image.fromarray((roughness * 255).astype(np.uint8))
    print("Saving the final result texture...")
    out_img.save(final_image)
    print("Saved!")
    ask_for_looping(True, True)
    
def create_metallicmap(image_original, final_image): #Metallic map generation
    allowLooping = False
    contrast_input = input("Contrast (empty - default): ")
    contrast = 255
    if(contrast_input=="" or contrast_input==" "):
        contrast = 255
    else:
        contrast = int(contrast_input)
    print(" ")
    print("Opening image...")
    img = Image.open(image_original)
    img = img.convert('L')
    print("Turning image into array...")
    img_arr = np.asarray(img)
    print("Applying filters...")
    metallic = np.zeros_like(img_arr, dtype=np.float32)
    height, width = img_arr.shape
    for y in range(height):
        for x in range(width):
            values = []
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    value = img_arr[(y+dy)%height, (x+dx)%width]
                    values.append(value)
            avg_brightness = np.mean(values)
            metallic[y, x] = 1.0 - avg_brightness / contrast
    print("Converting the texture...")
    metallic /= np.max(metallic)
    out_img = Image.fromarray((metallic * contrast).astype(np.uint8))
    print("Saving the image...")
    out_img.save(final_image)
    print("Saved!")
    ask_for_looping(True, True)

def create_displacementmap(image_original, final_image, filetype): #Displacement map generation
    allowLooping = False
    print("Loading image...")
    img = cv2.imread(image_original, cv2.IMREAD_GRAYSCALE)
    noise = np.zeros_like(img, dtype=np.float32)
    freq = 64
    octaves = 3
    for i in range(octaves):
        freq /= 2
        noise += (cv2.resize(np.random.randn(int(img.shape[0]//freq), int(img.shape[1]//freq)), img.shape[::-1], interpolation=cv2.INTER_LINEAR) * 128).astype(int)
    noise = noise / np.max(np.abs(noise))
    print("Turning image into array...")
    x_disp, y_disp = np.meshgrid(np.arange(img.shape[1]), np.arange(img.shape[0]))
    x_disp = (x_disp.astype(np.float32) / img.shape[1] - 0.5) * 2
    y_disp = (y_disp.astype(np.float32) / img.shape[0] - 0.5) * 2
    x_disp += noise * 0.1
    y_disp += noise * 0.1
    disp_map = np.dstack((x_disp, y_disp))
    disp_map = cv2.GaussianBlur(disp_map, (5,5), 0)
    x_disp, y_disp = np.dsplit(disp_map, 2)
    print("Converting the image to grayscale...")
    x_disp = (x_disp - np.min(x_disp)) / (np.max(x_disp) - np.min(x_disp)) * 2 - 1
    y_disp = (y_disp - np.min(y_disp)) / (np.max(y_disp) - np.min(y_disp)) * 2 - 1
    cv2.imwrite('x_disp' + filetype, ((x_disp + 1) * 128).astype(np.uint8))
    cv2.imwrite('y_disp' + filetype, ((y_disp + 1) * 128).astype(np.uint8))
    x_disp = cv2.imread('x_disp' + filetype, cv2.IMREAD_GRAYSCALE)
    y_disp = cv2.imread('y_disp' + filetype, cv2.IMREAD_GRAYSCALE)
    disp_map = cv2.resize(noise, img.shape[::-1], interpolation=cv2.INTER_LINEAR)
    print("Converting texture...")
    disp_map = (disp_map + img.astype(np.float32)).clip(0, 255).astype(np.uint8)
    disp_map = cv2.cvtColor(disp_map, cv2.COLOR_GRAY2BGR)
    print("Saving image...")
    cv2.imwrite(final_image, disp_map)
    print("Saved!")
    x_removefile = "x_disp" + filetype
    y_removefile = "y_disp" + filetype
    if(os.remove(x_removefile)):
        successful = True
    elif(os.remove(y_removefile)):
        successful = True
    else:
        successful = False
    print("Successfully removed unnecessary generated files! (",x_removefile,")(",y_removefile,").")
    ask_for_looping(True, successful)

def create_opacitymap(image_original, final_image): #Opacity map generation
    allowLooping = False
    print("Loading image...")
    img = cv2.imread(image_original)
    print("Turning image into array...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print("Applying binary filter...")
    mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    opacity = cv2.bitwise_not(mask)
    print("Saving image...")
    cv2.imwrite(final_image, opacity)
    print("Saved!")
    ask_for_looping(True, True)
    
def create_bumpmap(image_original, final_image): #Bump map generation
    allowLooping = False
    print("Loading image...")
    img = cv2.imread(image_original)
    print("Turning image into array...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print("Applying filters to texture...")
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
    norm = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
    norm = cv2.normalize(norm, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    print("Saving image...")
    cv2.imwrite(final_image, norm)
    print("Saved!")
    ask_for_looping(True, True)
    
def retrieve_nextname(image_original, typeofname): #Generate the map file name, preserving the file type, just adding a name of the map at the end of it
    clearscreen()
    filename = os.path.splitext(os.path.basename(image_original))[0]
    filetype = os.path.splitext(os.path.basename(image_original))[1]
    final_name = filename.replace(filetype, "")
    if(typeofname == "metallic"):
        final_name += "_metallic"
        final_name += filetype
        print("\nCreating metallic map from provided file:", final_name, ".\nPlease wait and be patient, as this could take a few seconds...\n")
        create_metallicmap(image_original, final_name)
    elif(typeofname == "roughness"):
        final_name += "_roughness"
        final_name += filetype
        print("\nCreating roughness map from provided file:", final_name, ".\nPlease wait and be patient, as this could take a few seconds...\n")
        create_roughnessmap(image_original, final_name)
    elif(typeofname == "displacement"):
        final_name += "_displacement"
        final_name += filetype
        print("\nCreating displacement map from provided file:", final_name, ".\nPlease wait and be patient, as this could take a few seconds...\n")
        create_displacementmap(image_original, final_name, filetype)
    elif(typeofname == "opacity"):
        final_name += "_opacity"
        final_name += filetype
        print("\nCreating opacity map from provided file:", final_name, ".\nPlease wait and be patient, as this could take a few seconds...\n")
        create_opacitymap(image_original, final_name)
    elif(typeofname == "bump"):
        final_name += "_bump"
        final_name += filetype
        print("\nCreating bump map from provided file:", final_name, ".\nPlease wait and be patient, as this could take a few seconds...\n")
        create_bumpmap(image_original, final_name)
        
def ask_for_looping(left_from_generation, sucessful):
    if(left_from_generation and sucessful):
        print("\n|---------------------------------------------------------------------------|")
        print("|                     Generation of the map was sucessful!                  |")
        print("|    Do you wish to continue generating more maps, or to exit the program?  |")
        print("|                            (1) - Exit program                             |")
        print("|                            (2) - Continue                                 |")
        print("|---------------------------------------------------------------------------|")
    elif(not sucessful):
        print("\n|---------------------------------------------------------------------------|")
        print("|                   Generation of the map was unsucessful!                  |")
        print("|    Do you wish to continue generating more maps, or to exit the program?  |")
        print("|                            (1) - Exit program                             |")
        print("|                            (2) - Continue                                 |")
        print("|---------------------------------------------------------------------------|")
    else:
        print("\n|---------------------------------------------------------------------------|")
        print("|    Do you wish to continue generating more maps, or to exit the program?  |")
        print("|                            (1) - Exit program                             |")
        print("|                            (2) - Continue                                 |")
        print("|---------------------------------------------------------------------------|")
    loop_choice = int(input(""))
    if(loop_choice == 1): # If person enters 1, stop looping and exit program
        allowLooping = False
        exit()
    elif(loop_choice == 2): #Else, continue looping
        allowLooping = True
        looping()
    else:
        if(left_from_generation):
            looping()
        elif(not left_from_generation):
            helpscreen()
def looping(): #This part loops the whole time while creating the file
    clearscreen()
    print("|------------------------------------------------------|")
    print("|                                                      |")
    print("|                  img2map.exe v1.6                    |")
    print("|       A tool for generating simple texture maps      |")
    print("|            Created by Luka Beg (c) 2023              |")
    print("|              For Personal Use Only!                  |")
    print("|                                                      |")
    print("|------------------------------------------------------|\n")
    print("(1) - Convert Image to Roughness map")
    print("(2) - Convert Image to Metallic map")
    print("(3) - Convert Image to Displacement map")
    print("(4) - Convert Image to Opacity map")
    print("(5) - Convert Image to Bump map")
    print("(6) - Image Type Conversion")
    print("(7) - Help")
    print("\n")
    mode = int(input("Mode: ")) #Inputs the mode
    if(mode == 1): #Mode #1 -> Roughness map generator
        retrieve_nextname(input(r"File Path: "), "roughness")
    elif(mode == 2): #Mode #2 -> Metallic map generator
        retrieve_nextname(input(r"File Path: "), "metallic")
    elif(mode == 3): #Mode #3 -> Displacement map generator
        retrieve_nextname(input(r"File Path: "), "displacement")
    elif(mode == 4): #Mode #4 -> Opacity map generator
        retrieve_nextname(input(r"File Path: "), "opacity")
    elif(mode == 5): #Mode #5 -> Bump map generator
        retrieve_nextname(input(r"File Path: "), "bump")
    elif(mode == 6): #Mode #6 -> Image file converter
        convert_images_ask()
    elif(mode == 7): #Mode #7 -> Help screen
        helpscreen()
    else: #Any number over or under 1-3 are invalid, so print error
        looping()
looping() #To jumpstart the program
