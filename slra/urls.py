from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SystematicReviewViewSet, ResearchQuestionViewSet, HypothesisKeywordViewSet,
    PrimaryStudyViewSet, SearchQueryViewSet, DigitalLibrarySearchViewSet,
    SearchResultViewSet, RelevancyEvaluationViewSet, LLMProviderViewSet,
    LLMModelViewSet, LLMQueryLogViewSet
)

router = DefaultRouter()

router.register(r'reviews', SystematicReviewViewSet, basename='systematicreview')
router.register(r'research-questions', ResearchQuestionViewSet, basename='researchquestion')
router.register(r'keywords', HypothesisKeywordViewSet, basename='hypothesiskeyword')
router.register(r'primary-studies', PrimaryStudyViewSet, basename='primarystudy')
router.register(r'search-queries', SearchQueryViewSet, basename='searchquery')
router.register(r'library-searches', DigitalLibrarySearchViewSet, basename='digitallibrarysearch')
router.register(r'search-results', SearchResultViewSet, basename='searchresult')
router.register(r'relevancy-evaluations', RelevancyEvaluationViewSet, basename='relevancyevaluation')
router.register(r'llm-providers', LLMProviderViewSet, basename='llmprovider')
router.register(r'llm-models', LLMModelViewSet, basename='llmmodel')
router.register(r'llm-query-logs', LLMQueryLogViewSet, basename='llmquerylog')

urlpatterns = [
    path('api/', include(router.urls)),
]