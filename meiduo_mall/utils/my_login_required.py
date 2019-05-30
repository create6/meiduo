from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

class MyLoginRequiredMiXinView(LoginRequiredMixin,View):
    login_url = "/login/"