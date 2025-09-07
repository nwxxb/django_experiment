from django.urls import path
from . import views

urlpatterns = [
    path("services/create", views.create_service, name="create_service"),
    path("services/", views.show_all_services, name="show_all_services"),
    path("services/<int:service_id>", views.show_service, name="show_service"),
    path("services/<int:service_id>/update", views.update_service, name="update_service"),
    path("services/<int:service_id>/delete", views.delete_service, name="delete_service"),

    path("appointments/create", views.create_appointment, name="create_appointment"),
    path("appointments/", views.show_all_appointments, name="show_all_appointments"),
    path("appointments/<int:appointment_id>/delete", views.delete_appointment, name="delete_appointment"),
]
