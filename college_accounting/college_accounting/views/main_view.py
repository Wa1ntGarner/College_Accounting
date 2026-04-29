import flet as ft
from datetime import date, datetime, timedelta
from services.student_service import StudentService
from services.user_service import UserService
from services.room_service import RoomService
from services.contract_service import ContractService
from services.payment_service import PaymentService
from services.equipment_service import EquipmentService


class MainView:
    def __init__(self, page: ft.Page, current_user):
        self.page = page
        self.current_view = "students"
        self.current_user = current_user
        self.student_service = StudentService()
        self.user_service = UserService()
        self.room_service = RoomService()
        self.contract_service = ContractService()
        self.payment_service = PaymentService()
        self.equipment_service = EquipmentService()
        self.all_students = []
        self.all_rooms = []
        self.room_search_field = None
        self.room_floor_dropdown = None
        self.room_occupancy_dropdown = None
        self.rooms_table = None

    def show_overdue_notifications(self, overdue_contracts):
        def refresh_notifications(e=None):
            new_overdue = self.payment_service.get_overdue_contracts()
            self.show_overdue_notifications(new_overdue)

        notification_items = []

        for item in overdue_contracts:
            contract = item["contract"]
            student = contract.student
            room = contract.room

            notification_items.append(
                ft.ListTile(
                    title=ft.Text(f"{student.last_name} {student.first_name}"),
                    subtitle=ft.Text(
                        f"Комната {room.room_number}, просрочка {item['months_overdue']} мес."
                    ),
                    trailing=ft.Text(
                        f"{float(room.monthly_price) * item['months_overdue']} руб.",
                        color="#F44336",
                    ),
                )
            )

        def close_notifications(e):
            self.switch_view("students")
            self.page.update()

        notifications_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Просроченные платежи",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#F44336",
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Обновить", on_click=refresh_notifications
                                ),
                                ft.TextButton("Закрыть", on_click=close_notifications),
                            ],
                            spacing=10,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                (
                    ft.Column(notification_items, scroll=ft.ScrollMode.AUTO)
                    if notification_items
                    else ft.Text("Нет просроченных платежей", color="#4CAF50", size=16)
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

        self.content_container.content = notifications_view
        self.page.update()

    def build(self):
        overdue_contracts = self.payment_service.get_overdue_contracts()
        overdue_count = len(overdue_contracts)

        self.content_container = ft.Container(
            content=self.get_students_view(),
            expand=True,
            padding=20,
        )

        sidebar_buttons = [
            ft.Text("Меню", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Пользователь: {self.current_user.username}", size=12),
        ]

        if overdue_count > 0:
            sidebar_buttons.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                f"Просрочено: {overdue_count}", color="#F44336", size=14
                            ),
                        ],
                        spacing=5,
                    ),
                    padding=10,
                    border_radius=5,
                    bgcolor="#FFEBEE",
                    on_click=lambda e: self.show_overdue_notifications(
                        overdue_contracts
                    ),
                )
            )

        sidebar_buttons.extend(
            [
                ft.Divider(),
                ft.ElevatedButton(
                    "Студенты",
                    on_click=lambda e: self.switch_view("students"),
                    width=200,
                ),
                ft.ElevatedButton(
                    "Комнаты",
                    on_click=lambda e: self.switch_view("rooms"),
                    width=200,
                ),
                ft.ElevatedButton(
                    "Контракты",
                    on_click=lambda e: self.switch_view("contracts"),
                    width=200,
                ),
                ft.ElevatedButton(
                    "Платежи",
                    on_click=lambda e: self.switch_view("payments"),
                    width=200,
                ),
                ft.ElevatedButton(
                    "Оборудование",
                    on_click=lambda e: self.switch_view("equipment"),
                    width=200,
                ),
            ]
        )

        if self.current_user.role == "super_admin":
            sidebar_buttons.append(
                ft.ElevatedButton(
                    "Пользователи",
                    on_click=lambda e: self.switch_view("users"),
                    width=200,
                )
            )
            sidebar_buttons.append(
                ft.ElevatedButton(
                    "Отчеты",
                    on_click=lambda e: self.switch_view("reports"),
                    width=200,
                )
            )

        sidebar_buttons.extend(
            [
                ft.Divider(),
                ft.ElevatedButton(
                    "Выйти",
                    on_click=self.logout,
                    width=200,
                    bgcolor="#ff4f42",
                ),
            ]
        )

        sidebar = ft.Column(
            sidebar_buttons,
            spacing=10,
        )

        return ft.Row(
            [
                ft.Container(
                    content=sidebar,
                    padding=20,
                    bgcolor="#ECEFF1",
                ),
                ft.VerticalDivider(width=1),
                self.content_container,
            ],
            expand=True,
        )

    def switch_view(self, view_name):
        self.current_view = view_name
        if view_name == "students":
            self.content_container.content = self.get_students_view()
        elif view_name == "rooms":
            self.content_container.content = self.get_rooms_view()
        elif view_name == "contracts":
            self.content_container.content = self.get_contracts_view()
        elif view_name == "payments":
            self.content_container.content = self.get_payments_view()
        elif view_name == "equipment":
            self.content_container.content = self.get_equipment_view()
        elif view_name == "users":
            self.content_container.content = self.get_users_view()
        elif view_name == "reports":
            self.content_container.content = self.get_reports_view()
        self.page.update()

    def logout(self, e):
        from views.login_view import LoginView

        def on_login_success(user):
            self.page.clean()
            main_view = MainView(self.page, user)
            self.page.add(main_view.build())

        self.page.clean()
        login_view = LoginView(self.page, on_login_success)
        self.page.add(login_view.build())

    def get_users_view(self):
        users = self.user_service.get_all_users()

        self.users_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Логин")),
                ft.DataColumn(ft.Text("Роль")),
                ft.DataColumn(ft.Text("Дата создания")),
                ft.DataColumn(ft.Text("Действия")),
            ],
            rows=self._build_user_rows(users),
        )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Управление пользователями",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.ElevatedButton(
                            "Добавить администратора",
                            on_click=self.open_add_admin_dialog,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Column(
                    [self.users_table],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def _build_user_rows(self, users):
        rows = []
        for user in users:
            delete_button = None
            if user.role != "super_admin" and user.id != self.current_user.id:
                delete_button = ft.TextButton(
                    "Удалить", data=user.id, on_click=self.delete_user
                )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(user.id))),
                        ft.DataCell(ft.Text(user.username)),
                        ft.DataCell(ft.Text(user.role)),
                        ft.DataCell(
                            ft.Text(str(user.created_at) if user.created_at else "-")
                        ),
                        ft.DataCell(ft.Row([delete_button] if delete_button else [])),
                    ]
                )
            )
        return rows

    def open_add_admin_dialog(self, e):
        username_field = ft.TextField(
            label="Логин",
            width=300,
        )
        password_field = ft.TextField(
            label="Пароль",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        confirm_password_field = ft.TextField(
            label="Подтвердите пароль",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        error_text = ft.Text("", color="#F44336")

        def save_admin(e):
            username = username_field.value
            password = password_field.value
            confirm = confirm_password_field.value

            if not username or not password:
                error_text.value = "Введите логин и пароль"
                self.page.update()
                return

            if password != confirm:
                error_text.value = "Пароли не совпадают"
                self.page.update()
                return

            if len(password) < 6:
                error_text.value = "Пароль должен быть не менее 6 символов"
                self.page.update()
                return

            user = self.user_service.create_user(username, password, "admin")
            if user:
                self.content_container.content = self.get_users_view()
                self.page.update()
            else:
                error_text.value = "Пользователь с таким логином уже существует"
                self.page.update()

        def cancel_add(e):
            self.content_container.content = self.get_users_view()
            self.page.update()

        form_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Добавить администратора",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                username_field,
                password_field,
                confirm_password_field,
                error_text,
                ft.Row(
                    [
                        ft.ElevatedButton("Сохранить", on_click=save_admin),
                        ft.TextButton("Отмена", on_click=cancel_add),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

        self.content_container.content = form_view
        self.page.update()

    def delete_user(self, e):
        user_id = e.control.data

        def confirm_delete(e):
            self.user_service.delete_user(user_id)
            self.content_container.content = self.get_users_view()
            self.page.update()

        def cancel_delete(e):
            self.content_container.content = self.get_users_view()
            self.page.update()

        confirm_view = ft.Column(
            [
                ft.Text("Подтверждение удаления", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Вы уверены что хотите удалить этого пользователя?"),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Удалить", on_click=confirm_delete, bgcolor="#F44336"
                        ),
                        ft.TextButton("Отмена", on_click=cancel_delete),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        )

        self.content_container.content = confirm_view
        self.page.update()

    def get_students_view(self):
        students = self.student_service.get_all_students()
        self.all_students = students

        search_field = ft.TextField(
            label="Поиск по фамилии, имени или номеру билета",
            width=400,
            on_change=self.filter_students,
        )

        self.students_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Фамилия")),
                ft.DataColumn(ft.Text("Имя")),
                ft.DataColumn(ft.Text("Номер билета")),
                ft.DataColumn(ft.Text("Телефон")),
                ft.DataColumn(ft.Text("Факультет")),
                ft.DataColumn(ft.Text("Группа")),
                ft.DataColumn(ft.Text("Действия")),
            ],
            rows=self._build_student_rows(students),
        )

        header_row = [
            ft.Text("Список студентов", size=20, weight=ft.FontWeight.BOLD),
        ]

        if self.current_user.role == "super_admin":
            header_row.append(
                ft.ElevatedButton(
                    "Добавить студента", on_click=self.open_student_dialog
                )
            )

        return ft.Column(
            [
                ft.Row(
                    header_row,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                search_field,
                ft.Divider(),
                ft.Column(
                    [self.students_table],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def filter_students(self, e):
        search_text = e.control.value.lower()

        filtered_students = []
        for student in self.all_students:
            if (
                search_text in student.last_name.lower()
                or search_text in student.first_name.lower()
                or search_text in student.student_card_number.lower()
            ):
                filtered_students.append(student)

        self.students_table.rows = self._build_student_rows(filtered_students)
        self.page.update()

    def _build_student_rows(self, students):
        rows = []
        for student in students:
            action_buttons = []

            if self.current_user.role == "super_admin":
                action_buttons.extend(
                    [
                        ft.TextButton(
                            "Редактировать", data=student.id, on_click=self.edit_student
                        ),
                        ft.TextButton(
                            "Удалить", data=student.id, on_click=self.delete_student
                        ),
                    ]
                )
            else:
                action_buttons.append(
                    ft.TextButton(
                        "Редактировать", data=student.id, on_click=self.edit_student
                    )
                )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(student.id))),
                        ft.DataCell(ft.Text(student.last_name)),
                        ft.DataCell(ft.Text(student.first_name)),
                        ft.DataCell(ft.Text(student.student_card_number)),
                        ft.DataCell(ft.Text(student.phone or "-")),
                        ft.DataCell(ft.Text(student.faculty or "-")),
                        ft.DataCell(ft.Text(student.group_name or "-")),
                        ft.DataCell(ft.Row(action_buttons)),
                    ]
                )
            )
        return rows

    def open_student_dialog(self, e, student_id=None):
        student = None
        if student_id:
            student = self.student_service.get_student_by_id(student_id)

        first_name_field = ft.TextField(
            label="Имя",
            value=student.first_name if student else "",
        )
        last_name_field = ft.TextField(
            label="Фамилия",
            value=student.last_name if student else "",
        )
        card_number_field = ft.TextField(
            label="Номер студенческого билета",
            value=student.student_card_number if student else "",
        )
        phone_field = ft.TextField(
            label="Телефон",
            value=student.phone if student else "",
        )
        faculty_field = ft.TextField(
            label="Факультет",
            value=student.faculty if student else "",
        )
        group_field = ft.TextField(
            label="Группа",
            value=student.group_name if student else "",
        )

        def save_student(e):
            data = {
                "first_name": first_name_field.value,
                "last_name": last_name_field.value,
                "student_card_number": card_number_field.value,
                "phone": phone_field.value,
                "faculty": faculty_field.value,
                "group_name": group_field.value,
            }

            if student_id:
                self.student_service.update_student(student_id, data)
            else:
                self.student_service.create_student(data)

            self.content_container.content = self.get_students_view()
            self.page.update()

        def cancel_edit(e):
            self.content_container.content = self.get_students_view()
            self.page.update()

        form_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            (
                                "Редактировать студента"
                                if student_id
                                else "Добавить студента"
                            ),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                first_name_field,
                last_name_field,
                card_number_field,
                phone_field,
                faculty_field,
                group_field,
                ft.Row(
                    [
                        ft.ElevatedButton("Сохранить", on_click=save_student),
                        ft.TextButton("Отмена", on_click=cancel_edit),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

        self.content_container.content = form_view
        self.page.update()

    def edit_student(self, e):
        student_id = e.control.data
        self.open_student_dialog(e, student_id)

    def delete_student(self, e):
        student_id = e.control.data

        def confirm_delete(e):
            self.student_service.delete_student(student_id)
            self.content_container.content = self.get_students_view()
            self.page.update()

        def cancel_delete(e):
            self.content_container.content = self.get_students_view()
            self.page.update()

        confirm_view = ft.Column(
            [
                ft.Text("Подтверждение удаления", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Вы уверены что хотите удалить этого студента?"),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Удалить", on_click=confirm_delete, bgcolor="#F44336"
                        ),
                        ft.TextButton("Отмена", on_click=cancel_delete),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        )

        self.content_container.content = confirm_view
        self.page.update()

    def refresh_students_table(self):
        students = self.student_service.get_all_students()
        self.students_table.rows = self._build_student_rows(students)
        self.page.update()

    def get_rooms_view(self):
        print("=== get_rooms_view вызван ===")
        rooms = self.room_service.get_all_rooms()
        self.all_rooms = rooms
        print(f"Загружено комнат: {len(rooms)}")

        self.room_search_field = ft.TextField(
            label="Поиск по номеру",
            width=200,
        )

        floors = sorted(set(r.floor for r in rooms))
        floor_options = [ft.dropdown.Option(key="all", text="Все этажи")]
        for floor in floors:
            floor_options.append(
                ft.dropdown.Option(key=str(floor), text=f"{floor} этаж")
            )

        self.room_floor_dropdown = ft.Dropdown(
            label="Фильтр по этажу",
            options=floor_options,
            value="all",
            width=200,
        )

        self.room_occupancy_dropdown = ft.Dropdown(
            label="Наличие мест",
            options=[
                ft.dropdown.Option(key="all", text="Все комнаты"),
                ft.dropdown.Option(key="free", text="Есть свободные"),
                ft.dropdown.Option(key="full", text="Заполненные"),
            ],
            value="all",
            width=200,
        )

        apply_button = ft.ElevatedButton(
            "Применить фильтр", on_click=self.apply_room_filter
        )

        reset_button = ft.TextButton("Сбросить", on_click=self.reset_room_filter)

        filter_row = ft.Row(
            [
                self.room_search_field,
                self.room_floor_dropdown,
                self.room_occupancy_dropdown,
                apply_button,
                reset_button,
            ],
            spacing=10,
        )

        self.rooms_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Номер")),
                ft.DataColumn(ft.Text("Этаж")),
                ft.DataColumn(ft.Text("Вместимость")),
                ft.DataColumn(ft.Text("Занято")),
                ft.DataColumn(ft.Text("Свободно")),
                ft.DataColumn(ft.Text("Цена/мес")),
                ft.DataColumn(ft.Text("Действия")),
            ],
            rows=self._build_room_rows(rooms),
        )

        header_row = [
            ft.Text("Список комнат", size=20, weight=ft.FontWeight.BOLD),
        ]

        if self.current_user.role == "super_admin":
            header_row.append(
                ft.ElevatedButton("Добавить комнату", on_click=self.open_room_dialog)
            )

        return ft.Column(
            [
                ft.Row(
                    header_row,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                filter_row,
                ft.Divider(),
                ft.Column(
                    [self.rooms_table],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def apply_room_filter(self, e):
        print("=== apply_room_filter вызван ===")

        search_text = (
            self.room_search_field.value.lower() if self.room_search_field.value else ""
        )
        floor_filter = (
            self.room_floor_dropdown.value if self.room_floor_dropdown else "all"
        )
        occupancy_filter = (
            self.room_occupancy_dropdown.value
            if self.room_occupancy_dropdown
            else "all"
        )

        print(f"Поиск: '{search_text}'")
        print(f"Этаж: '{floor_filter}'")
        print(f"Места: '{occupancy_filter}'")

        filtered_rooms = []
        for room in self.all_rooms:
            if search_text and search_text not in room.room_number.lower():
                continue

            if floor_filter != "all" and floor_filter is not None:
                if str(room.floor) != str(floor_filter):
                    continue

            if occupancy_filter == "free" and room.current_occupancy >= room.capacity:
                continue
            if occupancy_filter == "full" and room.current_occupancy < room.capacity:
                continue

            filtered_rooms.append(room)

        print(f"Отфильтровано комнат: {len(filtered_rooms)} из {len(self.all_rooms)}")

        self.rooms_table.rows = self._build_room_rows(filtered_rooms)
        self.page.update()

    def reset_room_filter(self, e):
        self.room_search_field.value = ""
        self.room_floor_dropdown.value = "all"
        self.room_occupancy_dropdown.value = "all"
        self.rooms_table.rows = self._build_room_rows(self.all_rooms)
        self.page.update()

    def _build_room_rows(self, rooms):
        rows = []
        for room in rooms:
            free_spaces = room.capacity - room.current_occupancy
            occupancy_color = "#4CAF50" if free_spaces > 0 else "#F44336"

            action_buttons = []

            if self.current_user.role == "super_admin":
                action_buttons.extend(
                    [
                        ft.TextButton(
                            "Редактировать", data=room.id, on_click=self.edit_room
                        ),
                        ft.TextButton(
                            "Удалить", data=room.id, on_click=self.delete_room
                        ),
                    ]
                )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(room.id))),
                        ft.DataCell(ft.Text(room.room_number)),
                        ft.DataCell(ft.Text(str(room.floor))),
                        ft.DataCell(ft.Text(str(room.capacity))),
                        ft.DataCell(ft.Text(str(room.current_occupancy))),
                        ft.DataCell(ft.Text(str(free_spaces), color=occupancy_color)),
                        ft.DataCell(ft.Text(f"{room.monthly_price} руб.")),
                        ft.DataCell(
                            ft.Row(action_buttons) if action_buttons else ft.Text("-")
                        ),
                    ]
                )
            )
        return rows

    def open_room_dialog(self, e, room_id=None):
        room = None
        if room_id:
            room = self.room_service.get_room_by_id(room_id)

        room_number_field = ft.TextField(
            label="Номер комнаты",
            value=room.room_number if room else "",
        )
        floor_field = ft.TextField(
            label="Этаж",
            value=str(room.floor) if room else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        capacity_field = ft.TextField(
            label="Вместимость",
            value=str(room.capacity) if room else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        price_field = ft.TextField(
            label="Цена за месяц",
            value=str(room.monthly_price) if room else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        error_text = ft.Text("", color="#F44336")

        def save_room(e):
            if not room_number_field.value:
                error_text.value = "Введите номер комнаты"
                self.page.update()
                return

            try:
                floor = int(floor_field.value) if floor_field.value else 0
                capacity = int(capacity_field.value) if capacity_field.value else 0
                price = float(price_field.value) if price_field.value else 0
            except ValueError:
                error_text.value = "Проверьте числовые поля"
                self.page.update()
                return

            if capacity <= 0:
                error_text.value = "Вместимость должна быть больше 0"
                self.page.update()
                return

            if price <= 0:
                error_text.value = "Цена должна быть больше 0"
                self.page.update()
                return

            data = {
                "room_number": room_number_field.value,
                "floor": floor,
                "capacity": capacity,
                "current_occupancy": room.current_occupancy if room else 0,
                "monthly_price": price,
            }

            if room_id:
                self.room_service.update_room(room_id, data)
            else:
                self.room_service.create_room(data)

            self.content_container.content = self.get_rooms_view()
            self.page.update()

        def cancel_edit(e):
            self.content_container.content = self.get_rooms_view()
            self.page.update()

        form_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Редактировать комнату" if room_id else "Добавить комнату",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                room_number_field,
                floor_field,
                capacity_field,
                price_field,
                error_text,
                ft.Row(
                    [
                        ft.ElevatedButton("Сохранить", on_click=save_room),
                        ft.TextButton("Отмена", on_click=cancel_edit),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

        self.content_container.content = form_view
        self.page.update()

    def edit_room(self, e):
        room_id = e.control.data
        self.open_room_dialog(e, room_id)

    def delete_room(self, e):
        room_id = e.control.data
        room = self.room_service.get_room_by_id(room_id)

        if room.current_occupancy > 0:

            def close_error(e):
                self.content_container.content = self.get_rooms_view()
                self.page.update()

            error_view = ft.Column(
                [
                    ft.Text(
                        "Ошибка удаления",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#F44336",
                    ),
                    ft.Divider(),
                    ft.Text(
                        f"Невозможно удалить комнату {room.room_number}. В комнате проживают студенты."
                    ),
                    ft.Row(
                        [
                            ft.TextButton("OK", on_click=close_error),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
            )

            self.content_container.content = error_view
            self.page.update()
            return

        def confirm_delete(e):
            self.room_service.delete_room(room_id)
            self.content_container.content = self.get_rooms_view()
            self.page.update()

        def cancel_delete(e):
            self.content_container.content = self.get_rooms_view()
            self.page.update()

        confirm_view = ft.Column(
            [
                ft.Text("Подтверждение удаления", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(f"Вы уверены что хотите удалить комнату {room.room_number}?"),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Удалить", on_click=confirm_delete, bgcolor="#F44336"
                        ),
                        ft.TextButton("Отмена", on_click=cancel_delete),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        )

        self.content_container.content = confirm_view
        self.page.update()

    def get_contracts_view(self):
        contracts = self.contract_service.get_all_contracts()

        self.contracts_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Номер")),
                ft.DataColumn(ft.Text("Студент")),
                ft.DataColumn(ft.Text("Комната")),
                ft.DataColumn(ft.Text("Заезд")),
                ft.DataColumn(ft.Text("Выезд")),
                ft.DataColumn(ft.Text("Статус")),
                ft.DataColumn(ft.Text("Действия")),
            ],
            rows=self._build_contract_rows(contracts),
        )

        header_row = [
            ft.Text("Список контрактов", size=20, weight=ft.FontWeight.BOLD),
        ]

        if self.current_user.role == "super_admin":
            header_row.append(
                ft.ElevatedButton(
                    "Добавить контракт", on_click=self.open_contract_dialog
                )
            )

        return ft.Column(
            [
                ft.Row(
                    header_row,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Column(
                    [self.contracts_table],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def _build_contract_rows(self, contracts):
        rows = []
        for contract in contracts:
            student = contract.student
            room = contract.room
            student_name = (
                f"{student.last_name} {student.first_name}" if student else "-"
            )
            room_number = room.room_number if room else "-"

            status_color = "#4CAF50"
            if contract.status == "completed":
                status_color = "#2196F3"
            elif contract.status == "terminated":
                status_color = "#F44336"

            status_text = {
                "active": "Активен",
                "completed": "Завершен",
                "terminated": "Расторгнут",
            }.get(contract.status, contract.status)

            action_buttons = []

            if self.current_user.role == "super_admin":
                action_buttons.append(
                    ft.TextButton(
                        "Редактировать", data=contract.id, on_click=self.edit_contract
                    )
                )

                if contract.status == "active":
                    action_buttons.append(
                        ft.TextButton(
                            "Завершить",
                            data=contract.id,
                            on_click=self.terminate_contract,
                        )
                    )

                action_buttons.append(
                    ft.TextButton(
                        "Удалить", data=contract.id, on_click=self.delete_contract
                    )
                )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(contract.id))),
                        ft.DataCell(ft.Text(contract.contract_number)),
                        ft.DataCell(ft.Text(student_name)),
                        ft.DataCell(ft.Text(room_number)),
                        ft.DataCell(ft.Text(str(contract.check_in_date))),
                        ft.DataCell(
                            ft.Text(
                                str(contract.check_out_date)
                                if contract.check_out_date
                                else "-"
                            )
                        ),
                        ft.DataCell(ft.Text(status_text, color=status_color)),
                        ft.DataCell(
                            ft.Row(action_buttons) if action_buttons else ft.Text("-")
                        ),
                    ]
                )
            )
        return rows

    def open_contract_dialog(self, e, contract_id=None):
        contract = None
        if contract_id:
            contract = self.contract_service.get_contract_by_id(contract_id)

        students = self.student_service.get_all_students()
        rooms = self.room_service.get_available_rooms()

        if contract and contract.status == "active":
            current_room = self.room_service.get_room_by_id(contract.room_id)
            if current_room and current_room not in rooms:
                rooms.append(current_room)

        student_options = []
        for student in students:
            student_options.append(
                ft.dropdown.Option(
                    key=str(student.id),
                    text=f"{student.last_name} {student.first_name} ({student.student_card_number})",
                )
            )

        room_options = []
        for room in rooms:
            free_spaces = room.capacity - room.current_occupancy
            room_options.append(
                ft.dropdown.Option(
                    key=str(room.id),
                    text=f"{room.room_number} (свободно: {free_spaces}, цена: {room.monthly_price} руб.)",
                )
            )

        student_dropdown = ft.Dropdown(
            label="Студент",
            options=student_options,
            value=str(contract.student_id) if contract else None,
            width=400,
        )

        room_dropdown = ft.Dropdown(
            label="Комната",
            options=room_options,
            value=str(contract.room_id) if contract else None,
            width=400,
        )

        contract_number_field = ft.TextField(
            label="Номер контракта",
            value=(
                contract.contract_number
                if contract
                else self.contract_service.generate_contract_number()
            ),
            width=400,
        )

        check_in_date_field = ft.TextField(
            label="Дата заезда (ГГГГ-ММ-ДД)",
            value=str(contract.check_in_date) if contract else str(date.today()),
            width=400,
        )

        check_out_date_field = ft.TextField(
            label="Дата выезда (ГГГГ-ММ-ДД)",
            value=(
                str(contract.check_out_date)
                if contract and contract.check_out_date
                else ""
            ),
            width=400,
        )

        status_dropdown = ft.Dropdown(
            label="Статус",
            options=[
                ft.dropdown.Option(key="active", text="Активен"),
                ft.dropdown.Option(key="completed", text="Завершен"),
                ft.dropdown.Option(key="terminated", text="Расторгнут"),
            ],
            value=contract.status if contract else "active",
            width=400,
        )

        error_text = ft.Text("", color="#F44336")

        def save_contract(e):
            if not student_dropdown.value:
                error_text.value = "Выберите студента"
                self.page.update()
                return

            if not room_dropdown.value:
                error_text.value = "Выберите комнату"
                self.page.update()
                return

            if not contract_number_field.value:
                error_text.value = "Введите номер контракта"
                self.page.update()
                return

            try:
                check_in = (
                    date.fromisoformat(check_in_date_field.value)
                    if check_in_date_field.value
                    else date.today()
                )
            except ValueError:
                error_text.value = "Неверный формат даты заезда"
                self.page.update()
                return

            check_out = None
            if check_out_date_field.value:
                try:
                    check_out = date.fromisoformat(check_out_date_field.value)
                except ValueError:
                    error_text.value = "Неверный формат даты выезда"
                    self.page.update()
                    return

            student_id = int(student_dropdown.value)
            existing_active = self.contract_service.get_student_active_contract(
                student_id
            )
            if existing_active and (not contract or existing_active.id != contract.id):
                if status_dropdown.value == "active":
                    error_text.value = "У этого студента уже есть активный контракт"
                    self.page.update()
                    return

            room_id = int(room_dropdown.value)
            room = self.room_service.get_room_by_id(room_id)
            if room and room.current_occupancy >= room.capacity:
                if not contract or contract.room_id != room_id:
                    error_text.value = "В выбранной комнате нет свободных мест"
                    self.page.update()
                    return

            data = {
                "student_id": student_id,
                "room_id": room_id,
                "contract_number": contract_number_field.value,
                "check_in_date": check_in,
                "check_out_date": check_out,
                "status": status_dropdown.value,
            }

            if contract_id:
                self.contract_service.update_contract(contract_id, data)
            else:
                self.contract_service.create_contract(data)

            self.content_container.content = self.get_contracts_view()
            self.page.update()

        def cancel_edit(e):
            self.content_container.content = self.get_contracts_view()
            self.page.update()

        form_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            (
                                "Редактировать контракт"
                                if contract_id
                                else "Добавить контракт"
                            ),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                student_dropdown,
                room_dropdown,
                contract_number_field,
                check_in_date_field,
                check_out_date_field,
                status_dropdown,
                error_text,
                ft.Row(
                    [
                        ft.ElevatedButton("Сохранить", on_click=save_contract),
                        ft.TextButton("Отмена", on_click=cancel_edit),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            width=500,
        )

        self.content_container.content = form_view
        self.page.update()

    def edit_contract(self, e):
        contract_id = e.control.data
        self.open_contract_dialog(e, contract_id)

    def terminate_contract(self, e):
        contract_id = e.control.data

        def confirm_terminate(e):
            self.contract_service.terminate_contract(contract_id)
            self.content_container.content = self.get_contracts_view()
            self.page.update()

        def cancel_terminate(e):
            self.content_container.content = self.get_contracts_view()
            self.page.update()

        confirm_view = ft.Column(
            [
                ft.Text("Завершение контракта", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Вы уверены что хотите завершить этот контракт?"),
                ft.Row(
                    [
                        ft.ElevatedButton("Завершить", on_click=confirm_terminate),
                        ft.TextButton("Отмена", on_click=cancel_terminate),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        )

        self.content_container.content = confirm_view
        self.page.update()

    def delete_contract(self, e):
        contract_id = e.control.data

        def confirm_delete(e):
            self.contract_service.delete_contract(contract_id)
            self.content_container.content = self.get_contracts_view()
            self.page.update()

        def cancel_delete(e):
            self.content_container.content = self.get_contracts_view()
            self.page.update()

        confirm_view = ft.Column(
            [
                ft.Text("Подтверждение удаления", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Вы уверены что хотите удалить этот контракт?"),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Удалить", on_click=confirm_delete, bgcolor="#F44336"
                        ),
                        ft.TextButton("Отмена", on_click=cancel_delete),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        )

        self.content_container.content = confirm_view
        self.page.update()

    def get_payments_view(self):
        payments = self.payment_service.get_all_payments()

        self.payments_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Контракт")),
                ft.DataColumn(ft.Text("Студент")),
                ft.DataColumn(ft.Text("Дата платежа")),
                ft.DataColumn(ft.Text("Период")),
                ft.DataColumn(ft.Text("Сумма")),
                ft.DataColumn(ft.Text("Действия")),
            ],
            rows=self._build_payment_rows(payments),
        )

        header_row = [
            ft.Text("Список платежей", size=20, weight=ft.FontWeight.BOLD),
        ]

        if self.current_user.role in ["super_admin", "admin"]:
            header_row.append(
                ft.ElevatedButton("Добавить платеж", on_click=self.open_payment_dialog)
            )

        return ft.Column(
            [
                ft.Row(
                    header_row,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Column(
                    [self.payments_table],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def _build_payment_rows(self, payments):
        rows = []
        for payment in payments:
            contract = payment.contract
            student = contract.student if contract else None
            student_name = (
                f"{student.last_name} {student.first_name}" if student else "-"
            )
            contract_number = contract.contract_number if contract else "-"
            period = f"{payment.payment_period_month:02d}.{payment.payment_period_year}"

            action_buttons = []

            if self.current_user.role in ["super_admin", "admin"]:
                action_buttons.extend(
                    [
                        ft.TextButton(
                            "Редактировать", data=payment.id, on_click=self.edit_payment
                        ),
                        ft.TextButton(
                            "Удалить", data=payment.id, on_click=self.delete_payment
                        ),
                    ]
                )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(payment.id))),
                        ft.DataCell(ft.Text(contract_number)),
                        ft.DataCell(ft.Text(student_name)),
                        ft.DataCell(ft.Text(str(payment.payment_date))),
                        ft.DataCell(ft.Text(period)),
                        ft.DataCell(ft.Text(f"{payment.amount} руб.")),
                        ft.DataCell(
                            ft.Row(action_buttons) if action_buttons else ft.Text("-")
                        ),
                    ]
                )
            )
        return rows

    def open_payment_dialog(self, e, payment_id=None):
        payment = None
        if payment_id:
            payment = self.payment_service.get_payment_by_id(payment_id)

        contracts = self.contract_service.get_active_contracts()

        contract_options = []
        for contract in contracts:
            student = contract.student
            room = contract.room
            student_name = (
                f"{student.last_name} {student.first_name}" if student else "-"
            )
            room_number = room.room_number if room else "-"
            contract_options.append(
                ft.dropdown.Option(
                    key=str(contract.id),
                    text=f"{contract.contract_number} - {student_name} - комн. {room_number}",
                )
            )

        contract_dropdown = ft.Dropdown(
            label="Контракт",
            options=contract_options,
            value=str(payment.contract_id) if payment else None,
            width=400,
        )

        payment_date_field = ft.TextField(
            label="Дата платежа (ГГГГ-ММ-ДД)",
            value=str(payment.payment_date) if payment else str(date.today()),
            width=400,
        )

        amount_field = ft.TextField(
            label="Сумма",
            value=str(payment.amount) if payment else "",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=400,
        )

        month_field = ft.TextField(
            label="Месяц (1-12)",
            value=(
                str(payment.payment_period_month)
                if payment
                else str(date.today().month)
            ),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=400,
        )

        year_field = ft.TextField(
            label="Год",
            value=(
                str(payment.payment_period_year) if payment else str(date.today().year)
            ),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=400,
        )

        error_text = ft.Text("", color="#F44336")

        def save_payment(e):
            if not contract_dropdown.value:
                error_text.value = "Выберите контракт"
                self.page.update()
                return

            if not amount_field.value:
                error_text.value = "Введите сумму"
                self.page.update()
                return

            try:
                payment_date = (
                    date.fromisoformat(payment_date_field.value)
                    if payment_date_field.value
                    else date.today()
                )
                amount = float(amount_field.value)
                month = int(month_field.value)
                year = int(year_field.value)
            except ValueError:
                error_text.value = "Проверьте числовые поля и формат даты"
                self.page.update()
                return

            if amount <= 0:
                error_text.value = "Сумма должна быть больше 0"
                self.page.update()
                return

            if month < 1 or month > 12:
                error_text.value = "Месяц должен быть от 1 до 12"
                self.page.update()
                return

            if year < 2000 or year > 2100:
                error_text.value = "Введите корректный год"
                self.page.update()
                return

            data = {
                "contract_id": int(contract_dropdown.value),
                "payment_date": payment_date,
                "amount": amount,
                "payment_period_month": month,
                "payment_period_year": year,
            }

            if payment_id:
                self.payment_service.update_payment(payment_id, data)
            else:
                self.payment_service.create_payment(data)

            self.content_container.content = self.get_payments_view()
            self.page.update()

        def cancel_edit(e):
            self.content_container.content = self.get_payments_view()
            self.page.update()

        if not contracts:
            error_view = ft.Column(
                [
                    ft.Text("Добавление платежа", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(
                        "Нет активных контрактов для добавления платежа",
                        color="#F44336",
                    ),
                    ft.Row(
                        [
                            ft.TextButton("Назад", on_click=cancel_edit),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
            )
            self.content_container.content = error_view
            self.page.update()
            return

        form_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Редактировать платеж" if payment_id else "Добавить платеж",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                contract_dropdown,
                payment_date_field,
                amount_field,
                month_field,
                year_field,
                error_text,
                ft.Row(
                    [
                        ft.ElevatedButton("Сохранить", on_click=save_payment),
                        ft.TextButton("Отмена", on_click=cancel_edit),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            width=500,
        )

        self.content_container.content = form_view
        self.page.update()

    def edit_payment(self, e):
        payment_id = e.control.data
        self.open_payment_dialog(e, payment_id)

    def delete_payment(self, e):
        payment_id = e.control.data

        def confirm_delete(e):
            self.payment_service.delete_payment(payment_id)
            self.content_container.content = self.get_payments_view()
            self.page.update()

        def cancel_delete(e):
            self.content_container.content = self.get_payments_view()
            self.page.update()

        confirm_view = ft.Column(
            [
                ft.Text("Подтверждение удаления", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Вы уверены что хотите удалить этот платеж?"),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Удалить", on_click=confirm_delete, bgcolor="#F44336"
                        ),
                        ft.TextButton("Отмена", on_click=cancel_delete),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        )

        self.content_container.content = confirm_view
        self.page.update()

    def get_equipment_view(self):
        equipment_list = self.equipment_service.get_all_equipment()

        self.equipment_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Комната")),
                ft.DataColumn(ft.Text("Название")),
                ft.DataColumn(ft.Text("Количество")),
                ft.DataColumn(ft.Text("Состояние")),
                ft.DataColumn(ft.Text("Действия")),
            ],
            rows=self._build_equipment_rows(equipment_list),
        )

        header_row = [
            ft.Text("Список оборудования", size=20, weight=ft.FontWeight.BOLD),
        ]

        if self.current_user.role in ["super_admin", "admin"]:
            header_row.append(
                ft.ElevatedButton(
                    "Добавить оборудование", on_click=self.open_equipment_dialog
                )
            )

        return ft.Column(
            [
                ft.Row(
                    header_row,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Column(
                    [self.equipment_table],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def _build_equipment_rows(self, equipment_list):
        rows = []
        for equipment in equipment_list:
            room = equipment.room
            room_number = room.room_number if room else "-"

            condition_text = {
                "good": "Хорошее",
                "needs_repair": "Требует ремонта",
                "broken": "Сломано",
            }.get(equipment.condition, equipment.condition)

            condition_color = {
                "good": "#4CAF50",
                "needs_repair": "#FF9800",
                "broken": "#F44336",
            }.get(equipment.condition, "#000000")

            action_buttons = []

            if self.current_user.role in ["super_admin", "admin"]:
                action_buttons.extend(
                    [
                        ft.TextButton(
                            "Редактировать",
                            data=equipment.id,
                            on_click=self.edit_equipment,
                        ),
                        ft.TextButton(
                            "Удалить", data=equipment.id, on_click=self.delete_equipment
                        ),
                    ]
                )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(equipment.id))),
                        ft.DataCell(ft.Text(room_number)),
                        ft.DataCell(ft.Text(equipment.name)),
                        ft.DataCell(ft.Text(str(equipment.quantity))),
                        ft.DataCell(ft.Text(condition_text, color=condition_color)),
                        ft.DataCell(
                            ft.Row(action_buttons) if action_buttons else ft.Text("-")
                        ),
                    ]
                )
            )
        return rows

    def open_equipment_dialog(self, e, equipment_id=None):
        equipment = None
        if equipment_id:
            equipment = self.equipment_service.get_equipment_by_id(equipment_id)

        rooms = self.room_service.get_all_rooms()

        room_options = []
        for room in rooms:
            room_options.append(
                ft.dropdown.Option(
                    key=str(room.id), text=f"{room.room_number} (этаж {room.floor})"
                )
            )

        room_dropdown = ft.Dropdown(
            label="Комната",
            options=room_options,
            value=str(equipment.room_id) if equipment else None,
            width=400,
        )

        name_field = ft.TextField(
            label="Название",
            value=equipment.name if equipment else "",
            width=400,
        )

        quantity_field = ft.TextField(
            label="Количество",
            value=str(equipment.quantity) if equipment else "1",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=400,
        )

        condition_dropdown = ft.Dropdown(
            label="Состояние",
            options=[
                ft.dropdown.Option(key="good", text="Хорошее"),
                ft.dropdown.Option(key="needs_repair", text="Требует ремонта"),
                ft.dropdown.Option(key="broken", text="Сломано"),
            ],
            value=equipment.condition if equipment else "good",
            width=400,
        )

        error_text = ft.Text("", color="#F44336")

        def save_equipment(e):
            if not room_dropdown.value:
                error_text.value = "Выберите комнату"
                self.page.update()
                return

            if not name_field.value:
                error_text.value = "Введите название оборудования"
                self.page.update()
                return

            try:
                quantity = int(quantity_field.value) if quantity_field.value else 1
            except ValueError:
                error_text.value = "Количество должно быть числом"
                self.page.update()
                return

            if quantity <= 0:
                error_text.value = "Количество должно быть больше 0"
                self.page.update()
                return

            data = {
                "room_id": int(room_dropdown.value),
                "name": name_field.value,
                "quantity": quantity,
                "condition": condition_dropdown.value,
            }

            if equipment_id:
                self.equipment_service.update_equipment(equipment_id, data)
            else:
                self.equipment_service.create_equipment(data)

            self.content_container.content = self.get_equipment_view()
            self.page.update()

        def cancel_edit(e):
            self.content_container.content = self.get_equipment_view()
            self.page.update()

        form_view = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            (
                                "Редактировать оборудование"
                                if equipment_id
                                else "Добавить оборудование"
                            ),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                room_dropdown,
                name_field,
                quantity_field,
                condition_dropdown,
                error_text,
                ft.Row(
                    [
                        ft.ElevatedButton("Сохранить", on_click=save_equipment),
                        ft.TextButton("Отмена", on_click=cancel_edit),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            width=500,
        )

        self.content_container.content = form_view
        self.page.update()

    def edit_equipment(self, e):
        equipment_id = e.control.data
        self.open_equipment_dialog(e, equipment_id)

    def delete_equipment(self, e):
        equipment_id = e.control.data

        def confirm_delete(e):
            self.equipment_service.delete_equipment(equipment_id)
            self.content_container.content = self.get_equipment_view()
            self.page.update()

        def cancel_delete(e):
            self.content_container.content = self.get_equipment_view()
            self.page.update()

        confirm_view = ft.Column(
            [
                ft.Text("Подтверждение удаления", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Вы уверены что хотите удалить это оборудование?"),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Удалить", on_click=confirm_delete, bgcolor="#F44336"
                        ),
                        ft.TextButton("Отмена", on_click=cancel_delete),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        )

        self.content_container.content = confirm_view
        self.page.update()

    def get_reports_view(self):
        start_date_field = ft.TextField(
            label="Начальная дата (ГГГГ-ММ-ДД)",
            value=str(date.today().replace(day=1)),
            width=200,
        )

        end_date_field = ft.TextField(
            label="Конечная дата (ГГГГ-ММ-ДД)",
            value=str(date.today()),
            width=200,
        )

        report_result = ft.Column()

        def generate_report(e):
            try:
                start_date = date.fromisoformat(start_date_field.value)
                end_date = date.fromisoformat(end_date_field.value)
            except ValueError:
                report_result.controls = [
                    ft.Text("Неверный формат даты", color="#F44336")
                ]
                self.page.update()
                return

            report = self.payment_service.get_payments_report(start_date, end_date)
            payments = report["payments"]

            payment_rows = []
            for payment in payments:
                contract = payment.contract
                student = contract.student if contract else None
                student_name = (
                    f"{student.last_name} {student.first_name}" if student else "-"
                )

                payment_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(payment.payment_date))),
                            ft.DataCell(ft.Text(student_name)),
                            ft.DataCell(
                                ft.Text(
                                    f"{payment.payment_period_month:02d}.{payment.payment_period_year}"
                                )
                            ),
                            ft.DataCell(ft.Text(f"{payment.amount} руб.")),
                        ]
                    )
                )

            report_result.controls = [
                ft.Divider(height=20),
                ft.Text(
                    f"Отчет за период с {start_date} по {end_date}",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(f"Всего платежей: {report['count']}"),
                ft.Text(
                    f"Общая сумма: {report['total_amount']} руб.",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(height=10),
            ]

            if payment_rows:
                report_result.controls.append(
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Дата")),
                            ft.DataColumn(ft.Text("Студент")),
                            ft.DataColumn(ft.Text("Период")),
                            ft.DataColumn(ft.Text("Сумма")),
                        ],
                        rows=payment_rows,
                    )
                )
            else:
                report_result.controls.append(
                    ft.Text("Платежи за выбранный период не найдены")
                )

            self.page.update()

        return ft.Column(
            [
                ft.Text("Отчеты по платежам", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row(
                    [
                        start_date_field,
                        end_date_field,
                        ft.ElevatedButton(
                            "Сформировать отчет", on_click=generate_report
                        ),
                    ],
                    spacing=10,
                ),
                report_result,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
