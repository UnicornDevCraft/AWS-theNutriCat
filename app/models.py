from app.db import db
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import DDL, Index
from sqlalchemy.schema import CreateTable
from sqlalchemy.orm import validates
from sqlalchemy.dialects.postgresql import TSVECTOR

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
    tags = db.relationship('Tag', secondary='recipe_tags', backref='recipes')
    ingredients = db.relationship('Ingredient', secondary='recipe_ingredients', backref='recipes')
    instructions = db.relationship('Instruction', backref='recipes', lazy=True)
    title_search = db.Column(TSVECTOR)

    @validates('title')
    def validate_title(self, key, value):
        self.title_search = func.to_tsvector('english', value)
        return value

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

class IngredientTranslation(db.Model):
    __tablename__ = "ingredient_translations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    language_code = db.Column(db.String(10), nullable=False)
    translated_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


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

class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        Index('ix_tags_name', 'name'), 
    )

class RecipeTag(db.Model):
    __tablename__ = "recipe_tags"

    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True, nullable=False)

class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    added_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Ensures a user cannot favorite the same recipe multiple times
    __table_args__ = (db.UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe"),)

class UserRecipeNote(db.Model):
    __tablename__ = "user_recipe_notes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Optional relationships
    user = db.relationship("User", backref="recipe_notes")
    recipe = db.relationship("Recipe", backref="user_notes")

    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='uix_user_recipe'),)


# Adding indexing for search
Index('ix_recipes_title_search', Recipe.title_search, postgresql_using='gin')
Index('ix_ingredients_name_search', Ingredient.name_search, postgresql_using='gin')
Index('ix_instructions_instruction_search', Instruction.instruction_search, postgresql_using='gin')