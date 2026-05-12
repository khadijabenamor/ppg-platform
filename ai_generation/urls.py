from django.urls import path
from .views import (
    GenerateSummaryView,
    GenerateFromPDFView,
    SummaryListView,
    ValidateSummaryView,
    RequestVerificationView,
    RespondVerificationView,
    VerificationListView,
    MyResumeListView,
)

urlpatterns = [
    path("generate-summary/",                        GenerateSummaryView.as_view(),    name="generate-summary"),
    path("generate-from-pdf/",                       GenerateFromPDFView.as_view(),    name="generate-from-pdf"),
    path("summaries/",                               SummaryListView.as_view(),        name="summary-list"),
    path("my-summaries/",                            MyResumeListView.as_view(),       name="my-summaries"),
    path("summaries/<int:pk>/validate/",             ValidateSummaryView.as_view(),    name="validate-summary"),
    path("summaries/<int:pk>/request-verification/", RequestVerificationView.as_view(),name="request-verification"),
    path("verification/<int:pk>/respond/",           RespondVerificationView.as_view(),name="respond-verification"),
    path("verifications/",                           VerificationListView.as_view(),   name="verification-list"),
]
