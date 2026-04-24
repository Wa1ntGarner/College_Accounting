from sqlalchemy.orm import Session
from models import Room
from database import SessionLocal


class RoomService:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_rooms(self):
        return self.db.query(Room).order_by(Room.room_number).all()

    def get_room_by_id(self, room_id):
        return self.db.query(Room).filter(Room.id == room_id).first()

    def get_available_rooms(self):
        return self.db.query(Room).filter(Room.current_occupancy < Room.capacity).all()

    def create_room(self, room_data):
        room = Room(
            room_number=room_data["room_number"],
            floor=room_data["floor"],
            capacity=room_data["capacity"],
            current_occupancy=room_data.get("current_occupancy", 0),
            monthly_price=room_data["monthly_price"]
        )
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def update_room(self, room_id, room_data):
        room = self.get_room_by_id(room_id)
        if room:
            room.room_number = room_data["room_number"]
            room.floor = room_data["floor"]
            room.capacity = room_data["capacity"]
            room.current_occupancy = room_data.get("current_occupancy", room.current_occupancy)
            room.monthly_price = room_data["monthly_price"]
            self.db.commit()
            self.db.refresh(room)
        return room

    def delete_room(self, room_id):
        room = self.get_room_by_id(room_id)
        if room:
            self.db.delete(room)
            self.db.commit()
            return True
        return False

    def update_occupancy(self, room_id, delta):
        room = self.get_room_by_id(room_id)
        if room:
            room.current_occupancy += delta
            self.db.commit()
            self.db.refresh(room)
        return room

    def __del__(self):
        self.db.close()