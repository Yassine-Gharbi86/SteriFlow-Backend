from django.urls import path
from .views import (
    KitListCreateView,
    KitDetailView,
    KitPublicView,
    ReportCreateView,
    ReportAdminListView,
    ReportAdminDetailView,
)

urlpatterns = [



    path('view/<str:kit_id>/',       KitPublicView.as_view(),        name='kit-public-view'),


    path('reports/',                 ReportCreateView.as_view(),     name='report-create'),

    path('reports/admin/',           ReportAdminListView.as_view(),  name='report-admin-list'),
    path('reports/admin/<int:pk>/',  ReportAdminDetailView.as_view(),name='report-admin-detail'),


    path('',                         KitListCreateView.as_view(),    name='kit-list-create'),
    path('<str:kit_id>/',            KitDetailView.as_view(),        name='kit-detail'),
]