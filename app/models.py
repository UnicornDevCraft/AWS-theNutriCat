"""Database models for the application."""

# Related third-party imports
from sqlalchemy import Index, event
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

# Local application/library imports
from app.db import db

# User model for authentication and user management
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def set_password(self, user_password):
        self.password = generate_password_hash(user_password)

    def check_password(self, user_password):
        return check_password_hash(self.password, user_password)


# Recipe model for storing recipe information
class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    servings = db.Column(db.Integer, nullable=False, default=1)
    prep_time = db.Column(db.Integer, nullable=True)
    cook_time = db.Column(db.Integer, nullable=True)
    local_image_path = db.Column(db.String(255), nullable=True)
    quality_img_URL = db.Column(db.String(255), nullable=True)
    compressed_img_URL = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    tags = db.relationship('Tag', secondary='recipe_tags', back_populates='recipes', cascade="all, delete")
    ingredients = db.relationship('Ingredient', secondary='recipe_ingredients', backref='recipes')
    instructions = db.relationship('Instruction', backref='recipes', lazy=True, cascade="all, delete-orphan")
    title_search = db.Column(TSVECTOR)

    @validates('title')
    def validate_title(self, key, value):
        self.title_search = func.to_tsvector('english', value)
        return value

@event.listens_for(Recipe, 'before_insert')
@event.listens_for(Recipe, 'before_update')
def update_title_search(mapper, connection, target):
    if target.title:
        target.title_search = func.to_tsvector('english', target.title)


# RecipeTranslation model for storing translations of recipes // TODO: add support for multiple languages
class RecipeTranslation(db.Model):
    __tablename__ = "recipe_translations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    language_code = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# Ingredient model for storing ingredient information
class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    name_search = db.Column(TSVECTOR)

    __table_args__ = (
        Index('ix_ingredients_name', 'name'),  # Create index on 'name' column
    )

    @validates('name')
    def validate_name(self, key, value):
        self.name_search = func.to_tsvector('english', value)
        return value


# RecipeIngredient model for storing the relationship between recipes and ingredients
class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    quantity = db.Column(db.String(50), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    quantity_notes = db.Column(db.String(50), nullable=True)
    ingredient_notes = db.Column(db.String(255), nullable=True) 
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# IngredientTranslation model for storing translations of ingredients
class IngredientTranslation(db.Model):
    __tablename__ = "ingredient_translations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    language_code = db.Column(db.String(10), nullable=False)
    translated_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# Instruction model for storing cooking instructions
class Instruction(db.Model):
    __tablename__ = "instructions"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    instruction = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    instruction_search = db.Column(TSVECTOR)

    @validates('instruction')
    def validate_instruction(self, key, value):
        self.instruction_search = func.to_tsvector('english', value)
        return value


# Tag model for storing tags related to recipes
class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
     # Recipe relationship using the association table 'recipe_tags'
    recipes = db.relationship("Recipe", secondary="recipe_tags", back_populates="tags", passive_deletes=True)

    __table_args__ = (
        db.UniqueConstraint('name', 'type', name='uix_tag_name_type'),
        Index('ix_tags_name', 'name'), 
    )


# RecipeTag model for storing the many-to-many relationship between recipes and tags
class RecipeTag(db.Model):
    __tablename__ = "recipe_tags"

    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True, nullable=False)


# Favorite model for storing user favorites
class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    added_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Ensures a user cannot favorite the same recipe multiple times
    __table_args__ = (db.UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe"),)


# UserRecipeNote model for storing user notes on recipes
class UserRecipeNote(db.Model):
    __tablename__ = "user_recipe_notes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Ensures a user cannot leave multiple notes for the same recipe
    user = db.relationship("User", backref="recipe_notes")
    recipe = db.relationship("Recipe", backref="user_notes")
    

    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='uix_user_recipe'),)


# MenuShoppingInfo model for storing shopping information related to menus
class MenuShoppingInfo(db.Model):
    __tablename__ = "menu_shopping_infos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    menu_tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete="CASCADE"), unique=True, nullable=False)
    shopping_list_text = db.Column(db.Text, nullable=True)
    preparations_text = db.Column(db.Text, nullable=True)
    meat_marinades_text = db.Column(db.Text, nullable=True)
    dressings_text = db.Column(db.Text, nullable=True)
    rules_and_tips_text = db.Column(db.Text, nullable=True)

    menu_tag = db.relationship('Tag')


# Adding indexing for search
Index('ix_recipes_title_search', Recipe.title_search, postgresql_using='gin')
Index('ix_ingredients_name_search', Ingredient.name_search, postgresql_using='gin')
Index('ix_instructions_instruction_search', Instruction.instruction_search, postgresql_using='gin')