from rest_framework import serializers
from .models import (
    SystematicReview, ResearchQuestion, HypothesisKeyword,
    PrimaryStudy, SearchQuery, DigitalLibrarySearch,
    SearchResult, RelevancyEvaluation, LLMProvider,
    LLMModel, LLMQueryLog
)


class SystematicReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystematicReview
        fields = '__all__'


class ResearchQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchQuestion
        fields = '__all__'


class HypothesisKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HypothesisKeyword
        fields = '__all__'


class PrimaryStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrimaryStudy
        fields = '__all__'


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = '__all__'


class DigitalLibrarySearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalLibrarySearch
        fields = '__all__'


class SearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchResult
        fields = '__all__'


class RelevancyEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelevancyEvaluation
        fields = '__all__'


class LLMProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMProvider
        fields = '__all__'


class LLMModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMModel
        fields = '__all__'


class LLMQueryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMQueryLog
        fields = '__all__'
