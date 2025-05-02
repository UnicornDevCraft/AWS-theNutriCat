from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import cv2
import os
import PyPDF2

def main():
    # Set the name of the pdf
    pdf_path = ('universal/universal_15-27.pdf')

    # Set the name of the file where to extract
    file_name = ('extracted/universal_menu.txt')

    # If file is big and given by parts
    if '-' in pdf_path:
        # Declare starting page
        starts_with = int(pdf_path.split('_')[1].split('-')[0])
    else:
        starts_with = 1

    # Counting pages
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        print(f'Total number of pages: {num_pages}.')

    # Cut out folder name
    folder_name = pdf_path.split('/')[0] + '/'
    print(f'In folder: {folder_name}')

    # Converting pdf to images
    pdf_to_image(pdf_path, folder_name, starts_with)

    # Converting images to grayscale
    for i in range(starts_with, num_pages + starts_with):
        convert_gray(f'page_{i}.png', folder_name)
        binarize(f'page_{i}.png', folder_name)
        text_extracted = text_extraction(f'binary_page_{i}.png', folder_name)
        write_to(file_name, text_extracted)
        # Clean up
        clean(f'binary_page_{i}.png', folder_name)
        clean(f'gray_page_{i}.png', folder_name)
        clean(f'page_{i}.png', folder_name)


# Writing to a file
def write_to(file, text):
    with open(file, 'a') as f:
        f.write(text)
    print(f'Successfuly written to a file {file}.')

# Cleaning
def clean(image_name, folder_name):
    image_path = folder_name + image_name
    if os.path.exists(image_path):
        os.remove(image_path)
        print(f'{image_path} has been deleted.')
    else: 
        print(f'{image_path} does not exist.')


# Convert pdf to images
def pdf_to_image(pdf_path, folder_name, start):
    images = convert_from_path(pdf_path)
    # Save each image
    for i, image in enumerate(images):
        image.save(f'{folder_name}page_{i+start}.png', 'PNG')

    print(f"Saved {len(images)} pages as images to {folder_name}.")


# Converting to grayscale
def convert_gray(img_name, folder_name):
    img = Image.open(f'{folder_name}{img_name}').convert('L')
    new_name = 'gray_' + img_name
    img.save(f'{folder_name}{new_name}')
    print(f'Converted to {new_name}.')


# Binarization 
def binarize(gray_img_name, folder_name):
    img = cv2.imread(f'{folder_name}{gray_img_name}', 0) # Load image in grayscale
    _, binary_img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
    cv2.imwrite(f'{folder_name}binary_{gray_img_name}', binary_img)
    print(f'Made a binary_{gray_img_name}')


# Extract text from image
def text_extraction(img_name, folder_name):
    img = Image.open(f'{folder_name}{img_name}')
    text = pytesseract.image_to_string(img, lang='rus')
    print(text)
    return text


main()