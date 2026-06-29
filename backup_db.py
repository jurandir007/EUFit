# backup_db.py
import csv
import os
from datetime import datetime
from app.database.models import Eu2016

def run_backup():
    """Performs database backup and cleans up old files."""
    backup_folder = "backups"
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = os.path.join(backup_folder, f"backup_eufit_{timestamp}.csv")

    print(f"--- Starting backup at: {filename} ---")
    records = Eu2016.query.all()

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Weight', 'Fat', 'Muscle', 'Basal', 'Age', 'Visceral'])
            for r in records:
                writer.writerow([r.carimbo, r.peso, r.gordura, r.musculo, r.basal, r.idade, r.viceral])
        print("Backup saved successfully.")

        cleanup_old_backups(backup_folder, 30)

    except Exception as e:
        print(f"Error creating backup: {e}")

def cleanup_old_backups(folder, days):
    print(f"--- Checking cleanup in {folder} ---")
    import time
    now = time.time()
    limit = days * 24 * 60 * 60

    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isfile(path) and file.startswith('backup_eufit_'):
            if (now - os.path.getmtime(path)) > limit:
                os.remove(path)
                print(f"File removed: {file}")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        run_backup()