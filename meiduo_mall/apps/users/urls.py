from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^register/$',views.RegisterView.as_view(),name="register"),
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.CheckUsernameView.as_view(),name="username"),
    url(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/$',views.CheckMobileView.as_view(),name="mobile"),
    url(r'^login/$',views.LoginUserView.as_view()),
    url(r'^logout/$',views.LogoutUserView.as_view()),
    # url(r'^info/$',views.UserCenterView.as_view()),
    # url(r'^info/$',login_required(views.UserCenterView.as_view())),
    url(r'^info/$',views.UserCenterView.as_view()),
    url(r'^emails/$',views.EmailSendView.as_view()),
    url(r'^emails/verification/$',views.EmailActiveView.as_view()),
    url(r'^addresses/$',views.AddressView.as_view()),
    url(r'^addresses/create/$',views.AddressCreateView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/$',views.AddressUpdateView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/default/$',views.AddressDefaultView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/title/$',views.AddressTitleView.as_view()),
    url(r'^password/$',views.PasswordChangeView.as_view()),
]