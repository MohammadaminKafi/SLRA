from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from django.shortcuts import get_object_or_404

from .models import (
    SystematicReview, ResearchQuestion, HypothesisKeyword,
    PrimaryStudy, SearchQuery, DigitalLibrarySearch,
    SearchResult, RelevancyEvaluation, LLMProvider,
    LLMModel, LLMQueryLog
)
from .serializers import (
    SystematicReviewSerializer, ResearchQuestionSerializer, HypothesisKeywordSerializer,
    PrimaryStudySerializer, SearchQuerySerializer, DigitalLibrarySearchSerializer,
    SearchResultSerializer, RelevancyEvaluationSerializer, LLMProviderSerializer,
    LLMModelSerializer, LLMQueryLogSerializer
)


# --------------------------------------------------------------------
# SystematicReview (covers 5 of the 30 endpoints)
# --------------------------------------------------------------------
class SystematicReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD for Systematic Reviews.
    Endpoints:
      - list (GET)      -> /api/reviews/
      - retrieve (GET)  -> /api/reviews/{id}/
      - create (POST)   -> /api/reviews/
      - update (PUT)    -> /api/reviews/{id}/
      - destroy (DELETE)-> /api/reviews/{id}/
    """
    queryset = SystematicReview.objects.all()
    serializer_class = SystematicReviewSerializer


# --------------------------------------------------------------------
# ResearchQuestion endpoints
# --------------------------------------------------------------------
class ResearchQuestionViewSet(viewsets.ModelViewSet):
    """
    Manage research questions within a systematic review.
    Endpoints:
      - list (GET)        -> /api/research-questions/
      - retrieve (GET)    -> /api/research-questions/{id}/
      - create (POST)     -> /api/research-questions/
      - update (PUT)      -> /api/research-questions/{id}/
      - destroy (DELETE)  -> /api/research-questions/{id}/
    """
    queryset = ResearchQuestion.objects.all()
    serializer_class = ResearchQuestionSerializer

    def create(self, request, *args, **kwargs):
        """
        Example: Ensure the SystematicReview exists before creating.
        """
        review_id = request.data.get('systematic_review')
        if not SystematicReview.objects.filter(pk=review_id).exists():
            raise ValidationError(f"SystematicReview with id={review_id} does not exist.")

        return super().create(request, *args, **kwargs)


# --------------------------------------------------------------------
# HypothesisKeyword endpoints
# --------------------------------------------------------------------
class HypothesisKeywordViewSet(viewsets.ModelViewSet):
    """
    Manage hypothesis keywords for each review.
    """
    queryset = HypothesisKeyword.objects.all()
    serializer_class = HypothesisKeywordSerializer


# --------------------------------------------------------------------
# PrimaryStudy endpoints
# --------------------------------------------------------------------
class PrimaryStudyViewSet(viewsets.ModelViewSet):
    """
    Manage primary studies collected for a systematic review.
    """
    queryset = PrimaryStudy.objects.all()
    serializer_class = PrimaryStudySerializer

    @action(detail=True, methods=['post'], url_path='evaluate')
    def evaluate_study(self, request, pk=None):
        """
        Custom endpoint to set relevancy (H/M/L/X) for a specific PrimaryStudy.
        e.g., POST /api/primary-studies/{pk}/evaluate/ { "relevancy": "H" }
        """
        study = self.get_object()  # Raises 404 if not found
        relevancy = request.data.get('relevancy')

        valid_choices = [c[0] for c in RelevancyEvaluation.RELEVANCY_CHOICES]
        if relevancy not in valid_choices:
            raise ValidationError(f"Invalid relevancy. Must be one of {valid_choices}.")

        # Create a RelevancyEvaluation record
        evaluation = RelevancyEvaluation.objects.create(
            primary_study=study,
            evaluator=request.data.get('evaluator', 'Unknown'),
            relevancy=relevancy,
            notes=request.data.get('notes', '')
        )
        # Also update the PrimaryStudy's relevancy_level if you wish
        if relevancy == 'X':
            study.relevancy_level = 'N'  # Or keep it as is
        else:
            # If it's not excluded, set the study's main relevancy
            # It's up to your business logic whether you do this or not
            study.relevancy_level = relevancy
        study.save()

        serializer = RelevancyEvaluationSerializer(evaluation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='quality-check')
    def perform_quality_check(self, request):
        """
        (Optional) Illustrative endpoint to filter or assess studies based on certain criteria.
        GET /api/primary-studies/quality-check/
        """
        # Add your own logic: e.g., select only those with citations > 50
        high_quality_studies = PrimaryStudy.objects.filter(citations__gt=50)
        serializer = self.get_serializer(high_quality_studies, many=True)
        return Response(serializer.data)


# --------------------------------------------------------------------
# SearchQuery endpoints
# --------------------------------------------------------------------
class SearchQueryViewSet(viewsets.ModelViewSet):
    """
    Manage search queries used in the systematic review.
    """
    queryset = SearchQuery.objects.all()
    serializer_class = SearchQuerySerializer

    @action(detail=True, methods=['post'], url_path='search-libraries')
    def perform_library_search(self, request, pk=None):
        """
        Custom endpoint to perform an actual search on external libraries
        using the query_string. For demonstration only.
        e.g., POST /api/search-queries/{pk}/search-libraries/
        """
        search_query = self.get_object()
        # Pretend we search external libraries here...
        # This is where you'd integrate with real external APIs (ACM, etc.).

        library_name = request.data.get('library_name', 'Unknown Library')
        # Let's pretend we found 10 results:
        found_count = 10

        # Create a DigitalLibrarySearch record
        library_search = DigitalLibrarySearch.objects.create(
            search_query=search_query,
            library_name=library_name,
            total_results_found=found_count
        )

        # Possibly create some SearchResult entries
        # For demonstration, we just create a couple of dummy ones:
        for i in range(1, 3):
            SearchResult.objects.create(
                library_search=library_search,
                url=f"https://example.com/dummy-{i}",
                title=f"Sample Title {i}",
                authors="Doe, J; Roe, R",
                abstract="A dummy abstract..."
            )

        # Return the newly created DigitalLibrarySearch and results
        dl_serializer = DigitalLibrarySearchSerializer(library_search)
        return Response(dl_serializer.data, status=status.HTTP_201_CREATED)


# --------------------------------------------------------------------
# DigitalLibrarySearch endpoints
# --------------------------------------------------------------------
class DigitalLibrarySearchViewSet(viewsets.ModelViewSet):
    """
    Manage records of actual searches performed.
    """
    queryset = DigitalLibrarySearch.objects.all()
    serializer_class = DigitalLibrarySearchSerializer


# --------------------------------------------------------------------
# SearchResult endpoints
# --------------------------------------------------------------------
class SearchResultViewSet(viewsets.ModelViewSet):
    """
    Manage individual search results from digital libraries.
    """
    queryset = SearchResult.objects.all()
    serializer_class = SearchResultSerializer


# --------------------------------------------------------------------
# RelevancyEvaluation endpoints
# --------------------------------------------------------------------
class RelevancyEvaluationViewSet(viewsets.ModelViewSet):
    """
    Manage explicit relevancy evaluations for each PrimaryStudy.
    """
    queryset = RelevancyEvaluation.objects.all()
    serializer_class = RelevancyEvaluationSerializer


# --------------------------------------------------------------------
# LLM Provider / Model / Query Log endpoints
# --------------------------------------------------------------------
class LLMProviderViewSet(viewsets.ModelViewSet):
    queryset = LLMProvider.objects.all()
    serializer_class = LLMProviderSerializer


class LLMModelViewSet(viewsets.ModelViewSet):
    queryset = LLMModel.objects.all()
    serializer_class = LLMModelSerializer


class LLMQueryLogViewSet(viewsets.ModelViewSet):
    queryset = LLMQueryLog.objects.all()
    serializer_class = LLMQueryLogSerializer

    @action(detail=True, methods=['post'], url_path='send-prompt')
    def send_prompt_to_llm(self, request, pk=None):
        """
        Demonstration of sending a prompt to this LLM and storing the response.
        e.g., POST /api/llm-query-logs/{pk}/send-prompt/
        {
            "prompt_override": "Some text to override the existing prompt..."
        }
        """
        query_log = self.get_object()
        # If the user wants to override the stored prompt:
        prompt_text = request.data.get('prompt_override') or query_log.prompt_text
        # Pretend we call the LLM provider's API or local inference here...

        # Fake LLM response:
        response_text = f"Simulated LLM response to prompt: {prompt_text[:50]}..."

        # Update the query log
        query_log.response_text = response_text
        query_log.save()

        serializer = self.get_serializer(query_log)
        return Response(serializer.data, status=status.HTTP_200_OK)

