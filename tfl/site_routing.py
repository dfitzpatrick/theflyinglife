from starlette.routing import Route, Mount

from tfl.site.views.airports import AirportsView
from tfl.site.views.main import MainView
from tfl.site.views.member import RegisterPage, LoginPage, ProfilePage

member_page_routes = [
    Route('/register', RegisterPage, name='register'),
    Route('/login', LoginPage, name='login'),
    Route('/profile', ProfilePage, name='profile')
]


static_page_routes = [
    #Route('/', MainView, name='main'),
    #Route('/members/register', RegisterPage, name='register'),
    #Route('/members/profile', ProfilePage, name='profile'),
    Route('/airports/{icao}', AirportsView)
]