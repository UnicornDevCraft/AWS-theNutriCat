from flask import (
    Blueprint, flash, g, jsonify, redirect, render_template, request, session, url_for
)
from flask_sqlalchemy import pagination
from werkzeug.exceptions import abort
from sqlalchemy.orm import joinedload
from sqlalchemy import func, or_
from sqlalchemy import asc, desc
from app.auth import login_required
from app.db import db
from app.models import Favorite, Ingredient, Recipe, Instruction, RecipeTag, RecipeIngredient, Tag, User, UserRecipeNote
from app.utils.delete import delete_recipe
from werkzeug.utils import secure_filename
import os


bp = Blueprint('recipes', __name__)

# AWS S3 configuration
import boto3
import mimetypes
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
s3_folder = os.getenv("AWS_S3_FOLDER")

@bp.route('/')
def index():
    # Fetch first 7 recipes
    recipes = Recipe.query.limit(7).all()

    # Fetch the user from the session
    user = User.query.filter_by(id=session.get('user_id')).first()

    favorite_recipes = [
        {
            "name": recipe.title.capitalize(),
            "id" : recipe.id,
            "time" : (recipe.prep_time or 0) + (recipe.cook_time or 0),
            "image" : recipe.compressed_img_URL or "/static/img/recipes/placeholder-image.jpeg"
        }
        for recipe in recipes
    ]
    
    return render_template('recipes/index.html', favorites=favorite_recipes, user=user)

@bp.route('/recipes')
def recipes():
    # Get query parameters
    search_query = request.args.get('search', '')
    filter_tag = request.args.get('filter', None)
    tag_type = request.args.get('tag_type')
    sort_order = request.args.get('sort', 'default')
    page = request.args.get('page', 1, type=int)
    per_page = 9

    # Fetch the user from the session
    user = User.query.filter_by(id=session.get('user_id')).first()

    if user:
        # Fetch the user's favorite recipes
        favorite_recipes_ids = Favorite.query.filter_by(user_id=user.id).with_entities(Favorite.recipe_id).all()
        favorite_recipe_ids_set = {recipe_id for recipe_id, in favorite_recipes_ids}
    else:
        favorite_recipe_ids_set = set()
        user = None

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
        elif "my" in t:
            options = sorted(options)
            tag_name = "My recipes"
        else:
            tag_name = t
            
        tag_options[tag_name] = options

    # Full-text search query
    if search_query:
        # Search in title, ingredients, and instructions
        search_query_ts = func.websearch_to_tsquery('english', search_query)
        search_conditions = Recipe.title_search.op('@@')(search_query_ts)

        query = (
            db.session.query(Recipe)
            .join(Recipe.ingredients)
            .join(Recipe.instructions)
            .filter(search_conditions)
            .distinct(Recipe.id)
        )
        
    else:
        # Base query for recipes
        query = Recipe.query.options(joinedload(Recipe.tags))

    # Apply filter if a tag name is selected
    if filter_tag:
        if filter_tag == "favorites":
            query = query.filter(Recipe.id.in_(favorite_recipe_ids_set))
        else:
            query = query.join(Recipe.tags).filter(Tag.name == filter_tag)
    elif tag_type:
        query = query.join(Recipe.tags).filter(Tag.type == tag_type)

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
            "favorite": recipe.id in favorite_recipe_ids_set,
            "id": recipe.id
        } for recipe in paginated_recipes.items],
        "total_pages": paginated_recipes.pages,
        "user": True if user else False}
        )

    return render_template(
        "recipes/recipes.html",
        recipes=paginated_recipes.items,
        tag_options=tag_options,
        page=page,
        total_pages=paginated_recipes.pages,
        sort_order=sort_order,
        favorite_recipe_ids_set=favorite_recipe_ids_set, 
        user=user
    )

@bp.route('/recipe/<int:recipe_id>')
def recipe_id(recipe_id):
    note = None

    # Fetch recipe and eager-load relationships
    recipe = Recipe.query.options(
        joinedload(Recipe.tags),
        joinedload(Recipe.instructions),
        joinedload(Recipe.ingredients)
    ).get(recipe_id)

    if not recipe:
        abort(404)

    # Instructions (already eager-loaded, but sorted just in case)
    instructions = sorted(recipe.instructions, key=lambda x: x.step_number)

    # RecipeIngredients (includes quantity, unit, and ingredient data)
    recipe_ingredients = (
        RecipeIngredient.query
        .filter_by(recipe_id=recipe_id)
        .join(Ingredient)
        .add_entity(Ingredient)
        .all()
    )

    # Format ingredient data as needed: [(ingredient_name, quantity, unit, ingredient_notes)]
    ingredients = [
        {
            'name': ingredient.name,
            'quantity': ri.quantity,
            'unit': ri.unit,
            'quantity_notes': ri.quantity_notes,
            'ingredient_notes': ri.ingredient_notes
        }
        for ri, ingredient in recipe_ingredients
    ]

    # Favorite recipes set and notes
    favorite_recipe_ids_set = set()
    if g.user:
        favorite_recipe_ids_set = {
            fav.recipe_id for fav in Favorite.query.filter_by(user_id=g.user.id).all()
        }
        note = UserRecipeNote.query.filter_by(user_id=g.user.id, recipe_id=recipe_id).first()
        user = g.user
        # Check if this recipe has a 'my_recipe' tag
        has_my_recipe_tag = any(tag.type == "my_recipe" for tag in recipe.tags)

    return render_template(
        'recipes/recipe_id.html',
        recipe=recipe,
        ingredients=ingredients,
        instructions=instructions,
        favorite_recipe_ids_set=favorite_recipe_ids_set, 
        note=note, 
        user=user, 
        editable=has_my_recipe_tag
    )

@bp.route("/toggle_favorite/<int:recipe_id>", methods=["POST"])
@login_required
def toggle_favorite(recipe_id):
    user = g.user

    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return jsonify({"success": False, "error": "Recipe not found"}), 404

    favorite = Favorite.query.filter_by(user_id=user.id, recipe_id=recipe_id).first()

    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"success": True, "favorite": False, "message": "Removed from favorites!"})
    else:
        new_favorite = Favorite(user_id=user.id, recipe_id=recipe_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"success": True, "favorite": True, "message": "Added to favorites!"})

@bp.route('/recipe/<int:recipe_id>/note', methods=['POST'])
@login_required
def save_note(recipe_id):
    note_text = request.form.get('note', '')
    note = UserRecipeNote.query.filter_by(user_id=g.user.id, recipe_id=recipe_id).first()

    if note:
        note.note = note_text
    else:
        note = UserRecipeNote(user_id=g.user.id, recipe_id=recipe_id, note=note_text)
        db.session.add(note)

    db.session.commit()
    flash("Note saved successfully.", "success")
    return redirect(url_for('recipes.recipe_id', recipe_id=recipe_id, note=note_text))

@bp.route("/recipe/<int:recipe_id>/note/edit", methods=["POST"])
@login_required
def edit_note(recipe_id):
    note = UserRecipeNote.query.filter_by(user_id=g.user.id, recipe_id=recipe_id).first()
    if note:
        note.note = request.form["note"]
        db.session.commit()
        flash("Note updated successfully.", "success")
    return redirect(url_for("recipes.recipe_id", recipe_id=recipe_id))

@bp.route("/recipe/<int:recipe_id>/note/delete", methods=["POST"])
@login_required
def delete_note(recipe_id):
    note = UserRecipeNote.query.filter_by(user_id=g.user.id, recipe_id=recipe_id).first()
    if note:
        db.session.delete(note)
        db.session.commit()
        flash("Note deleted.","success")
    return redirect(url_for("recipes.recipe_id", recipe_id=recipe_id))


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == "POST":
        # --- BASIC FIELDS ---
        title = request.form.get("title")
        servings = request.form.get("servings", type=int)
        prep_time = request.form.get("prep_time", type=int)
        cook_time = request.form.get("cook_time", type=int)
        notes = request.form.get("notes")

        # --- INGREDIENTS ---
        ingredient_names = request.form.getlist("ingredient_name[]")
        quantities = request.form.getlist("quantity[]")
        units = request.form.getlist("unit[]")
        quantity_notes = request.form.getlist("quantity_notes[]")
        ingredient_notes = request.form.getlist("ingredient_notes[]")

        # --- INSTRUCTIONS ---
        steps = request.form.getlist("step[]")
        instructions = request.form.getlist("instruction[]")

        # --- TAGS ---
        tag_list = request.form.getlist("tag[]")

        # Check for basic required fields
        if not title or not servings or not prep_time or not cook_time:
            flash("All fields marked with * are required.", "error")
            return redirect(request.referrer)

        if not ingredient_names or not any(name.strip() for name in ingredient_names):
            flash("At least one ingredient is required.", "error")
            return redirect(request.referrer)

        if not tag_list or not any(tag.strip() for tag in tag_list):
            flash("At least one tag is required.", "error")
            return redirect(request.referrer)

        if not steps or not instructions or not any(i.strip() for i in instructions):
            flash("At least one instruction is required.", "error")
            return redirect(request.referrer)

        # --- CREATE RECIPE ---
        recipe = Recipe(
            title=title.strip(),
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
        )
        db.session.add(recipe)
        db.session.flush()  # get recipe.id early for FKs

        for i in range(len(ingredient_names)):
            name = ingredient_names[i].strip()
            if not name:
                continue
            ingredient = Ingredient.query.filter_by(name=name).first()
            if not ingredient:
                ingredient = Ingredient(name=name)
                db.session.add(ingredient)
                db.session.flush()

            ri = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity=quantities[i].strip() if i < len(quantities) else None,
                unit=units[i].strip() if i < len(units) else None,
                quantity_notes=quantity_notes[i].strip() if i < len(quantity_notes) else None,
                ingredient_notes=ingredient_notes[i].strip() if i < len(ingredient_notes) else None,
            )
            db.session.add(ri)

        for i in range(len(instructions)):
            line = instructions[i].strip()
            if not line:
                continue
            else:
                db.session.add(Instruction(
                    recipe_id=recipe.id,
                    step_number=steps[i].strip() if i < len(steps) else None,
                    instruction=line
                ))

        for i in range(len(tag_list)):
            name = tag_list[i].strip()
            if not name:
                continue 
            # Check if the tag already exists
            tag = Tag.query.filter_by(name=name, type='my_recipe').first()
            
            if not tag:
                tag = Tag(name=name, type='my_recipe')
                db.session.add(tag)
                db.session.flush()
            db.session.add(RecipeTag(recipe_id=recipe.id, tag_id=tag.id))

        # --- NOTES ---
        if notes:
            user_id = g.user.id
            db.session.add(UserRecipeNote(
                user_id=user_id,
                recipe_id=recipe.id,
                note=notes.strip()
            ))

        # --- IMAGE UPLOAD ---
        image = request.files.get("image")
        if image and image.filename:
            filename = secure_filename(image.filename)

            # Get MIME type
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or "application/octet-stream"

            # Initialize S3 client
            s3 = boto3.client("s3", region_name=AWS_REGION)

            # Upload directly from memory using file-like object
            s3.upload_fileobj(
                image,
                S3_BUCKET_NAME,
                f"{s3_folder}{filename}",
                ExtraArgs={"ContentType": content_type},
            )

            # Construct public URL
            file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_folder}{filename}"
            print(f"✅ Upload successful! File URL: {file_url}")

            # Save to database
            recipe.quality_img_URL = file_url
            recipe.compressed_img_URL = file_url

        db.session.commit()
        flash("Recipe added successfully!", "success")
        return redirect(url_for("recipes.recipe_id", recipe_id=recipe.id))

    # --- GET ---
    ingredients = Ingredient.query.order_by(Ingredient.name).all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template("recipes/create.html", ingredients=ingredients, tags=tags)


def get_recipe(id, check_author=True):
    recipe = Recipe.query.get_or_404(id)

    if check_author and g.user.id != recipe.author_id:
        abort(403)

    return recipe

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
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

    return render_template('recipes/edit.html', recipe=recipe, recipe_id=recipe.id)

@bp.route("/recipe/<int:recipe_id>/delete", methods=["POST"])
@login_required
def delete(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    # Only allow delete if recipe has a 'my_recipe' tag
    if not any(tag.type == "my_recipe" for tag in recipe.tags):
        flash("You are not allowed to delete this recipe.", "error")
        return redirect(url_for("recipes.recipe_id", recipe_id=recipe.id))
    
    for tag in recipe.tags:
        print(" - Tag:", tag.id, tag.name)

    db.session.delete(recipe)
    db.session.commit()
    flash("Recipe deleted successfully!", "success")
    return redirect(url_for("recipes.index"))


@bp.route('/menus')
def menus():
    return render_template('recipes/menus.html')


