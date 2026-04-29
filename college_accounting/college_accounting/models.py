from sqlalchemy import Column, Integer, String, Date, ForeignKey, DECIMAL, CheckConstraint, Boolean
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="admin")
    is_active = Column(Boolean, default=True)
    created_at = Column(Date)

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'super_admin')", name='check_user_role'),
    )


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    student_card_number = Column(String(20), unique=True, nullable=False)
    phone = Column(String(15))
    faculty = Column(String(100))
    group_name = Column(String(20))

    contracts = relationship("Contract", back_populates="student", cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(10), unique=True, nullable=False)
    floor = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    current_occupancy = Column(Integer, default=0)
    monthly_price = Column(DECIMAL(10, 2), nullable=False)

    contracts = relationship("Contract", back_populates="room", cascade="all, delete-orphan")
    equipment = relationship("Equipment", back_populates="room", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('current_occupancy <= capacity', name='check_occupancy_not_exceed_capacity'),
    )


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    contract_number = Column(String(50), unique=True, nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date)
    status = Column(String(20), default="active")

    student = relationship("Student", back_populates="contracts")
    room = relationship("Room", back_populates="contracts")
    payments = relationship("Payment", back_populates="contract", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed', 'terminated')",
            name="check_contract_status"
        ),
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_period_month = Column(Integer, nullable=False)
    payment_period_year = Column(Integer, nullable=False)

    contract = relationship("Contract", back_populates="payments")

    __table_args__ = (
        CheckConstraint('payment_period_month BETWEEN 1 AND 12', name='check_month_range'),
    )


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    condition = Column(String(50), default="good")

    room = relationship("Room", back_populates="equipment")

    __table_args__ = (
        CheckConstraint("condition IN ('good', 'needs_repair', 'broken')", name='check_equipment_condition'),
    )