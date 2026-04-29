from datetime import date
from sqlalchemy.orm import Session
from models import Contract, Student, Room
from database import SessionLocal


class ContractService:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_contracts(self):
        return self.db.query(Contract).order_by(Contract.check_in_date.desc()).all()

    def get_contract_by_id(self, contract_id):
        return self.db.query(Contract).filter(Contract.id == contract_id).first()

    def get_active_contracts(self):
        return self.db.query(Contract).filter(Contract.status == "active").all()

    def get_student_active_contract(self, student_id):
        return self.db.query(Contract).filter(
            Contract.student_id == student_id,
            Contract.status == "active"
        ).first()

    def create_contract(self, contract_data):
        contract = Contract(
            student_id=contract_data["student_id"],
            room_id=contract_data["room_id"],
            contract_number=contract_data["contract_number"],
            check_in_date=contract_data["check_in_date"],
            check_out_date=contract_data.get("check_out_date"),
            status=contract_data.get("status", "active")
        )
        self.db.add(contract)

        room = self.db.query(Room).filter(Room.id == contract_data["room_id"]).first()
        if room:
            room.current_occupancy += 1

        self.db.commit()
        self.db.refresh(contract)
        return contract

    def update_contract(self, contract_id, contract_data):
        contract = self.get_contract_by_id(contract_id)
        if contract:
            old_room_id = contract.room_id
            old_status = contract.status

            contract.student_id = contract_data["student_id"]
            contract.room_id = contract_data["room_id"]
            contract.contract_number = contract_data["contract_number"]
            contract.check_in_date = contract_data["check_in_date"]
            contract.check_out_date = contract_data.get("check_out_date")
            contract.status = contract_data.get("status", contract.status)

            if old_room_id != contract.room_id:
                old_room = self.db.query(Room).filter(Room.id == old_room_id).first()
                if old_room:
                    old_room.current_occupancy -= 1

                new_room = self.db.query(Room).filter(Room.id == contract.room_id).first()
                if new_room:
                    new_room.current_occupancy += 1

            elif old_status != contract.status:
                room = self.db.query(Room).filter(Room.id == contract.room_id).first()
                if contract.status == "completed" or contract.status == "terminated":
                    if room:
                        room.current_occupancy -= 1
                elif old_status in ["completed", "terminated"] and contract.status == "active":
                    if room:
                        room.current_occupancy += 1

            self.db.commit()
            self.db.refresh(contract)
        return contract

    def terminate_contract(self, contract_id):
        contract = self.get_contract_by_id(contract_id)
        if contract and contract.status == "active":
            contract.status = "terminated"
            contract.check_out_date = date.today()

            room = self.db.query(Room).filter(Room.id == contract.room_id).first()
            if room:
                room.current_occupancy -= 1

            self.db.commit()
            self.db.refresh(contract)
        return contract

    def delete_contract(self, contract_id):
        contract = self.get_contract_by_id(contract_id)
        if contract:
            if contract.status == "active":
                room = self.db.query(Room).filter(Room.id == contract.room_id).first()
                if room:
                    room.current_occupancy -= 1

            self.db.delete(contract)
            self.db.commit()
            return True
        return False

    def generate_contract_number(self):
        year = date.today().year
        month = date.today().month
        count = self.db.query(Contract).count() + 1
        return f"K{year}{month:02d}-{count:04d}"

    def __del__(self):
        self.db.close()