import json
from app import create_app, db
from app.models import Ingredient

app = create_app()

with app.app_context():
    ingredients = Ingredient.query.order_by(Ingredient.name).all()

    # Export to CSV
    import csv
    with open("ingredients_dump.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name"])
        for i in ingredients:
            writer.writerow([i.id, i.name])
