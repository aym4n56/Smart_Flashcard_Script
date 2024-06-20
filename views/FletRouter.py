import flet as ft
from views.home import Home
from views.name_flashcard import NameFlashcard
from views.flashcard_content import FlashcardContent
from views.view_flashcard import ViewFlashcard
from views.pick_flashcard import PickFlashcard

class Router:

    def __init__(self, page, ft):
        self.page = page
        self.fr = ft
        self.routes = {
            "/": Home(page).view(),
            "/name_flashcard": NameFlashcard(page).view(),
            "/flashcard_content": FlashcardContent(page).view(),
            "/pick_flashcard": PickFlashcard(page).view()
        }
        self.body = ft.Container(content=self.routes['/'])

    def route_change(self, route):
        if route.route == '/view_flashcard':
            self.routes['/view_flashcard'] = ViewFlashcard(self.page).view()
            self.page.update()
        
        self.body.content = self.routes.get(route.route, self.routes['/'])
        self.body.update()
        return False
