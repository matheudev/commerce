from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("closed_listings/", views.closed_listings, name="closed_listings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing/", views.create_listing, name='create_listing'),
    path("listings/<int:listing_id>/", views.listing_detail, name='listing_detail'),
    path("add_watchlist/<int:listing_id>/", views.add_watchlist, name='add_watchlist'),
    path("remove_watchlist/<int:listing_id>/", views.remove_watchlist, name="remove_watchlist"),
    path("add_comment/<int:listing_id>/", views.add_comment, name="add_comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path('listings/<int:listing_id>/close', views.close_listing, name='close_listing'),
    path('listings/<int:listing_id>/bid', views.place_bid, name='place_bid'),
    path('categories/', views.categories, name='categories'),
]
