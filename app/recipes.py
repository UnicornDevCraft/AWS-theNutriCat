from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

bp = Blueprint('recipes', __name__)

@bp.route('/')
def index():
    db = get_db()
    favorite_recipes = []

    try:
        # Query the database for the first 7 recipes
        favorites = db.execute('''
            SELECT title, cook_time, prep_time, image_path
            FROM recipes WHERE id < 8
        ''').fetchall()

        if not favorites:
            print("No favorite recipes found in the database.")
            return render_template('recipes/index.html', favorites=[])

        # Process each recipe and build the favorite_recipes list
        for favorite in favorites:
            favorite_recipes.append({
                'name': favorite["title"].capitalize(),
                'time': (favorite["prep_time"] or 0) + (favorite["cook_time"] or 0),
                'image': favorite["image_path"] or "default_image.png"  # Fallback to a default image
            })

    except Exception as e:
        print(f"Database error: {e}")
        return f"An error occurred: {e}", 500

    return render_template('recipes/index.html', favorites=favorite_recipes)

@bp.route('/recipes')
def recipes():
    db = get_db()
    per_page = 9
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * per_page

    # SQL query to select recipe details along with associated tags
    query = """
        SELECT r.id, r.title, r.servings, r.prep_time, r.cook_time, r.image_path, 
               GROUP_CONCAT(t.name) AS tags
        FROM recipes r
        LEFT JOIN recipe_tags rt ON r.id = rt.recipe_id
        LEFT JOIN tags t ON rt.tag_id = t.id
        GROUP BY r.id
        LIMIT ? OFFSET ?
    """
    recipes = db.execute(query, (per_page, offset)).fetchall()

    # Query total count of recipes
    total_recipes = db.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    total_pages = (total_recipes + per_page - 1) // per_page

    return render_template('recipes/recipes.html', recipes=recipes, page=page, total_pages=total_pages)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('recipes.index'))

    return render_template('recipes/create.html')


def get_recipe(id, check_author=True):
    recipe = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if recipe is None:
        abort(404, f"Recipe id {id} doesn't exist.")

    if check_author and recipe['author_id'] != g.user['id']:
        abort(403)

    return recipe

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    recipe = get_recipe(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('recipes.index'))

    return render_template('recipes/update.html', recipe=recipe)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_recipe(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('recipes.index'))

@bp.route('/menus')
def menus():
    db = get_db()

    return render_template('recipes/menus.html')