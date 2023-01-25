from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", view=views.index, name="index"),
    path("signin/", view=views.signin, name="signin"),
    path("signup/", view=views.signup, name="signup"),
    path("logout/", view=views.logout, name="logout"),
    path("settings/", view=views.settings, name="settings"),
    path("upload", view= views.upload, name= "upload"),
    # profile/userprofile where str is the datatype and pk is the key
    path("profile/<str:pk>", view= views.profile, name= "profile"),
    path("like-post", view= views.like_post, name= "like-post"),
    path("follow", view= views.follow, name= "follow"),
    path("search", view= views.search, name= "search"),


]


urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
