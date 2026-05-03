from django.urls import path
from .views import GenerateSummaryView, SummaryListView, ValidateSummaryView

urlpatterns = [
    path("generate-summary/",            GenerateSummaryView.as_view(), name="generate-summary"),
    path("summaries/",                   SummaryListView.as_view(),     name="summary-list"),
    path("summaries/<int:pk>/validate/", ValidateSummaryView.as_view(), name="validate-summary"),
]
