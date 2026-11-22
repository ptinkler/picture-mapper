from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import PictureForm
from .models import Picture


class OwnPicturesMixin(LoginRequiredMixin):
    """Only ever show a user their own pictures, so editing someone else's is a 404."""

    model = Picture
    success_url = reverse_lazy("profile")

    def get_queryset(self):
        return Picture.objects.filter(owner=self.request.user)


class ProfileView(OwnPicturesMixin, ListView):
    template_name = "pictures/profile.html"
    context_object_name = "pictures"


class UploadPictureView(LoginRequiredMixin, CreateView):
    model = Picture
    form_class = PictureForm
    template_name = "pictures/picture_form.html"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f"{form.instance.title} uploaded.")
        return super().form_valid(form)


class EditPictureView(OwnPicturesMixin, UpdateView):
    form_class = PictureForm
    template_name = "pictures/picture_form.html"

    def form_valid(self, form):
        messages.success(self.request, f"{form.instance.title} updated.")
        return super().form_valid(form)


class DeletePictureView(OwnPicturesMixin, DeleteView):
    template_name = "pictures/picture_confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, f"{self.object.title} deleted.")
        return super().form_valid(form)


class MapView(LoginRequiredMixin, TemplateView):
    """The global map page."""

    template_name = "pictures/map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = get_user_model().objects.filter(pictures__isnull=False)
        context["users"] = users.distinct().order_by("username")
        return context


class PictureDataView(LoginRequiredMixin, View):
    """Every picture as JSON for the map; ``?user=<id>`` limits it to one user's pictures."""

    def get(self, request):
        pictures = Picture.objects.select_related("owner")
        user = request.GET.get("user", "")
        if user:
            if not user.isdecimal():
                return JsonResponse({"error": "user must be a number"}, status=400)
            pictures = pictures.filter(owner_id=int(user))
        return JsonResponse(
            {
                "pictures": [
                    {
                        "id": p.id,
                        "title": p.title,
                        "description": p.description,
                        "image": p.image.url,
                        "owner": p.owner.get_username(),
                        "created": p.created.isoformat(),
                        "latitude": float(p.latitude),
                        "longitude": float(p.longitude),
                    }
                    for p in pictures
                ]
            }
        )
