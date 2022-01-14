from starlette.routing import Route, Mount

from tfl.site.views.airports import AirportsView
from tfl.site.views.member import RegisterPage, LoginPage, ProfilePage

member_page_routes = [
    Route('/register', RegisterPage, name='register'),
    Route('/login', LoginPage, name='login'),
    Route('/profile', ProfilePage, name='profile')
]


static_page_routes = [
    Mount('/members', routes=member_page_routes, name='member'),
    Route('/airports/{icao}', AirportsView)
]