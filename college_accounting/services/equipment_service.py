from sqlalchemy.orm import Session
from models import Equipment
from database import SessionLocal


class EquipmentService:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_equipment(self):
        return self.db.query(Equipment).order_by(Equipment.room_id, Equipment.name).all()

    def get_equipment_by_id(self, equipment_id):
        return self.db.query(Equipment).filter(Equipment.id == equipment_id).first()

    def get_equipment_by_room(self, room_id):
        return self.db.query(Equipment).filter(
            Equipment.room_id == room_id
        ).order_by(Equipment.name).all()

    def create_equipment(self, equipment_data):
        equipment = Equipment(
            room_id=equipment_data["room_id"],
            name=equipment_data["name"],
            quantity=equipment_data.get("quantity", 1),
            condition=equipment_data.get("condition", "good")
        )
        self.db.add(equipment)
        self.db.commit()
        self.db.refresh(equipment)
        return equipment

    def update_equipment(self, equipment_id, equipment_data):
        equipment = self.get_equipment_by_id(equipment_id)
        if equipment:
            equipment.room_id = equipment_data["room_id"]
            equipment.name = equipment_data["name"]
            equipment.quantity = equipment_data.get("quantity", equipment.quantity)
            equipment.condition = equipment_data.get("condition", equipment.condition)
            self.db.commit()
            self.db.refresh(equipment)
        return equipment

    def delete_equipment(self, equipment_id):
        equipment = self.get_equipment_by_id(equipment_id)
        if equipment:
            self.db.delete(equipment)
            self.db.commit()
            return True
        return False

    def __del__(self):
        self.db.close()