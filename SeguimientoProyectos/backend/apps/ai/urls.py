from django.urls import path

from .views import AiAssetCreateView, AiContractView, AiSuggestView, AiSuggestionStatusView


urlpatterns = [
    path("contract/", AiContractView.as_view(), name="ai_contract"),
    path("assets/", AiAssetCreateView.as_view(), name="ai_assets"),
    path("suggest/", AiSuggestView.as_view(), name="ai_suggest"),
    path("suggestions/<uuid:suggestion_id>/", AiSuggestionStatusView.as_view(), name="ai_suggestion_status"),
]
