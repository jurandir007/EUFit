#app/services/vape_service.py
from app.modules.core.database import db
from app.database.models import RecordVape
from datetime import datetime

def create_vape_record(user_id, puff_count):
    try:
        new_record = RecordVape(user_id=user_id, puff_count=puff_count)
        db.session.add(new_record)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e

def delete_vape_record(record_id, user_id):
    try:
        record = RecordVape.query.filter_by(id=record_id, user_id=user_id).first()
        if record:
            db.session.delete(record)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        raise e

def update_vape_record(record_id, user_id, puff_count):
    try:
        record = RecordVape.query.filter_by(id=record_id, user_id=user_id).first()
        if record:
            record.puff_count = puff_count
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        raise e
