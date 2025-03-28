from flask import (
    Blueprint, flash, g, jsonify, redirect, render_template, request, session, url_for
)
from flask_sqlalchemy import pagination
from werkzeug.exceptions import abort
from sqlalchemy.orm import joinedload
from sqlalchemy import asc, desc
from app.auth import login_required
from app.db import db
from app.models import Recipe, Tag, RecipeTag, User

bp = Blueprint('recipes', __name__)

@bp.route('/')
def index():
    # Fetch first 7 recipes
    recipes = Recipe.query.limit(7).all()

    favorite_recipes = [
        {
            'name': recipe.title.capitalize(),
            'time': (recipe.prep_time or 0) + (recipe.cook_time or 0),
            'image': recipe.compressed_img_URL or "default_image.png"
        }
        for recipe in recipes
    ]

    user = User.query.filter_by(id=session.get('user_id')).first()
    
    return render_template('recipes/index.html', favorites=favorite_recipes, user=user)

@bp.route('/recipes')
def recipes():
    # Get query parameters
    filter_tag = request.args.get('filter', None)
    sort_order = request.args.get('sort', 'default')
    time_sort_order = request.args.get('time_sort')
    page = request.args.get('page', 1, type=int)
    per_page = 9

    # Get unique tag types and their names
    tag_types = db.session.query(Tag.type).distinct().all()
    tag_types = [t[0] for t in tag_types]
    tag_options = {}
    for t in tag_types:
        options = db.session.query(Tag.name).filter(Tag.type == t).distinct().all()
        options = [n[0] for n in options]
        if "day" in t:
            week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            options = sorted(options, key=lambda x: week_days.index(x) if x in week_days else len(week_days))
            tag_name = "Day of the week"
        elif "meal" in t:
            meal_order = ["Breakfast", "Lunch", "Dinner", "Dessert"]
            options = sorted(options, key=lambda x: meal_order.index(x) if x in meal_order else len(meal_order))
            tag_name = "Meals"
        elif "menu" in t:
            options = sorted(options)
            tag_name = "Menu"
        else:
            tag_name = t
            
        tag_options[tag_name] = options

    # Base query for recipes
    query = Recipe.query.options(joinedload(Recipe.tags))

    # Apply filter if a tag name is selected
    if filter_tag:
        query = query.join(Recipe.tags).filter(Tag.name == filter_tag)

    # Apply sorting by title
    if sort_order == "asc":
        query = query.order_by(asc(Recipe.title))
    elif sort_order == "desc":
        query = query.order_by(desc(Recipe.title))
    else:
        query = query.order_by(Recipe.id.asc())

    # Pagination
    paginated_recipes = query.paginate(page=page, per_page=per_page, error_out=False)

    # AJAX response for filtering
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "recipes": [{
            "title": recipe.title,
            "compressed_img_URL": recipe.compressed_img_URL or recipe.quality_img_URL or recipe.local_image_path,
            "prep_time": recipe.prep_time,
            "cook_time": recipe.cook_time,
            "tags": [{"name": tag.name} for tag in recipe.tags],
            "id": recipe.id
        } for recipe in paginated_recipes.items],
        "total_pages": paginated_recipes.pages})

    return render_template(
        "recipes/recipes.html",
        recipes=paginated_recipes.items,
        tag_options=tag_options,
        page=page,
        total_pages=paginated_recipes.pages,
        sort_order=sort_order
    )


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        servings = request.form.get('servings', type=int)
        prep_time = request.form.get('prep_time', type=int)
        cook_time = request.form.get('cook_time', type=int)
        compressed_img_URL = request.form.get('compressed_img_URL')
        tag_names = request.form.getlist('tags')  # Assuming multi-select for tags
        error = None

        if not title:
            error = 'Title is required.'

        if error:
            flash(error)
        else:
            recipe = Recipe(
                title=title,
                servings=servings or 1,
                prep_time=prep_time,
                cook_time=cook_time,
                compressed_img_URL=compressed_img_URL,
            )
            db.session.add(recipe)
            db.session.commit()

            # Add tags if provided
            if tag_names:
                for tag_name in tag_names:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                        db.session.commit()
                    db.session.add(RecipeTag(recipe_id=recipe.id, tag_id=tag.id))
                db.session.commit()

            return redirect(url_for('recipes.index'))

    return render_template('recipes/create.html')



def get_recipe(id, check_author=True):
    recipe = Recipe.query.get_or_404(id)

    if check_author and g.user.id != recipe.author_id:
        abort(403)

    return recipe

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    recipe = get_recipe(id)

    if request.method == 'POST':
        recipe.title = request.form['title']
        recipe.servings = request.form.get('servings', type=int)
        recipe.prep_time = request.form.get('prep_time', type=int)
        recipe.cook_time = request.form.get('cook_time', type=int)
        recipe.compressed_img_URL = request.form.get('compressed_img_URL')
        tag_names = request.form.getlist('tags')

        if not recipe.title:
            flash('Title is required.')
        else:
            # Update tags
            recipe.tags.clear()
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                db.session.add(RecipeTag(recipe_id=recipe.id, tag_id=tag.id))

            db.session.commit()
            return redirect(url_for('recipes.index'))

    return render_template('recipes/update.html', recipe=recipe)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    recipe = get_recipe(id)
    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for('recipes.index'))

@bp.route('/menus')
def menus():
    return render_template('recipes/menus.html')