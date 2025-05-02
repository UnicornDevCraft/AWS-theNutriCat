"""Routes for managing menus."""

# Standard library imports
import logging

# Related third-party imports
from flask import (
    Blueprint, flash, g, jsonify, render_template, request, session
)
from sqlalchemy.orm import joinedload

# Local application/library imports
from app.models import db, Recipe, Tag, MenuShoppingInfo


# Create a blueprint for the menus
bp = Blueprint("menus", __name__)

# Set up logging
logger = logging.getLogger(__name__)


@bp.route("/menus")
def menus():
    """Render the menus page with a list of menu names."""
    user = g.user
    menu_names = Tag.query.filter_by(type="menu_name").order_by(Tag.name.asc()).all()
    return render_template("menus/menus.html", menu_names=menu_names, user=user)


@bp.route("/menus/<menu_name>", methods=["GET"])
def get_weekly_menu(menu_name):
    """Return structured weekly menu and shopping info for a given menu name."""
    menu_tag = Tag.query.filter_by(name=menu_name, type="menu_name").first()
    if not menu_tag:
        logger.warning(f"Menu '{menu_name}' not found.")
        return jsonify({"error": f"Menu '{menu_name}' not found."}), 404

    # Fetch the menu shopping information
    menu_shopping_info = MenuShoppingInfo.query.filter_by(menu_tag_id=menu_tag.id).first()

    # Preload tags for organizing recipes
    meal_types = Tag.query.filter_by(type="meal_type").all()
    days_of_week = Tag.query.filter_by(type="day_of_week").order_by(Tag.id).all()

    # Retrieve recipes matching the menu, day, and meal type
    recipes = (
        Recipe.query
        .join(Recipe.tags)
        .filter(
            Recipe.tags.any(id=menu_tag.id),
            Recipe.tags.any(Tag.type == "day_of_week"),
            Recipe.tags.any(Tag.type == "meal_type"),
            ~Recipe.tags.any(Tag.type == "my_recipe")
        )
        .options(joinedload(Recipe.tags))
        .all()
    )

    # Organize by day and meal type
    result = {}
    for day_tag in days_of_week:
        result[day_tag.name] = {mt.name: [] for mt in meal_types}

    for recipe in recipes:
        tag_types = {tag.type: tag.name for tag in recipe.tags}
        day = tag_types.get("day_of_week")
        meal = tag_types.get("meal_type")

        if day and meal and day in result and meal in result[day]:
            result[day][meal].append({
                "id": recipe.id,
                "title": recipe.title.capitalize()
            })
    # Build shopping info if available        
    shopping_info = {}

    if menu_shopping_info:
        shopping_info["rules_and_tips"] = [
            line for line in menu_shopping_info.rules_and_tips_text.replace("\\n", "\n").split("\n") 
            if line.strip().startswith("*")
            ] if menu_shopping_info.rules_and_tips_text else ""
        
        shopping_info["preparations"] = [
            line for line in menu_shopping_info.preparations_text.replace("\\n","\n").split("\n")[1:] 
            if line.strip()
            ] if menu_shopping_info.preparations_text else ""
        
        shopping_info["shopping_list"] = to_structured_list(
            menu_shopping_info.shopping_list_text.replace("\\n","\n").split("\n")[1:]
            ) if menu_shopping_info.shopping_list_text else ""
        
        shopping_info["meat_marinades"] = to_structured_list(
            menu_shopping_info.meat_marinades_text.replace("\\n","\n").split("\n")[1:]
            ) if menu_shopping_info.meat_marinades_text else ""
        
        shopping_info["dressings"] = to_structured_list(
            menu_shopping_info.dressings_text.replace("\\n","\n").split("\n")[1:]
            ) if menu_shopping_info.dressings_text else ""
        
    # Return the JSON response including menu shopping info
    return jsonify({
        "menu": menu_name,
        "recipes_by_day": result,
        "shopping_info": shopping_info
    })


@bp.route("/menus/categories")
def get_categories():
    """Return a list of menu categories with associated images."""
    categories = Tag.query.filter_by(type="menu_name").order_by(Tag.name.asc()).all()
    image_urls = [
        "https://nutri-cat-images.s3.eu-central-1.amazonaws.com/compressed_images/avocado_toast_with_egg_and_salad_compressed.jpg",
        "https://nutri-cat-images.s3.eu-central-1.amazonaws.com/compressed_images/chicken_lasagna_alla_genovese_compressed.jpg",
        "https://nutri-cat-images.s3.eu-central-1.amazonaws.com/compressed_images/guacamole_with_melon_and_lavash_nachos_compressed.jpg"
        ]

    return jsonify([{
        "name": categories[i].name,
        "image_url": image_urls[i]
    } for i in range(len(categories))])


def to_structured_list(lines):
    """
    Convert a list of lines into a structured list of categories and items.
    Args:
        lines (list): List of lines to be structured.
    Returns:
        list: Structured list of categories and items.
    """
    # Initialize the structured list
    structured_list = []
    current_category = None
    current_items = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.isupper():
            if current_category:
                structured_list.append({
                    "category": current_category,
                    "items": current_items
                })
            # start a new category
            current_category = stripped
            current_items = []
        else:
            current_items.append(stripped)

    # Add the final category block
    if current_category and current_items:
        structured_list.append({
            "category": current_category,
            "items": current_items
        })

    return structured_list