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

@bp.route("/menus/<menu_name>")
def show_menu(menu_name):
    menu_tag = Tag.query.filter_by(name=menu_name, type='menu_name').first_or_404()
    recipes = Recipe.query.join(Recipe.tags).filter(Tag.id == menu_tag.id).all()
    
    return render_template('menus/menus.html', menu_tag=menu_tag, recipes=recipes)