from app.db import db
from app.models import Recipe, Tag
from werkzeug.exceptions import NotFound
import os
import boto3

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
s3_folder = os.getenv("AWS_S3_FOLDER")

def delete_local_image(path):
    try:
        os.remove(path)
    except Exception as e:
        print(f"Failed to delete local image: {e}")

def delete_s3_image(s3_url):
    # Parse bucket and key from the URL
    s3 = boto3.client('s3')
    key = s3_url.split(f"{S3_BUCKET_NAME}/")[-1]

    try:
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=key)
    except Exception as e:
        print(f"Failed to delete from S3: {e}")


def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)

    if not recipe:
        raise NotFound("Recipe not found.")

    # Delete images (handle S3 or local path)
    if recipe.local_image_path:
        delete_local_image(recipe.local_image_path)

    if recipe.compressed_img_URL:
        delete_s3_image(recipe.compressed_img_URL)

    if recipe.quality_img_URL:
        delete_s3_image(recipe.quality_img_URL)

    # Detach tags to check which are orphaned
    my_recipe_tag_ids = []
    for tag in recipe.tags:
        if tag.type == 'my_recipe':
            my_recipe_tag_ids.append(tag.id)

    db.session.delete(recipe)
    db.session.commit()

    # Now remove orphaned "my_recipe" tags
    for tag_id in my_recipe_tag_ids:
        tag = Tag.query.get(tag_id)
        if tag and tag.type == 'my_recipe' and len(tag.recipes) == 0:
            print(f"Deleting orphaned tag: {tag.name}")
            db.session.delete(tag)

    db.session.commit()
    return True


