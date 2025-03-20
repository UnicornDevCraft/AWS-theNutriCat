# Standard library imports
import os
import time
import shutil
import mimetypes

# Third-party imports
import requests
import psycopg2
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, BotoCoreError
from PIL import Image
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

# Local application imports
from app import create_app
from app.db import db
from app.models import Recipe, RecipeIngredient, Ingredient


# -------------------------------
# DATABASE FUNCTIONS
# -------------------------------

def get_recipe_by_id(recipe_id):
    """
    Gets a single recipe by its ID from the database.
    
    :param recipe_id: an ID of a recipe from the database
    :return recipe_data: The recipe data (id, title, path to an image, ingredients) or None if an error occurred
    """

    # Validate input
    if not isinstance(recipe_id, int) or recipe_id <= 0:
        print(f"Invalid recipe ID: {recipe_id}")
        return None

    try:
        # Fetch recipe data with joins
        recipe = (
            db.session.query(Recipe.id, Recipe.title, Recipe.image_path, Ingredient.name)
            .join(RecipeIngredient, Recipe.id == RecipeIngredient.recipe_id)
            .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
            .filter(Recipe.id == recipe_id)
            .all()
        )

        if not recipe:
            print(f"No recipe found for ID {recipe_id}")
            return None

        # Extract recipe details
        recipe_data = {
            "id": recipe[0][0],
            "title": recipe[0][1].capitalize(),
            "image_path": recipe[0][2] or "No image available",
            "ingredients": [ingredient.lower() for _, _, _, ingredient in recipe]
        }

        return recipe_data

    except SQLAlchemyError as e:
        print(f"Database error while fetching recipe {recipe_id}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in get_recipe_by_id({recipe_id}): {e}")
        return None

def check_public_URL_in_db(recipe_id):
    """
    Gets a public URL from the database.
    
    :param recipe_id: an ID of a recipe from the database
    :return boolean: True if found URL in the database or False if an error occurred
    """

    # Validate input
    if not isinstance(recipe_id, int) or recipe_id <= 0:
        print(f"Invalid recipe ID: {recipe_id}")
        return None

    try:
        # Fetch public URL from the database
        URL_in_db = (
            db.session.query(Recipe.public_URL).filter(Recipe.id == recipe_id).first()
        )

        if not URL_in_db:
            print(f"No previous URL found for ID {recipe_id}")
            return True
        else:
            print(f"The public URL for the recipe with ID {recipe_id} already exists! {URL_in_db}")
            return False

    except SQLAlchemyError as e:
        print(f"Database error while fetching recipe {recipe_id}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in get_recipe_by_id({recipe_id}): {e}")
        return None

def update_recipe_table(recipe_id, public_URL):
    """
    Updates a public URL from the database.
    
    :param recipe_id: an ID of a recipe from the database
    :param public_URL: a public URL generated after uploading to the S3 bucket
    :return boolean: True if successfully updated the table or None if an error occurred
    """

    # Validate input
    if not isinstance(recipe_id, int) or recipe_id <= 0:
        print(f"Invalid recipe ID: {recipe_id}")
        return None
    
    if not isinstance(public_URL, str) or not public_URL.startswith("http"):
        print(f"Invalid URL provided: {public_URL}")
        return None

    try:
        # Fetch the recipe from the database
        recipe = db.session.query(Recipe).filter(Recipe.id == recipe_id).first()

        if not recipe:
            print(f"Recipe with ID {recipe_id} not found.")
            return False

        # Update the image path (URL)
        recipe.image_path = public_URL
        db.session.commit()

        print(f"Recipe ID {recipe_id} successfully updated with new image URL.")
        return True

    except SQLAlchemyError as e:
        print(f"Database error while updating recipe {recipe_id}: {e}")
        db.session.rollback()  # Rollback in case of error
        return None
    except Exception as e:
        print(f"Unexpected error in update_recipe_table({recipe_id}): {e}")
        return None

# -------------------------------
# IMAGE GENERATION FUNCTIONS
# -------------------------------

def ask_for_recipe_id():
    """ 
    Prompts user for the recipe id to generate an image.

    :return recipe_id: The id recipe of the recipe that user entered 
    """

    while True:
        try:
            recipe_id = int(input("Let's generate some images! Please enter recipe ID to start: "))
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
    return recipe_id

def generate_prompt(recipe):
    """
    Creates an AI image generation prompt based on a recipe data.
    
    :param recipe: a dictionary with the recipe data
    :return recipe_data: The prompt for API request with the recipe data or None if an error occurred
    """

    if not recipe:
        return None

    return (
        f"A mouthwatering and detailed photo of '{recipe['title']}' made with these ingredients: "
        f"{', '.join(recipe['ingredients'])}. Served like in a top-notch restaurant on a designer plate. "
        f"Please add a textured wall background to match the color palette of the dish, fresh fruits and "
        f"vegetables, and cookware to create a fresh homemade atmosphere."
    )

def generate_recipe_image(recipe, prompt, max_retries=3):
    """
    Send request to DeepAI and download the image if successful.

    :param recipe: a dictionary with the recipe data
    :param prompt: a string with the data for API request
    :param max_retries: an integer quantity of tries if API request fails
    :return image_url: The URL to download generated by DeepAI image or None if an error occurred
    """
    
    for attempt in range(max_retries):
        try:
            # Make API request
            response = requests.post(URL, data={
                "text": prompt, 
                "width": "1216", 
                "height": "832",
                "image_generator_version": "hd"
                }, 
                headers={"api-key": API_KEY}, timeout=10)

            # Check response
            if response.status_code == 200:
                result = response.json()
                image_url = result.get("output_url")
                if image_url:
                    return image_url
                else:
                    print(f"⚠️ No image URL in response for {recipe['title']}. Retrying...")
            else:
                print(f"❌ API Error for {recipe['title']}: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network error on attempt {attempt + 1}: {e}")

        time.sleep(5)  # Small delay before retrying
    
    print(f"🚨 Failed to generate image for {recipe['title']} after {max_retries} attempts.")
    return None

def download_image(image_url, recipe, image_directory):
    """
    Downloads an image and saves it to the local folder
    
    :param image_url: The URL to download generated by DeepAI image
    :param recipe: a dictionary with the recipe data
    :param image_directory: the path where to save generated by DeepAI image
    :return filepath: the full path to the image including filename or None if an error occurred
    """

    try:
        response = requests.get(image_url, stream=True, timeout=10)
        if response.status_code == 200:
            # Create a valid filename
            filename = f"{recipe['title'].replace(' ', '_').lower()}.jpg"
            filepath = os.path.join(image_directory, filename)

            # Save the image
            with open(filepath, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            print(f"✅ Image saved: {filepath}")
            return filepath
        else:
            print(f"❌ Failed to download image: {image_url}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error downloading image: {e}")
    
    return None

def enhance_image(file_path, recipe, max_retries=3):
    """
    Enhances an image using DeepAI's Image Editor API
    
    :param file_path: the full path to the image including filename
    :param recipe: a dictionary with the recipe data
    :param max_retries: an integer quantity of tries if API request fails
    :return image_url: The URL to download enhanced by DeepAI image or None if an error occurred
    """

    for attempt in range(max_retries):
        try: 
            with open(file_path, "rb") as image_file:
                # Make API request
                response = requests.post(
                    ENHANCE_URL,
                    files={"image": image_file},
                    headers={"api-key": API_KEY},
                )
    
            # Check response
            if response.status_code == 200:
                result = response.json()
                image_url = result.get("output_url")
                if image_url:
                    return image_url
                else:
                    print(f"⚠️ No image URL in response for enhancing {recipe['title']}. Retrying...")
            else:
                print(f"❌ API Error for enhancing {recipe['title']}: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network error on enhancing attempt {attempt + 1}: {e}")

        time.sleep(5)  # Small delay before retrying
    
    print(f"🚨 Failed to enhance image for {recipe['title']} after {max_retries} attempts.")

    return None

# -------------------------------
# IMAGE PROCESSING FUNCTIONS
# -------------------------------

def image_exists_local(folder_path, filename):
    """
    Checks wether the image exists localy in a static folder
    
    :param folder_path: a path to the local folder app/static/img/recipes
    :param filename: a name of the image to check for
    :return boolean: True if the image already exists in the folder or None if it does not
    """

    return os.path.exists(os.path.join(folder_path, filename))

def crop_center(image, width, height):
    """
    Crops an image to the specified width and height from the center.
    
    :param image: PIL Image object
    :param width: Desired crop width
    :param height: Desired crop height
    :return: Cropped Image object or None if an error occurs
    """

    try:
        # Validate input types
        if not isinstance(image, Image.Image):
            raise TypeError("Invalid image type. Expected a PIL Image object.")
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError("Width and height must be integers.")
        
        # Get image size
        img_width, img_height = image.size

        # Ensure the requested crop size is not larger than the image itself
        if width > img_width or height > img_height:
            raise ValueError(
                f"Crop size ({width}x{height}) is larger than image size ({img_width}x{img_height})."
            )

        # Calculate crop box
        left = (img_width - width) // 2
        top = (img_height - height) // 2
        right = left + width
        bottom = top + height

        # Perform cropping
        return image.crop((left, top, right, bottom))

    except Exception as e:
        print(f"Error cropping image: {e}")
        return None

def save_image_object(image, folder_path, image_name, format):
    """
    Saves a PIL Image object to the specified folder and returns the full path.

    :param image: PIL Image object to save
    :param folder_path: Path to the folder where the image should be saved
    :param image_name: Name of the saved image file (including extension)
    :param format: Image format (default: PNG)
    :return: Full path to the saved image or None if an error occurs
    """
    try:
        # Validate input types
        if not isinstance(image, Image.Image):
            raise TypeError("Invalid image type. Expected a PIL Image object.")
        if not isinstance(folder_path, str) or not isinstance(image_name, str):
            raise TypeError("Folder path and image name must be strings.")
        if not isinstance(format, str):
            raise TypeError("Format must be a string.")

        # Ensure folder exists, create it if necessary
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Construct the full path
        full_path = os.path.join(folder_path, image_name)

        # Validate format
        valid_formats = ["PNG", "JPEG", "JPG", "BMP", "GIF", "TIFF", "WEBP"]
        if format.upper() not in valid_formats:
            raise ValueError(f"Invalid format '{format}'. Choose from {valid_formats}.")

        # Save the image
        image.save(full_path, format=format.upper())

        print(f"Image successfully saved at: {full_path}")
        return full_path

    except Exception as e:
        print(f"Error saving image: {e}")
        return None
    
def open_in_vscode(file_path):
    """
    Opens an image or any file in VS Code.

    :param file_path: Path to the local file
    """
    try:
        # Validate input type
        if not isinstance(file_path, str):
            raise TypeError("Invalid file path. Expected a string.")

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check if VS Code is installed
        if not shutil.which("code"):
            raise EnvironmentError("VS Code is not installed or not added to system PATH.")

        # Open the file in VS Code
        os.system(f"code \"{file_path}\"")
        print(f"Opened {file_path} in VS Code.")

    except Exception as e:
        print(f"Error opening file in VS Code: {e}")

def delete_file(file_path):
    """
    Deletes a file from the system.

    :param file_path: Path to the local file
    """
    try:
        # Validate input type
        if not isinstance(file_path, str):
            raise TypeError("Invalid file path. Expected a string.")

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Delete the file
        os.remove(file_path)
        print(f"✅ Successfully deleted: {file_path}")

    except PermissionError:
        print(f"❌ Permission denied: Cannot delete {file_path}. Try running as an administrator.")
    except Exception as e:
        print(f"❌ Error deleting file: {e}")

def upload_to_S3(file_path, s3_folder="recipe_images/"):
    """
    Uploads a file to an S3 bucket.

    :param file_path: Path to the local file
    :param s3_folder: Folder (prefix) in S3 where the file should be stored
    :return: The public URL of the uploaded file or None if an error occurred
    """
    try:
        # Validate input type
        if not isinstance(file_path, str):
            raise TypeError("Invalid file path. Expected a string.")

        # Ensure the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Extract file name and detect MIME type
        file_name = os.path.basename(file_path)
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or "application/octet-stream"

        # Initialize S3 client
        s3 = boto3.client("s3", region_name=AWS_REGION)

        # Upload file
        s3.upload_file(
            file_path,
            S3_BUCKET_NAME,
            f"{s3_folder}{file_name}",
            ExtraArgs={"ContentType": content_type},
        )

        # Construct file URL
        file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_folder}{file_name}"
        print(f"✅ Upload successful! File URL: {file_url}")
        return file_url

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except TypeError as e:
        print(f"❌ Error: {e}")
    except NoCredentialsError:
        print("❌ Error: AWS credentials not found. Please configure them using AWS CLI or environment variables.")
    except PartialCredentialsError:
        print("❌ Error: Incomplete AWS credentials. Double-check your AWS access and secret keys.")
    except BotoCoreError as e:
        print(f"❌ AWS Boto3 error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    return None

# -------------------------------
# MAIN EXECUTION
# -------------------------------

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    API_KEY = os.getenv("DEEPAI_API_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
    URL = "https://api.deepai.org/api/text2img"
    ENHANCE_URL = "https://api.deepai.org/api/torch-srgan"

    # Ensure the temporary image storage directories exist
    GEN_IMAGE_DIR = "gen_recipe_images"
    os.makedirs(GEN_IMAGE_DIR, exist_ok=True)
    ENH_IMAGE_DIR = "enh_recipe_images"
    os.makedirs(ENH_IMAGE_DIR, exist_ok=True)
    BASE_DIR = "/home/ubuntu/AWS-theNutriCat/"

    # Local storage
    folder_path = f"{BASE_DIR}app/static/img/recipes/"

    # Setting final image dimentions
    img_width = 3065
    img_height = 1725

    # Initialize the Flask app without running it
    app = create_app()

    # Push application context
    with app.app_context():
        while True:
            # Asking user for the recipe ID
            recipe_id = ask_for_recipe_id()
            try:
                print(f'Fetching data for recipe with ID {recipe_id}...')
                recipe = get_recipe_by_id(recipe_id)
                if recipe:
                    image_name = recipe['image_path']
                    # Check if the image for the recipe with such id exists LOCALY
                    if image_exists_local(folder_path, image_name):
                        print(f'Image for {recipe['title']} already exists localy! Please try again...')
                        continue
                    else:
                        # Generate an image using DeepAI API
                        image_url = generate_recipe_image(recipe, generate_prompt(recipe))
                        if image_url:
                            gen_image_path = f"{BASE_DIR}{download_image(image_url, recipe, GEN_IMAGE_DIR)}"
                            # Enhance generated image
                            enhanced_img_url = enhance_image(gen_image_path, recipe)
                            if enhanced_img_url:
                                enhanced_img_path = f"{BASE_DIR}{download_image(enhanced_img_url, recipe, ENH_IMAGE_DIR)}"
                                # Crop enhanced image
                                try:
                                    cropped_img = crop_center(Image.open(enhanced_img_path), img_width, img_height)
                                    if cropped_img:
                                        cropped_image_path = save_image_object(cropped_img, folder_path, image_name, 'PNG')
                                        open_in_vscode(cropped_image_path)
                                        # Check the image and proceed as needed
                                        user_ok = input("Are you satisfied with the image? (Y/N)  ")
                                        if user_ok.lower() == 'y':
                                            # Upload to S3 bucket
                                            public_URL = upload_to_S3(cropped_image_path)
                                            # Check database for public URL of the recipe
                                            if check_public_URL_in_db(recipe_id):
                                                # Update the Recipes table
                                                update_recipe_table(recipe_id, public_URL)
                                            else:
                                                user_update = input("Do you want to update the link? (Y/N)  ")
                                                if user_update.lower() == 'y':
                                                    # Update the Recipes table
                                                    update_recipe_table(recipe_id, public_URL)
                                                elif user_update.lower() == 'n':
                                                    print("The link was not updated!!!")
                                                else:
                                                    print("I continue without updating the link, you can do it manually...")
                                            # Ask user before deleting generated images
                                            user_del = input("Do you want to delete copies? (Y/N)")
                                            if user_del.lower() == 'y':
                                                delete_file(gen_image_path)
                                                delete_file(enhanced_img_path)
                                                user_cont = input("Do you like to continue generating images? (Y/N)  ")
                                                if user_cont.lower() == 'y':
                                                    recipe_id += 1
                                                    continue
                                                elif user_cont.lower() == 'n':
                                                    print("Thank you! Bye :)")
                                                    break
                                                else:
                                                    print("You can try again or something else...")
                                                    break
                                            elif user_del.lower() == 'n':
                                                print("It seems you'll need to adjust manually. Exitting..")
                                                break
                                            else:
                                                print("You can try again or simply something else...")
                                                break
                                        elif user_ok.lower() == 'n':
                                            user_retry = input("Do you want to delete copies and regenerate images? (Y/N)")
                                            delete_file(gen_image_path)
                                            delete_file(enhanced_img_path)
                                            delete_file(cropped_image_path)
                                            continue
                                        else:
                                            print("That's all! Good luck :)")
                                            break
                                except FileNotFoundError:
                                    print("Error: Image file not found.")
                                        
                else:
                    print("Recipe not found.")
            except FileNotFoundError as e:
                print(f"File not found: {e}")
            except OSError as e:
                print(f"File operation error: {e}")
            except requests.RequestException as e:
                print(f"API request failed: {e}")
            except (SQLAlchemyError, psycopg2.DatabaseError) as e:
                print(f"Database error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")