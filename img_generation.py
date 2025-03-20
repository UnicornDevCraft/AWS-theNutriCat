import os
import time
import requests
import psycopg2
from PIL import Image
from dotenv import load_dotenv
from app import create_app
from app.db import db
from app.models import Recipe, RecipeIngredient, Ingredient
from sqlalchemy.exc import SQLAlchemyError



# -------------------------------
# DATABASE FUNCTIONS
# -------------------------------

def get_recipe_by_id(recipe_id):
    """Gets a single recipe by its ID from the database"""
    recipe = (
        db.session.query(Recipe.id, Recipe.title, Recipe.image_path, Ingredient.name)
        .join(RecipeIngredient, Recipe.id == RecipeIngredient.recipe_id)
        .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
        .filter(Recipe.id == recipe_id)
        .all()
    )

    if not recipe:
        return None

    recipe_data = {
        "id": recipe[0][0],
        "title": recipe[0][1].capitalize(),
        "image_path": recipe[0][2],
        "ingredients": [],
    }

    for _, _, _, ingredient in recipe:
        recipe_data["ingredients"].append(ingredient.lower())

    return recipe_data

# -------------------------------
# IMAGE GENERATION FUNCTIONS
# -------------------------------

def ask_for_recipe_id():
    """ Ask user for the recipe id to generate an image """
    while True:
        try:
            recipe_id = int(input("Let's generate some images! Please enter recipe ID to start: "))
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
    return recipe_id

def generate_prompt(recipe):
    """Creates an AI image generation prompt based on a recipe."""
    if not recipe:
        return None

    return (
        f"A mouthwatering and detailed photo of '{recipe['title']}' made with these ingredients: "
        f"{', '.join(recipe['ingredients'])}. Served like in a top-notch restaurant on a designer plate. "
        f"Please add a textured wall background to match the color palette of the dish, fresh fruits and "
        f"vegetables, and cookware to create a fresh homemade atmosphere."
    )

def generate_recipe_image(recipe, prompt, max_retries=3):
    """Send request to DeepAI and download the image if successful"""
    
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
    """Download image and save it to the local folder"""
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
    """Enhances an image using DeepAI's Image Editor API"""

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

def crop_center(image, width, height):
    """Crops an image to the specified width and height from the center. Takes an Image object as image."""
    img_width, img_height = image.size
    left = (img_width - width) // 2
    top = (img_height - height) // 2
    right = left + width
    bottom = top + height
    return image.crop((left, top, right, bottom))

def image_exists_local(folder_path, filename):
    """Checks wether the image exists localy in a static folder"""
    return os.path.exists(os.path.join(folder_path, filename))
    
def open_in_vscode(file_path):
    """Opens and shows an image to the user"""
    os.system(f"code {file_path}")

def save_image_object(image, folder_path, image_name, format):
    """Saves Image object to the specified folder and returns the full path to the image. """
    full_path = folder_path + image_name
    image.save(full_path, format=format)
    return full_path

def delete_file(file_path):
    """Delets file from the system. """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{file_path} has been deleted.")
    else:
        print("File not found.")

def save_to_S3(file_path):
    print(f"✅ Image successfully saved to the AWS storage! ")
    return None


# -------------------------------
# MAIN EXECUTION
# -------------------------------

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    API_KEY = os.getenv("DEEPAI_API_KEY")
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
        # Setting up a flag to start/continue generating images
        recipe_id = ask_for_recipe_id()

        while True:
            try:
                recipe = get_recipe_by_id(recipe_id)
                if recipe:
                    image_name = recipe['image_path']
                    # Check if the image for the recipe with such id exists LOCALY
                    if image_exists_local(folder_path, image_name):
                        print(f'Image for {recipe['title']} already exists localy!')
                        break
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
                                cropped_img = crop_center(Image.open(enhanced_img_path), img_width, img_height)
                                cropped_image_path = save_image_object(cropped_img, folder_path, image_name, 'PNG')
                                open_in_vscode(cropped_image_path)
                                # Check the image and proceed as needed
                                user_ok = input("Are you satisfied with the image? (Y/N)  ")
                                if user_ok.lower() == 'y':
                                    save_to_S3(cropped_image_path)
                                    user_del = input("Do you want to delete copies? (Y/N)")
                                    if user_del.lower() == 'y':
                                        delete_file(gen_image_path)
                                        delete_file(enhanced_img_path)
                                        user_cont = input("Do you like to continue generating images? (Y/N)")
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



