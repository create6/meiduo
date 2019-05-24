from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$',views.RegisterView.as_view(),name="register"),
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.CheckUsernameView.as_view(),name="username"),
    url(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/$',views.CheckMobileView.as_view(),name="mobile"),
    url(r'^login/$',views.LoginUserView.as_view()),
]