import bcrypt
from datetime import date
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal


class UserService:
    def __init__(self):
        self.db = SessionLocal()

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password, password_hash):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def create_user(self, username, password, role="admin"):
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            return None

        user = User(
            username=username,
            password_hash=self.hash_password(password),
            role=role,
            created_at=date.today()
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username, password):
        user = self.db.query(User).filter(User.username == username).first()
        if user and self.verify_password(password, user.password_hash):
            return user
        return None

    def get_user_by_id(self, user_id):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_all_users(self):
        return self.db.query(User).order_by(User.username).all()

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    def create_default_admin(self):
        admin = self.db.query(User).filter(User.username == "admin").first()
        if not admin:
            self.create_user("admin", "admin123", "super_admin")
            print("Создан супер-админ по умолчанию: admin / admin123")

    def __del__(self):
        self.db.close()