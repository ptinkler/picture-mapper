from django.urls import path

from . import views

urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("upload/", views.UploadPictureView.as_view(), name="upload_picture"),
    path("edit/<int:pk>/", views.EditPictureView.as_view(), name="edit_picture"),
    path("delete/<int:pk>/", views.DeletePictureView.as_view(), name="delete_picture"),
    path("map/", views.MapView.as_view(), name="map"),
    path("map/picture-data/", views.PictureDataView.as_view(), name="picture_data"),
]
