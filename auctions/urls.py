from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting/", views.createlisting, name='createlisting'),
    path("placebid/", views.placebid, name='placebid'),
    path("listing/<int:id>/", views.showlisting, name="showlisting"),
    path("category/<str:category>/", views.categorywise, name="categorywise"),
    path("categories/", views.categories, name="categories"),
    path("addtowatchlist/", views.addtowatchlist, name="addtowatchlist"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("comment/", views.comment, name="comment"),
    path("listing/<str:name>/", views.userlistings, name="userlistings"),
    path("deactivate/<str:title>", views.deactivate, name="deactivate"),
]
