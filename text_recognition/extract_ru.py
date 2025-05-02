# Defined class to store recipe
class Recipe:
    def __init__(self, language, name, ingredients, instructions, servings=1, prep_time=0, cook_time=0):
        self.language = language
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions
        self.servings = servings
        self.prep_time = prep_time
        self.cook_time = cook_time

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

    def to_dict(self):
        """Convert recipe object to a dictionary."""
        return {
            "language": self.language,
            "name": self.name,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "servings": self.servings,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time
        }

    def __str__(self):
        return f"{self.name}, {self.language}, {self.ingredients}, {self.instructions}, {self.servings}, {self.prep_time}, {self.cook_time}"



def extract_recipes(file_path):
    """
    Extract recipes from a Russian text file and store them in a list.

    Args:
        file_path (str): Path to the text file.

    Returns:
        list: A list of recipe objects.
    """
    extracted_recipes = []

    # Open and process recipe text file
    with open(file_path, 'r', encoding='utf-8') as file:
        sections = file.read().split('---')
        for section in sections[1:]:
            parts = section.split('\n\n')
            create_recipe = Recipe(
                language="ru",
                name=parts[2].strip(),
                prep_time= parts[3].split(':')[1].strip(),
                cook_time= parts[4].split(':')[1].strip(),
                ingredients=[item.strip() for item in parts[5].split('\n') if "ПОНАДОБИТСЯ:" not in item],
                instructions=[step.strip() for step in parts[6].split('\n') if "ПРИГОТОВЛЕНИЕ:" not in step]
            )

            extracted_recipes.append(create_recipe)

    return extracted_recipes


file_path = "text_recognition/formatted/italian_menu.txt"  
recipes = extract_recipes(file_path)
for recipe in recipes:
    print(recipe.to_dict())