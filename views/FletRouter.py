import flet as ft
from views.home import Home
from views.name_flashcard import NameFlashcard
from views.flashcard_content import FlashcardContent

class Router:

    def __init__(self, page, ft):
        self.page = page
        self.fr = ft
        self.routes = {
            "/": Home(page).view(),
            "/name_flashcard": NameFlashcard(page).view(),
            "/flashcard_content": FlashcardContent(page).view()
        }
        self.body = ft.Container(content=self.routes['/'])

    def route_change(self, route):
        self.body.content = self.routes[route.route]
        self.body.update()
        return False
