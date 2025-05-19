from app import create_app, mongo

app = create_app()

def clear_services():
    with app.app_context():
        result = mongo.db.services.delete_many({"category": "Healthcare"})
        print(f"Deleted {result.deleted_count} healthcare services from the database")

if __name__ == "__main__":
    clear_services()
    print("Healthcare services cleared successfully!")
