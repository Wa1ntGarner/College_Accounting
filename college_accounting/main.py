import flet as ft
from database import init_db
from views.login_view import LoginView
from views.main_view import MainView
from services.user_service import UserService


def main(page: ft.Page):
    page.title = "Учет общежития"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 1000
    page.window_min_height = 600

    user_service = UserService()
    user_service.create_default_admin()

    def on_login_success(user):
        page.clean()
        main_view = MainView(page, user)
        page.add(main_view.build())

    login_view = LoginView(page, on_login_success)
    page.add(login_view.build())


if __name__ == "__main__":
    init_db()
    ft.app(target=main)