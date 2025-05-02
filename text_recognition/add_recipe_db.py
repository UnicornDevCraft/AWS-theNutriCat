"""Before running check path and extraction file!!!! 
    Add enumerate and count, comment recipe = , change recipe_id do count
    Dont forget to automate the script tomorrow!!!
"""

# Local imports
from app import create_app
from app.db import db
from app.models import Recipe, RecipeTranslation
from extract_en import extract_recipes


def add_recipes_to_db(file_path):
    """Add recipes to the database from a given file."""
    # Extract recipes from the file
    recipes = extract_recipes(file_path)

    for count, extracted_recipe in enumerate(recipes, start=1):
        # Step 1: Create the Recipe object
        recipe = Recipe(
            servings=extracted_recipe.servings,
            prep_time=int(extracted_recipe.prep_time),
            cook_time=int(extracted_recipe.cook_time)
        )

        # Add the Recipe object to the database session
        db.session.add(recipe)
        db.session.flush()

        # Step 2: Create the RecipeTranslation object
        translation = RecipeTranslation(
            recipe_id=count,
            language=extracted_recipe.language,
            name=extracted_recipe.name,
            description=None,
            ingredients="\n".join(extracted_recipe.ingredients),
            instructions="\n".join(extracted_recipe.instructions) 
        )

        # Add the RecipeTranslation object to the session
        db.session.add(translation)

    # Step 3: Commit all changes to the database
    db.session.commit()
    print("Recipes successfully added to the database!")


if __name__ == "__main__":
    # Initialize the app and push the app context
    app = create_app()
    with app.app_context():  # Push the app context
        file_path = "text_recognition/formatted/italian_menu_en.txt"
        add_recipes_to_db(file_path)
        
