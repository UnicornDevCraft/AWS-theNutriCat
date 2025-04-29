from flask import (
    Blueprint, flash, g, jsonify, redirect, render_template, request, session, url_for
)
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from app.models import db, Recipe, Tag, MenuShoppingInfo

bp = Blueprint("menus", __name__)


@bp.route('/menus')
def menus():
    # Get the user
    user = g.user
    # Get the menu names
    menu_names = Tag.query.filter_by(type='menu_name').order_by(Tag.name.asc()).all()
    return render_template('menus/menus.html', menu_names=menu_names, user=user)

@bp.route("/menus/<menu_name>", methods=["GET"])
def get_weekly_menu(menu_name):
    # Fetch the `menu_name` tag
    menu_tag = Tag.query.filter_by(name=menu_name, type="menu_name").first()
    print(menu_tag)
    if not menu_tag:
        return jsonify({"error": f"Menu '{menu_name}' not found."}), 404

    # Fetch the menu shopping information
    menu_shopping_info = MenuShoppingInfo.query.filter_by(menu_tag_id=menu_tag.id).first()

    # Preload tags for filtering
    meal_types = Tag.query.filter_by(type="meal_type").all()
    days_of_week = Tag.query.filter_by(type="day_of_week").order_by(Tag.id).all()

    # Recipe query: must be tagged with the given menu_name and a day_of_week and a meal_type
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
    shopping_list = {}

    # If menu shopping info is available, extract the relevant information
    if menu_shopping_info:
        if menu_shopping_info.rules_and_tips_text:
            shopping_list["rules_and_tips"] = [line for line in menu_shopping_info.rules_and_tips_text.replace("\\n", "\n").split("\n") if line.strip().startswith("*")]
        else:
            shopping_list["rules_and_tips"] = ""
        if menu_shopping_info.preparations_text:
            shopping_list["preparations"] = [line for line in menu_shopping_info.preparations_text.replace("\\n","\n").split("\n")[1:] if line.strip()]
        else:
            shopping_list["preparations"] = ""
        if menu_shopping_info.shopping_list_text:
            shopping_list["shopping_list"] = to_structured_list(menu_shopping_info.shopping_list_text.replace("\\n","\n").split("\n")[1:])
        else:
            shopping_list["shopping_list"] = ""
        if menu_shopping_info.meat_marinades_text:
            shopping_list["meat_marinades"] = to_structured_list(menu_shopping_info.meat_marinades_text.replace("\\n","\n").split("\n")[1:])
        else:
            shopping_list["meat_marinades"] = ""
        if menu_shopping_info.dressings_text:
            shopping_list["dressings"] = to_structured_list(menu_shopping_info.dressings_text.replace("\\n","\n").split("\n")[1:])
        else:
            shopping_list["dressings"] = ""

    print(shopping_list["preparations"])
    # Return the JSON response including menu shopping info
    return jsonify({
        "menu": menu_name,
        "recipes_by_day": result,
        "shopping_info": shopping_list
    })

@bp.route('/menus/categories')
def get_categories():
    categories = Tag.query.filter_by(type='menu_name').order_by(Tag.name.asc()).all()
    image_urls = ["https://nutri-cat-images.s3.eu-central-1.amazonaws.com/compressed_images/avocado_toast_with_egg_and_salad_compressed.jpg",
                  "https://nutri-cat-images.s3.eu-central-1.amazonaws.com/compressed_images/chicken_lasagna_alla_genovese_compressed.jpg",
                  "https://nutri-cat-images.s3.eu-central-1.amazonaws.com/compressed_images/guacamole_with_melon_and_lavash_nachos_compressed.jpg"]

    return jsonify([{
        "name": categories[i].name,
        "image_url": image_urls[i]
    } for i in range(len(categories))])


def to_structured_list(lines):
    structured_list = []
    current_category = None
    current_items = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue  # skip empty lines
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

    # Don't forget to add the last category
    if current_category and current_items:
        structured_list.append({
            "category": current_category,
            "items": current_items
        })

    return structured_list