# Standard library imports
import re

# Third-party imports
from sqlalchemy.exc import IntegrityError
from attrdict import AttrDict

# Local application imports
from app.db import db
from app.models import Recipe, RecipeIngredient, Ingredient, Tag, RecipeTag, Instruction
           

# -------------------------------
# DATABASE FUNCTIONS
# -------------------------------

def add_recipe_to_db(recipes):
    """ 
    Extracts recipe components from a list of recipe dictionaries and writes them into a database.

    :param: recipes (list): A list of recipe dictionaries.
    :returns: messages (list): Info messages.
    """
    messages = []
    
    for recipe in recipes:
        try:
            local_image_path = create_filename(recipe.name)
            new_recipe = Recipe(
                title=recipe.name,
                prep_time=recipe.prep_time,
                cook_time=recipe.cook_time,
                local_image_path=local_image_path,
                servings=recipe.servings
            )

            db.add(new_recipe)
            db.commit()
            db.refresh(new_recipe)
            messages.append(f"Recipe '{recipe.name}' added successfully.")
        except IntegrityError:
            db.rollback()
            messages.append(f"Recipe '{recipe.name}' already exists.")
        except Exception as e:
            db.rollback()
            messages.append(f"Error adding '{recipe.name}': {e}")

    return messages

def add_tags_to_recipe(recipes):
    """ 
    Extracts tags from a list of recipe dictionaries and writes them into a database.

    :param: recipes (list): A list of recipe dictionaries.
    :returns: messages (list): Info messages.
    """
    messages = []

    for recipe in recipes:
        recipe_entry = db.query(Recipe).filter(Recipe.title.ilike(recipe.name)).first()
        if not recipe_entry:
            messages.append(f"No recipe found: {recipe.name}")
            continue

        tag_names = [recipe.meal_type, recipe.day_of_week, recipe.menu_name]
        for tag_name in tag_names:
            tag_entry = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag_entry:
                messages.append(f"Tag '{tag_name}' not found.")
                continue

            existing_tag = db.query(RecipeTag).filter(
                RecipeTag.recipe_id == recipe_entry.id,
                RecipeTag.tag_id == tag_entry.id
            ).first()

            if not existing_tag:
                new_recipe_tag = RecipeTag(recipe_id=recipe_entry.id, tag_id=tag_entry.id)
                db.add(new_recipe_tag)
        
        db.commit()
        messages.append(f"Tags added for '{recipe.name}'.")

    return messages

def add_ingredients_to_db(ingredients):
    """ 
    Writes ingredients to the database.

    :param: ingredients (list): A list of recipe objects.
    :returns: messages (list): Info messages.
    """
    messages = []

    for ingredient in ingredients:
        recipe_entry = db.query(Recipe).filter(Recipe.title.ilike(ingredient.for_recipe)).first()
        if not recipe_entry:
            messages.append(f"Recipe not found: {ingredient.for_recipe}")
            continue

        ingredient_entry = db.query(Ingredient).filter(Ingredient.name == ingredient.name).first()
        if not ingredient_entry:
            ingredient_entry = Ingredient(name=ingredient.name)
            db.add(ingredient_entry)
            db.commit()
            db.refresh(ingredient_entry)

        new_recipe_ingredient = RecipeIngredient(
            recipe_id=recipe_entry.id,
            ingredient_id=ingredient_entry.id,
            quantity=ingredient.quantity,
            unit=ingredient.unit,
            quantity_notes=ingredient.quantity_notes,
            ingredient_notes=ingredient.ingredient_notes
        )

        db.add(new_recipe_ingredient)
        db.commit()
        messages.append(f"Added ingredient '{ingredient.name}' to recipe '{ingredient.for_recipe}'.")

    return messages

def instructions_to_db(recipes):
    """ 
    Extracts recipe instructions from a list of recipe dictionaries and writes them to the database.

    :param: recipes (list): A list of recipe dictionaries.
    :returns: messages (list): Info messages.
    """
    messages = []

    for recipe in recipes:
        recipe_entry = db.query(Recipe).filter(Recipe.title.ilike(recipe.name)).first()
        if not recipe_entry:
            messages.append(f"No recipe found: {recipe.name}")
            continue

        for step in recipe.instructions:
            step_number = int(step[0])
            description = step[3:]
            
            existing_step = db.query(Instruction).filter(
                Instruction.recipe_id == recipe_entry.id,
                Instruction.step_number == step_number
            ).first()
            
            if not existing_step:
                new_instruction = Instruction(
                    recipe_id=recipe_entry.id,
                    step_number=step_number,
                    instruction=description
                )
                db.add(new_instruction)

        db.commit()
        messages.append(f"Instructions added for '{recipe.name}'.")

    return messages

# -------------------------------
# FILE MANIPULATION FUNCTIONS
# -------------------------------

def create_filename(recipe_name):
    """ 
    Creates an image filename out of recipe name.

    :param: recipe_name (str): The recipe name.
    :returns: filename (str): A proper filename for the image.
    """

    filename = re.sub(r'[^a-z0-9_]', '', recipe_name.lower().replace(" ", "_")) + ".png"
    
    return filename

def extract_recipes(file_path):
    """ 
    Extract recipes from the text file and store them in a list.

    :param: file_path (str): Path to the text file.
    :returns: extracted_recipes: A list of dictionaries with recipe data.
    """
    extracted_recipes = []

    # Open and process recipe text file
    with open(file_path, 'r', encoding='utf-8') as file:
        sections = file.read().split('---')
        for section in sections[1:]:
            parts = section.split('\n\n')
            # Check if servings information exists
            servings_match = re.search(r'\(for (\d+) servings\)', parts[5])
            # Create a dictionary with the recipe data from the file
            create_recipe = AttrDict({
                "language": file_path.split("\\")[3],
                "title": parts[2].strip(),
                "ingredients": [item.strip() for item in parts[5].split('\n') if "INGREDIENTS:" not in item],
                "instructions": [step.strip() for step in parts[6].split('\n') if "INSTRUCTIONS:" not in step],
                "prep_time": parts[3].split(':')[1].strip(),
                "cook_time": parts[4].split(':')[1].strip(),
                "meal_type": parts[1].split(':')[1].strip().capitalize(),
                "day_of_week": parts[1].split(':')[0].strip().capitalize(),
                "menu_name": file_path.split("\\")[4].split("_")[0].capitalize(),
                "servings": int(servings_match.group(1)) if servings_match else 1 
                })

            extracted_recipes.append(create_recipe)

    return extracted_recipes

def extract_ingredients(recipes):
    """ 
    Extracts recipe ingredients from a list of recipe dictionaries and returns a list of ingredient dictionaries.

    :param: recipes (list): A list of recipe dictionaries.
    :returns: ingredients (list): A list of ingredient dictionaries.
    """

    ingredients = []
    for recipe in recipes:
        for item in recipe.ingredients:
            if "—" in item:
                ingredient = item.split("—")[0].strip()
                quantity_info = item.split("—")[1].strip()
                quantity_note = None
                ingredient_note = None

                if "to" in quantity_info:
                    quantity_note = quantity_info
                    quantity = None
                    unit = None
                else:
                    quantity = quantity_info.split()[0].strip()
                    unit = quantity_info.split()[1].strip()

                if "(" in ingredient:
                    ingredient_name = ingredient.split("(")[0].strip()
                    ingredient_note = "(" + ingredient.split("(")[1].strip()
                else:
                    ingredient_name = ingredient

                create_ingredient = AttrDict({
                    "name" : ingredient_name,
                    "for_recipe" : recipe.name,
                    "ingredient_notes" : ingredient_note,
                    "quantity_notes" : quantity_note,
                    "quantity" : quantity,
                    "unit" : unit
                })
                ingredients.append(create_ingredient)
            else:
                print(f"Attention!!!!!! Strange item: {item} !!!!!!")
            
    return ingredients

# -------------------------------
# MAIN EXECUTION
# -------------------------------

if __name__ == "__main__":
    """ 
        Please carefully adjust the full paths before each use!

    """

    # Set up path to the menu text file
    file_path = "/home/ubuntu/AWS-theNutriCat/cleaned_up_recipes/en/summer_menu_en.txt" 

    recipes = extract_recipes(file_path)
    #add_recipe_to_db(recipes)
    #add_tags_to_recipe(recipes)
    #add_ingredients_to_db(extract_ingredients(recipes))
    #instructions_to_db(recipes)



        

