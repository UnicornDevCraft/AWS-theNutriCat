import re, sqlite3

# Defined class to store recipe
class Recipe:
    def __init__(self, language, name, ingredients, instructions, menu_name, servings=1, prep_time=0, cook_time=0, meal_type='any', day_of_week='any'):
        self.language = language
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions
        self.servings = servings
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.meal_type = meal_type
        self.day_of_week = day_of_week
        self.menu_name = menu_name

    def display(self):
        """Display recipe details."""
        print(f"Recipe Name: {self.name}")
        print(f"Language: {self.language}")
        print("Ingredients:")
        for item in self.ingredients:
            print(f" - {item}")
        print("Instructions:")
        for step in self.instructions:
            print(f" - {step}")
        print(f"Servings: {self.servings}")
        print(f"Prep Time: {self.prep_time}")
        print(f"Cook Time: {self.cook_time}\n")
        print(f"Meal Type: {self.meal_type}\n")
        print(f"Week Day: {self.day_of_week}\n")
        print(f"Menu Name: {self.menu_name}\n")

    def to_dict(self):
        """Convert recipe object to a dictionary."""
        return {
            "language": self.language,
            "name": self.name,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "servings": self.servings,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "meal_type": self.meal_type,
            "day_of_week": self.day_of_week,
            "menu_name": self.menu_name
        }

    def __str__(self):
        return f"{self.name}, {self.language}, {self.ingredients}, {self.instructions}, {self.servings}, {self.prep_time}, {self.cook_time}, {self.meal_type}, {self.day_of_week}, {self.menu_name}"

class Ingredient:
    def __init__(self, name, for_recipe, ingredient_notes, quantity_notes, quantity, unit):
        self.name = name
        self.for_recipe = for_recipe
        self.ingredient_notes = ingredient_notes
        self.quantity_notes = quantity_notes
        self.quantity = quantity
        self.unit = unit

    def __str__(self):
        return f"{self.name}, {self.for_recipe}, {self.ingredient_notes}, {self.quantity_notes}, {self.quantity}, {self.unit}"
           

def create_filename(recipe_name):
    """ 
    Creates an image filename out of recipe name.

    Args:
        recipe_name (str): The recipe name.

    Returns:
        filename (str): A proper filename for the image.
    """

    filename = recipe_name.lower()
    filename = filename.replace(" ", "_")
    # Removes any non-alphanumeric characters except for underscores
    filename = re.sub(r'[^a-z0-9_]', '', filename)
    filename = filename + ".png"
    
    return filename

def extract_recipes(file_path):
    """ 
    Extract recipes from the text file and store them in a list.

    Args:
        file_path (str): Path to the text file.

    Returns:
        extracted_recipes: A list of recipe objects.
    """
    extracted_recipes = []

    # Open and process recipe text file
    with open(file_path, 'r', encoding='utf-8') as file:
        sections = file.read().split('---')
        for section in sections[1:]:
            parts = section.split('\n\n')
            # Check if servings information exists
            servings_match = re.search(r'\(for (\d+) servings\)', parts[5])
            create_recipe = Recipe(
                language=file_path.split("\\")[3],
                menu_name=file_path.split("\\")[4].split("_")[0].capitalize(),
                day_of_week=parts[1].split(':')[0].strip().capitalize(),
                meal_type=parts[1].split(':')[1].strip().capitalize(),
                name=parts[2].strip(),
                prep_time= parts[3].split(':')[1].strip(),
                cook_time= parts[4].split(':')[1].strip(),
                ingredients=[item.strip() for item in parts[5].split('\n') if "INGREDIENTS:" not in item],
                instructions=[step.strip() for step in parts[6].split('\n') if "INSTRUCTIONS:" not in step],
                servings=int(servings_match.group(1)) if servings_match else 1 
            )

            extracted_recipes.append(create_recipe)

    return extracted_recipes

def add_recipe_to_db(recipes, db_path):
    """ 
    Extracts recipe components from a list of recipe objects and writes them into a database.

    Args:
        db_path (str): Path to the database.
        recipes (list): A list of recipe objects.

    Returns:
        message (str): Info message.
    """
    message = ""
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Successfully connected to the database: {db_path}")

        for index, recipe in enumerate(recipes):
            try:
                image_path = create_filename(recipe.name) # Placeholder for image path

                # Insert the recipe
                cursor.execute('''
                    INSERT INTO recipes (title, prep_time, cook_time, image_path, servings)
                    VALUES (?, ?, ?, ?, ?)
                ''', (recipe.name, recipe.prep_time, recipe.cook_time, image_path, recipe.servings))
                print(f"Recipe number '{index}' --- '{recipe.name}' was added successfully.")

            except sqlite3.Error as insert_error:
                print(f"Error inserting recipe number '{index}' --- '{recipe.name}': {insert_error}")
        
        # Commit changes to the database
        conn.commit()
        message = "Recipes added successfully."

    except sqlite3.Error as db_error:
        message = f"Error connecting to the database: {db_error}"
        print(message)
    
    finally:
        # Close the connection
        if conn:
            conn.close()
            print("Database connection closed.")

    return message

def add_tags_to_recipe(recipes, db_path):
    """ 
    Extracts tags from a list of recipe objects and writes them into a database.

    Args:
        db_path (str): Path to the database.
        recipes (list): A list of recipe objects.

    Returns:
        message (str): Info message.
    """
    message = ""
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Successfully connected to the database: {db_path}")

        for index, recipe in enumerate(recipes):
            try:
                # Query the recipes table to get the recipe_id
                cursor.execute('''
                        SELECT id FROM recipes WHERE TRIM(LOWER(title)) = TRIM(LOWER(?))
                    ''', (recipe.name.strip().lower(),))

                recipe_id = cursor.fetchone()
                if recipe_id:
                    recipe_id = recipe_id[0]
                    tag_names = [recipe.meal_type, recipe.day_of_week, recipe.menu_name]
                else:
                    print(f"No such recipe '{recipe.name}'")
                    return

                tag_ids = []
                for tag_name in tag_names:
                    # Query the tags table to get the tag_id
                    cursor.execute('''
                        SELECT id FROM tags WHERE name = ?
                    ''', (tag_name,))

                    tag_id = cursor.fetchone()

                    if tag_id:
                        tag_ids.append(tag_id[0])
                    else:
                        print(f"Tag '{tag_name}' not found.")
                        return
                    
                for tag_id in tag_ids:
                    # Insert the association
                    cursor.execute('''
                        INSERT INTO recipe_tags (recipe_id, tag_id)
                        VALUES (?, ?)
                    ''', (recipe_id, tag_id))

                    print(f"Added tag '{tag_id}' to recipe '{recipe.name.strip()}'.")

            except sqlite3.Error as insert_error:
                print(f"Error inserting tags to the recipe number '{index}' --- '{recipe.name}': {insert_error}")
        
        # Commit changes to the database
        conn.commit()
        message = "Tags added successfully."

    except sqlite3.Error as db_error:
        message = f"Error connecting to the database: {db_error}"
        print(message)
    
    finally:
        # Close the connection
        if conn:
            conn.close()
            print("Database connection closed.")

    return message

def extract_ingredients(recipes):
    """ 
    Extracts recipe ingredients from a list of recipe objects and returns a list of ingredient objects.

    Args:
        recipes (list): A list of recipe objects.

    Returns:
        ingredients (list): A list of ingredient objects.
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

                create_ingredient = Ingredient(
                    name=ingredient_name,
                    for_recipe=recipe.name,
                    ingredient_notes=ingredient_note,
                    quantity_notes=quantity_note,
                    quantity=quantity,
                    unit=unit
                )
                ingredients.append(create_ingredient)
            else:
                print(f"Attention!!!!!! Strange item: {item} !!!!!!")
            
    return ingredients

def add_ingredients_to_db(ingredients, db_path):
    """ 
    Writes ingredients to the database.

    Args:
        db_path (str): Path to the database.
        ingredients (list): A list of recipe objects.

    Returns:
        message (str): Info message.
    """
    message = ""
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Successfully connected to the database: {db_path}")

        for index, ingredient in enumerate(ingredients):
            try:
                # Query the ingredients table to get the ingredient_id
                cursor.execute('''
                    SELECT id FROM ingredients WHERE name = ?
                ''', (ingredient.name,))

                ingredient_id = cursor.fetchone()

                if not ingredient_id:
                    try:
                        # Insert new ingredient
                        cursor.execute('''
                                INSERT INTO ingredients (name)
                                VALUES (?) 
                            ''', (ingredient.name,))
                        print(f"Added {ingredient.name} to the Ingredients table successfully!")

                        ingredient_id = cursor.execute('''
                            SELECT id FROM ingredients WHERE name = ?
                        ''', (ingredient.name,)).fetchone()
                    except sqlite3.Error as new_ingr_error:
                        message = f"New ingredient insert failed for {ingredient.name} error: {new_ingr_error}."
                        print(message)
                ingredient_id = ingredient_id[0]

                # Query the recipes table to get the recipe_id
                cursor.execute('''
                        SELECT id FROM recipes WHERE TRIM(LOWER(title)) = TRIM(LOWER(?))
                    ''', (ingredient.for_recipe.strip().lower(),))

                recipe_id = cursor.fetchone()
                if recipe_id:
                    recipe_id = recipe_id[0]
                    # Insert the ingredients for recipe
                    cursor.execute('''
                        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, quantity_notes, ingredient_notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (recipe_id, ingredient_id, ingredient.quantity, ingredient.unit, ingredient.quantity_notes, ingredient.ingredient_notes))

                    print(f"{index} Added ingredient '{ingredient.name}' to recipe '{ingredient.for_recipe}'.")
                else:
                    print(f"No such recipe '{ingredient.for_recipe}'")
                    return 
        
            except sqlite3.Error as insert_error:
                message = f"Error inserting ingredient {ingredient.name} to the recipe {ingredient.for_recipe}: {insert_error}"
                print(message)
        
        # Commit changes to the database
        conn.commit()
        message = "Ingredients added successfully."

    except sqlite3.Error as db_error:
        message = f"Error connecting to the database: {db_error}"
        print(message)
    
    finally:
        # Close the connection
        if conn:
            conn.close()
            print("Database connection closed.")

    return message

def instructions_to_db(recipes, db_path):
    """ 
    Extracts recipe instructions from a list of recipe objects and writes them to the database.

    Args:
        recipes (list): A list of recipe objects.
        db_path (str): Path to the database.

    Returns:
        message (str): Info message.
    """
    message = ""
    
    # Convert recipes into a list of instructions
    all_recipes = []
    for recipe in recipes:
        recipe_instructions = {}
        recipe_instructions["name"] = recipe.name
        recipe_instructions["instructions"] = []
        for item in recipe.instructions:
            recipe_instructions["instructions"].append({"step": int(item[0]), "description": item[3:]})
        all_recipes.append(recipe_instructions)

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Successfully connected to the database: {db_path}")

        for recipe_data in all_recipes:
            # Query the recipes table to get the recipe_id
            cursor.execute('''
                SELECT id FROM recipes WHERE TRIM(LOWER(title)) = TRIM(LOWER(?))
            ''', (recipe_data["name"].strip().lower(),))

            recipe_id = cursor.fetchone()
            if recipe_id:
                recipe_id = recipe_id[0]
                for instruction in recipe_data["instructions"]:
                    try:
                        # Insert the instructions for the recipe
                        cursor.execute('''
                            INSERT INTO instructions (recipe_id, step_number, instruction)
                            VALUES (?, ?, ?)
                        ''', (recipe_id, instruction["step"], instruction["description"]))
                        print(f"Added step {instruction['step']} to recipe '{recipe_data['name']}'.")
                    except sqlite3.Error as insert_error:
                        print(
                            f"Error inserting step {instruction['step']} ('{instruction['description']}') for recipe '{recipe_data['name']}': {insert_error}"
                        )
            else:
                print(f"No such recipe '{recipe_data['name']}' found in the database. Skipping.")
                continue

        # Commit changes to the database
        conn.commit()
        message = "Instructions added successfully."
    except sqlite3.Error as db_error:
        message = f"Error connecting to the database: {db_error}"
        print(message)
    finally:
        # Close the connection
        if conn:
            conn.close()
            print("Database connection closed.")
    return message


file_path = r"D:\Nutri_Cat\cleaned_up_recipes\en\summer_menu_en.txt"
db_path = r"D:\Nutri_Cat\instance\nutri_cat.sqlite"  
""" 
    Please carefully adjust the full paths before each use!

"""
recipes = extract_recipes(file_path)
#add_recipe_to_db(recipes, db_path)
#add_tags_to_recipe(recipes, db_path)
#add_ingredients_to_db(extract_ingredients(recipes), db_path)
instructions_to_db(recipes, db_path)



        

