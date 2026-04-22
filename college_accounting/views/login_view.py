import flet as ft
from services.user_service import UserService


class LoginView:
    def __init__(self, page: ft.Page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success
        self.user_service = UserService()

    def build(self):
        self.username_field = ft.TextField(
            label="Логин",
            width=300,
            on_submit=lambda e: self.login(None)
        )
        self.password_field = ft.TextField(
            label="Пароль",
            password=True,
            can_reveal_password=True,
            width=300,
            on_submit=lambda e: self.login(None)
        )
        self.error_text = ft.Text("", color="#F44336")

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Вход в систему", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Информационная система учета общежития", size=16),
                    ft.Divider(height=30),
                    self.username_field,
                    self.password_field,
                    self.error_text,
                    ft.ElevatedButton(
                        "Войти",
                        on_click=self.login,
                        width=300,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=50,
            alignment=ft.Alignment(0, 0),
            expand=True,
        )

    def login(self, e):
        username = self.username_field.value
        password = self.password_field.value

        if not username or not password:
            self.error_text.value = "Введите логин и пароль"
            self.page.update()
            return

        user = self.user_service.authenticate(username, password)
        if user:
            self.on_login_success(user)
        else:
            self.error_text.value = "Неверный логин или пароль"
            self.page.update()