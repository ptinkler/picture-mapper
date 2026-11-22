from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("profile")

    def dispatch(self, request, *args, **kwargs):
        if not settings.REGISTRATION_OPEN:
            return RegistrationClosedView.as_view()(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class RegistrationClosedView(TemplateView):
    template_name = "registration/registration_closed.html"
