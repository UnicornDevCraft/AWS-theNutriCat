from flask import (
    Blueprint, flash, g, jsonify, redirect, render_template, request, session, url_for
)
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from app.models import db, Recipe, Tag

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

    print(result)

    return jsonify(result)