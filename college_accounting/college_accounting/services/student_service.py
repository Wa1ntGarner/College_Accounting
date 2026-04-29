from sqlalchemy.orm import Session
from models import Student
from database import SessionLocal


class StudentService:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_students(self):
        return self.db.query(Student).order_by(Student.last_name, Student.first_name).all()

    def get_student_by_id(self, student_id):
        return self.db.query(Student).filter(Student.id == student_id).first()

    def create_student(self, student_data):
        student = Student(
            first_name=student_data["first_name"],
            last_name=student_data["last_name"],
            student_card_number=student_data["student_card_number"],
            phone=student_data.get("phone", ""),
            faculty=student_data.get("faculty", ""),
            group_name=student_data.get("group_name", "")
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def update_student(self, student_id, student_data):
        student = self.get_student_by_id(student_id)
        if student:
            student.first_name = student_data["first_name"]
            student.last_name = student_data["last_name"]
            student.student_card_number = student_data["student_card_number"]
            student.phone = student_data.get("phone", "")
            student.faculty = student_data.get("faculty", "")
            student.group_name = student_data.get("group_name", "")
            self.db.commit()
            self.db.refresh(student)
        return student

    def delete_student(self, student_id):
        student = self.get_student_by_id(student_id)
        if student:
            self.db.delete(student)
            self.db.commit()
            return True
        return False

    def __del__(self):
        self.db.close()