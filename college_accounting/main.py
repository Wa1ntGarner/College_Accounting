import flet as ft
from database import init_db


def main(page: ft.Page):
    page.title = "Учет общежития"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 1000
    page.window_min_height = 600

    page.add(ft.Text("Информационная система учета общежития", size=24, weight=ft.FontWeight.BOLD))


if __name__ == "__main__":
    init_db()
    ft.app(target=main)