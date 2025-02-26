from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from sqlalchemy.orm import joinedload

from app.auth import login_required
from app.db import db
from app.models import Recipe, Tag, RecipeTag

bp = Blueprint('recipes', __name__)

@bp.route('/')
def index():
    # Fetch first 7 recipes
    recipes = Recipe.query.limit(7).all()

    favorite_recipes = [
        {
            'name': recipe.title.capitalize(),
            'time': (recipe.prep_time or 0) + (recipe.cook_time or 0),
            'image': recipe.image_path or "default_image.png"
        }
        for recipe in recipes
    ]

    return render_template('recipes/index.html', favorites=favorite_recipes)

@bp.route('/recipes')
def recipes():
    per_page = 9
    page = request.args.get('page', 1, type=int)
    
    # Fetch recipes with associated tags, paginated
    paginated_recipes = Recipe.query.options(
        joinedload(Recipe.tags)  # Eager load tags
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'recipes/recipes.html',
        recipes=paginated_recipes.items,
        page=page,
        total_pages=paginated_recipes.pages
    )

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        servings = request.form.get('servings', type=int)
        prep_time = request.form.get('prep_time', type=int)
        cook_time = request.form.get('cook_time', type=int)
        image_path = request.form.get('image_path')
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
                image_path=image_path,
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
        recipe.image_path = request.form.get('image_path')
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