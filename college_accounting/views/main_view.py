import flet as ft
from services.student_service import StudentService
from services.user_service import UserService


class MainView:
    def __init__(self, page: ft.Page, current_user):
        self.page = page
        self.current_view = "students"
        self.current_user = current_user
        self.student_service = StudentService()
        self.user_service = UserService()

    def build(self):
        self.content_container = ft.Container(
            content=self.get_students_view(),
            expand=True,
            padding=20,
        )

        sidebar_buttons = [
            ft.Text("Меню", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"Пользователь: {self.current_user.username}", size=12),
            ft.Text(f"Роль: {self.current_user.role}", size=12),
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

        if self.current_user.role == "super_admin":
            sidebar_buttons.append(
                ft.ElevatedButton(
                    "Пользователи",
                    on_click=lambda e: self.switch_view("users"),
                    width=200,
                )
            )

        sidebar_buttons.extend([
            ft.Divider(),
            ft.ElevatedButton(
                "Выйти",
                on_click=self.logout,
                width=200,
                bgcolor="#F44336",
            ),
        ])

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
                        ft.Text("Управление пользователями", size=20, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            "Добавить администратора",
                            on_click=self.open_add_admin_dialog
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Column(
                    [
                        self.users_table
                    ],
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
            if user.role != "super_admin":
                delete_button = ft.TextButton(
                    "Удалить",
                    data=user.id,
                    on_click=self.delete_user
                )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(user.id))),
                        ft.DataCell(ft.Text(user.username)),
                        ft.DataCell(ft.Text(user.role)),
                        ft.DataCell(ft.Text(str(user.created_at) if user.created_at else "-")),
                        ft.DataCell(
                            ft.Row(
                                [delete_button] if delete_button else []
                            )
                        ),
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
                        ft.Text("Добавить администратора", size=20, weight=ft.FontWeight.BOLD),
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
                        ft.ElevatedButton("Удалить", on_click=confirm_delete, bgcolor="#F44336"),
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
                    "Добавить студента",
                    on_click=self.open_student_dialog
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
                    [
                        self.students_table
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def _build_student_rows(self, students):
        rows = []
        for student in students:
            action_buttons = []

            if self.current_user.role == "super_admin":
                action_buttons.extend([
                    ft.TextButton("Ред.", data=student.id, on_click=self.edit_student),
                    ft.TextButton("Уд.", data=student.id, on_click=self.delete_student),
                ])
            else:
                action_buttons.append(
                    ft.TextButton("Ред.", data=student.id, on_click=self.edit_student)
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
                        ft.Text("Редактировать студента" if student_id else "Добавить студента", size=20,
                                weight=ft.FontWeight.BOLD),
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
                        ft.ElevatedButton("Удалить", on_click=confirm_delete, bgcolor="#F44336"),
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
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Список комнат", size=20, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            "Добавить комнату",
                            on_click=lambda e: print("Добавление комнаты")
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Text("Здесь будет таблица со списком комнат"),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def get_contracts_view(self):
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Список контрактов", size=20, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            "Добавить контракт",
                            on_click=lambda e: print("Добавление контракта")
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Text("Здесь будет таблица со списком контрактов"),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def get_payments_view(self):
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Список платежей", size=20, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            "Добавить платеж",
                            on_click=lambda e: print("Добавление платежа")
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Text("Здесь будет таблица со списком платежей"),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def get_equipment_view(self):
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Список оборудования", size=20, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            "Добавить оборудование",
                            on_click=lambda e: print("Добавление оборудования")
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Text("Здесь будет таблица со списком оборудования"),
            ],
            scroll=ft.ScrollMode.AUTO,
        )