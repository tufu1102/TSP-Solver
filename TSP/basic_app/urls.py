from django.urls import path
from basic_app import views

app_name = 'basic_app'

urlpatterns = [
    path('DP/', views.dp_approach_view, name = "DP"),
    path('NN/', views.nn_approach_view, name = "NN")
]