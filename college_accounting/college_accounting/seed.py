from datetime import date, timedelta
from database import SessionLocal, init_db
from models import Student, Room, Contract, Payment, Equipment
from services.user_service import UserService


def seed_database():
    init_db()
    db = SessionLocal()

    user_service = UserService()
    user_service.create_default_admin()

    # existing_students = db.query(Student).count()
    # if existing_students > 0:
    #     print("База данных уже содержит данные. Пропускаем заполнение.")
    #     db.close()
    #     return

    students_data = [
        {
            "first_name": "Иван",
            "last_name": "Иванов",
            "student_card_number": "ST2024001",
            "phone": "+79161234567",
            "faculty": "Факультет информационных технологий",
            "group_name": "ИТ-21-1"
        },
        {
            "first_name": "Мария",
            "last_name": "Петрова",
            "student_card_number": "ST2024002",
            "phone": "+79161234568",
            "faculty": "Экономический факультет",
            "group_name": "ЭК-22-2"
        },
        {
            "first_name": "Алексей",
            "last_name": "Сидоров",
            "student_card_number": "ST2024003",
            "phone": "+79161234569",
            "faculty": "Юридический факультет",
            "group_name": "ЮР-23-1"
        },
        {
            "first_name": "Елена",
            "last_name": "Козлова",
            "student_card_number": "ST2024004",
            "phone": "+79161234570",
            "faculty": "Факультет информационных технологий",
            "group_name": "ИТ-21-2"
        },
        {
            "first_name": "Дмитрий",
            "last_name": "Новиков",
            "student_card_number": "ST2024005",
            "phone": "+79161234571",
            "faculty": "Инженерный факультет",
            "group_name": "ИН-22-1"
        },
        {
            "first_name": "Анна",
            "last_name": "Морозова",
            "student_card_number": "ST2024006",
            "phone": "+79161234572",
            "faculty": "Экономический факультет",
            "group_name": "ЭК-21-3"
        },
        {
            "first_name": "Сергей",
            "last_name": "Волков",
            "student_card_number": "ST2024007",
            "phone": "+79161234573",
            "faculty": "Факультет информационных технологий",
            "group_name": "ИТ-23-1"
        },
        {
            "first_name": "Ольга",
            "last_name": "Соколова",
            "student_card_number": "ST2024008",
            "phone": "+79161234574",
            "faculty": "Юридический факультет",
            "group_name": "ЮР-22-2"
        },
    ]

    students = []
    for data in students_data:
        student = Student(**data)
        db.add(student)
        students.append(student)
    db.commit()
    print(f"Добавлено {len(students)} студентов")

    rooms_data = [
        {"room_number": "101", "floor": 1, "capacity": 2, "current_occupancy": 0, "monthly_price": 5000},
        {"room_number": "102", "floor": 1, "capacity": 3, "current_occupancy": 0, "monthly_price": 4500},
        {"room_number": "103", "floor": 1, "capacity": 2, "current_occupancy": 0, "monthly_price": 5000},
        {"room_number": "201", "floor": 2, "capacity": 2, "current_occupancy": 0, "monthly_price": 5500},
        {"room_number": "202", "floor": 2, "capacity": 4, "current_occupancy": 0, "monthly_price": 4000},
        {"room_number": "203", "floor": 2, "capacity": 2, "current_occupancy": 0, "monthly_price": 5500},
        {"room_number": "301", "floor": 3, "capacity": 1, "current_occupancy": 0, "monthly_price": 7000},
        {"room_number": "302", "floor": 3, "capacity": 2, "current_occupancy": 0, "monthly_price": 6000},
        {"room_number": "303", "floor": 3, "capacity": 3, "current_occupancy": 0, "monthly_price": 5000},
        {"room_number": "401", "floor": 4, "capacity": 2, "current_occupancy": 0, "monthly_price": 6500},
    ]

    rooms = []
    for data in rooms_data:
        room = Room(**data)
        db.add(room)
        rooms.append(room)
    db.commit()
    print(f"Добавлено {len(rooms)} комнат")

    contracts_data = [
        {
            "student": students[0],
            "room": rooms[0],
            "contract_number": "K202409-0001",
            "check_in_date": date(2024, 9, 1),
            "status": "active"
        },
        {
            "student": students[1],
            "room": rooms[1],
            "contract_number": "K202409-0002",
            "check_in_date": date(2024, 9, 1),
            "status": "active"
        },
        {
            "student": students[2],
            "room": rooms[3],
            "contract_number": "K202409-0003",
            "check_in_date": date(2024, 9, 5),
            "status": "active"
        },
        {
            "student": students[3],
            "room": rooms[4],
            "contract_number": "K202409-0004",
            "check_in_date": date(2024, 9, 1),
            "status": "active"
        },
        {
            "student": students[4],
            "room": rooms[5],
            "contract_number": "K202409-0005",
            "check_in_date": date(2024, 9, 10),
            "status": "active"
        },
        {
            "student": students[5],
            "room": rooms[7],
            "contract_number": "K202408-0006",
            "check_in_date": date(2024, 8, 25),
            "check_out_date": date(2025, 1, 15),
            "status": "completed"
        },
        {
            "student": students[6],
            "room": rooms[8],
            "contract_number": "K202409-0007",
            "check_in_date": date(2024, 9, 1),
            "status": "active"
        },
    ]

    contracts = []
    for data in contracts_data:
        student = data.pop("student")
        room = data.pop("room")
        contract = Contract(
            student_id=student.id,
            room_id=room.id,
            **data
        )
        db.add(contract)
        contracts.append(contract)

        if contract.status == "active":
            room.current_occupancy += 1

    db.commit()
    print(f"Добавлено {len(contracts)} контрактов")

    payments_data = []

    for contract in contracts:
        if contract.status == "active":
            check_in = contract.check_in_date
            current_date = date.today()

            start_month = check_in.month
            start_year = check_in.year

            months_count = (current_date.year - start_year) * 12 + (current_date.month - start_month)

            if months_count > 2:
                months_count = 2

            for i in range(months_count + 1):
                payment_month = start_month + i
                payment_year = start_year

                if payment_month > 12:
                    payment_month -= 12
                    payment_year += 1

                payment_date = date(payment_year, payment_month, 10)

                payments_data.append({
                    "contract_id": contract.id,
                    "payment_date": payment_date,
                    "amount": float(contract.room.monthly_price),
                    "payment_period_month": payment_month,
                    "payment_period_year": payment_year,
                })

    for data in payments_data:
        payment = Payment(**data)
        db.add(payment)

    db.commit()
    print(f"Добавлено {len(payments_data)} платежей")

    equipment_data = [
        {"room_id": rooms[0].id, "name": "Кровать", "quantity": 2, "condition": "good"},
        {"room_id": rooms[0].id, "name": "Стол", "quantity": 2, "condition": "good"},
        {"room_id": rooms[0].id, "name": "Стул", "quantity": 2, "condition": "good"},
        {"room_id": rooms[1].id, "name": "Кровать", "quantity": 3, "condition": "good"},
        {"room_id": rooms[1].id, "name": "Стол", "quantity": 3, "condition": "needs_repair"},
        {"room_id": rooms[3].id, "name": "Кровать", "quantity": 2, "condition": "good"},
        {"room_id": rooms[3].id, "name": "Шкаф", "quantity": 1, "condition": "good"},
        {"room_id": rooms[4].id, "name": "Кровать", "quantity": 4, "condition": "good"},
        {"room_id": rooms[4].id, "name": "Стол", "quantity": 2, "condition": "good"},
        {"room_id": rooms[5].id, "name": "Кровать", "quantity": 2, "condition": "good"},
        {"room_id": rooms[5].id, "name": "Холодильник", "quantity": 1, "condition": "good"},
        {"room_id": rooms[7].id, "name": "Кровать", "quantity": 2, "condition": "broken"},
        {"room_id": rooms[8].id, "name": "Кровать", "quantity": 3, "condition": "good"},
    ]

    for data in equipment_data:
        equipment = Equipment(**data)
        db.add(equipment)

    db.commit()
    print(f"Добавлено {len(equipment_data)} единиц оборудования")

    db.close()
    print("\nБаза данных успешно заполнена тестовыми данными.")
    print("\nДанные для входа:")
    print("  Логин: admin")
    print("  Пароль: admin123")
    print("  Роль: супер-админ")


if __name__ == "__main__":
    seed_database()