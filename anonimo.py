import csv
from datetime import datetime
from app import create_app
from app.modules.core.database import db
from app.database.models import User, Eu2016

# Initialize application context
app = create_app()

with app.app_context():
    # Step 1: Ensure the anonymous user exists in the database
    anonymous_user = db.session.get(User, 3)
    if not anonymous_user:
        anonymous_user = User(
            id=3,
            google_id="1",
            email="1",
            name="anonimo"
        )
        db.session.add(anonymous_user)
        db.session.commit()
        print("User 'anonimo' created successfully.")

    # Step 2: Read anonimo.csv from backups folder and insert records linked to fk_user_id = 3
    csv_file_path = "backups/anonimo.csv"
    imported_count = 0

    with open(csv_file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            record_timestamp = datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S")
            
            # Check if record already exists for this user and timestamp
            existing_record = Eu2016.query.filter_by(carimbo=record_timestamp, fk_user_id=3).first()
            if not existing_record:
                new_record = Eu2016(
                    carimbo=record_timestamp,
                    peso=float(row["Weight"]),
                    gordura=float(row["Fat"]),
                    musculo=float(row["Muscle"]),
                    basal=float(row["Basal"]),
                    idade=float(row["Age"]),
                    viceral=float(row["Visceral"]),
                    fk_user_id=3
                )
                db.session.add(new_record)
                imported_count += 1
        
        db.session.commit()
        print(f"Successfully imported {imported_count} records for user 'anonimos'.")
