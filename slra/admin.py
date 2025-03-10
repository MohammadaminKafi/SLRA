from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin  # Example if using django-import-export

from .models import (
    SystematicReview, ResearchQuestion, HypothesisKeyword,
    PrimaryStudy, SearchQuery, DigitalLibrarySearch,
    SearchResult, RelevancyEvaluation, LLMProvider,
    LLMModel, LLMQueryLog
)

# -------------------------------------------------------------------------
# 1. Inline Classes
# -------------------------------------------------------------------------

class ResearchQuestionInline(admin.TabularInline):
    """
    Allows inline editing of ResearchQuestion objects
    directly on a SystematicReview's admin page.
    """
    model = ResearchQuestion
    extra = 1  # Number of empty inline forms to display


class HypothesisKeywordInline(admin.TabularInline):
    """
    Allows inline addition/editing of HypothesisKeyword objects
    on a SystematicReview's admin page.
    """
    model = HypothesisKeyword
    extra = 1


class SearchResultInline(admin.TabularInline):
    """
    Manages SearchResult objects within a DigitalLibrarySearch entry.
    """
    model = SearchResult
    extra = 1
    # Example read-only field to preserve data integrity:
    readonly_fields = ('url', 'title', 'authors', 'abstract')


# -------------------------------------------------------------------------
# 2. Custom Admin Filters
# -------------------------------------------------------------------------

class RelevancyFilter(admin.SimpleListFilter):
    """
    Filter for PrimaryStudy objects by relevancy_level (H, M, L, N).
    """
    title = 'Relevancy'
    parameter_name = 'relevancy_level'

    def lookups(self, request, model_admin):
        return [
            ('H', 'High'),
            ('M', 'Medium'),
            ('L', 'Low'),
            ('N', 'Not Evaluated'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(relevancy_level=self.value())
        return queryset


class YearFilter(admin.SimpleListFilter):
    """
    Filter for PrimaryStudy objects by publication_year.
    """
    title = 'Publication Year'
    parameter_name = 'publication_year'

    def lookups(self, request, model_admin):
        # Example: Show only a few distinct years from the dataset
        years = queryset_years = model_admin.model.objects.values_list('publication_year', flat=True).distinct()
        return [(year, str(year)) for year in years if year]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(publication_year=self.value())
        return queryset


class LLMPhaseFilter(admin.SimpleListFilter):
    """
    Filter LLMQueryLog by phase of the systematic review.
    """
    title = 'LLM Phase'
    parameter_name = 'phase'

    def lookups(self, request, model_admin):
        # Use the PHASE_CHOICES from LLMQueryLog
        return model_admin.model.PHASE_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(phase=self.value())
        return queryset


# -------------------------------------------------------------------------
# 3. Admin Classes for Each Model
# -------------------------------------------------------------------------

@admin.register(SystematicReview)
class SystematicReviewAdmin(admin.ModelAdmin):
    """
    Admin panel for SystematicReview with inline editing
    of ResearchQuestion and HypothesisKeyword.
    """
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'problem_statement')
    inlines = [ResearchQuestionInline, HypothesisKeywordInline]

    # Custom action examples:
    actions = ['perform_snowballing']

    def perform_snowballing(self, request, queryset):
        """
        Example action to "perform snowballing" on selected reviews.
        In real usage, you'd implement logic to fetch references,
        parse citations, etc.
        """
        count = queryset.count()
        # Pseudocode: for each review -> fetch related papers -> link them
        self.message_user(request, f"Snowballing triggered for {count} review(s).")


@admin.register(PrimaryStudy)
class PrimaryStudyAdmin(admin.ModelAdmin):
    """
    Admin panel for PrimaryStudy with custom filters and search capabilities.
    """
    list_display = ('title', 'publication_year', 'relevancy_level', 'citations')
    list_filter = (RelevancyFilter, YearFilter)
    search_fields = ('title', 'abstract', 'keywords')
    readonly_fields = ('citations',)  # Example read-only field

    # Bulk actions for efficiency
    actions = ['bulk_approve_relevancy', 'bulk_reject_relevancy']

    def bulk_approve_relevancy(self, request, queryset):
        """
        Sets relevancy_level to 'H' (High) for all selected studies.
        """
        updated = queryset.update(relevancy_level='H')
        self.message_user(request, f"Approved relevancy for {updated} study/studies.")

    def bulk_reject_relevancy(self, request, queryset):
        """
        Sets relevancy_level to 'L' (Low) for all selected studies.
        """
        updated = queryset.update(relevancy_level='L')
        self.message_user(request, f"Rejected relevancy for {updated} study/studies.")


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    """
    Admin for managing search queries. 
    Includes potential re-run of digital library search.
    """
    list_display = ('query_string', 'systematic_review', 'created_at')
    search_fields = ('query_string',)
    # Potential custom actions:
    actions = ['re_run_library_search']

    def re_run_library_search(self, request, queryset):
        """
        Example action to re-run library searches for each query.
        """
        for sq in queryset:
            # Pseudocode:
            #  - sq.fetch_external_results()
            pass
        self.message_user(request, f"Re-ran library search for {queryset.count()} queries.")


@admin.register(DigitalLibrarySearch)
class DigitalLibrarySearchAdmin(admin.ModelAdmin):
    """
    Admin for DigitalLibrarySearch entries.
    Inline management of SearchResult objects.
    """
    list_display = ('search_query', 'library_name', 'search_date', 'total_results_found')
    inlines = [SearchResultInline]


@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    """
    Manually manage search results if needed.
    Read-only fields help maintain data integrity.
    """
    list_display = ('title', 'url', 'library_search')
    readonly_fields = ('title', 'url', 'authors', 'abstract', 'library_search')


@admin.register(RelevancyEvaluation)
class RelevancyEvaluationAdmin(admin.ModelAdmin):
    """
    Keep track of all relevancy evaluations with possible auditing features.
    """
    list_display = ('primary_study', 'relevancy', 'evaluator', 'evaluated_at')
    list_filter = ('relevancy', 'evaluator')
    readonly_fields = ('evaluated_at',)
    search_fields = ('notes', 'primary_study__title', 'evaluator')
    # If using django-simple-history, you'd see historical changes in the admin.


@admin.register(LLMProvider)
class LLMProviderAdmin(admin.ModelAdmin):
    """
    Manage LLM providers. Restrict changes to superusers only if needed.
    """
    list_display = ('name', 'base_url')
    search_fields = ('name', 'description')

    def has_change_permission(self, request, obj=None):
        """
        Example to restrict editing to superusers only.
        """
        if not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    """
    Manage LLM models, credentials, usage instructions, etc.
    Restrict editing if needed to superusers.
    """
    list_display = ('model_name', 'version', 'provider', 'usage_method')
    search_fields = ('model_name', 'version', 'usage_method')
    # Potentially read-only for credentials to normal staff
    # or override has_change_permission similarly to LLMProvider.

    def has_change_permission(self, request, obj=None):
        """
        Restrict editing credentials to superusers only (sample logic).
        """
        if not request.user.is_superuser:
            # Possibly allow partial editing but not credentials
            # or disallow entirely:
            return False
        return super().has_change_permission(request, obj)


@admin.register(LLMQueryLog)
class LLMQueryLogAdmin(ImportExportModelAdmin):
    """
    Manage logs of LLM interactions.
    - Example usage of django-import-export for easy CSV/Excel manipulation
    - Read-only for response_text to prevent tampering
    - Custom filter by phase (Problem Formulation, etc.)
    """
    list_display = ('prompt_text_short', 'phase', 'systematic_review', 'created_at')
    list_filter = (LLMPhaseFilter, 'systematic_review')
    search_fields = ('prompt_text', 'response_text')
    readonly_fields = ('response_text', 'created_at')

    def prompt_text_short(self, obj):
        """
        Utility method to show a truncated prompt in the list display.
        """
        if len(obj.prompt_text) > 50:
            return f"{obj.prompt_text[:50]}..."
        return obj.prompt_text

    prompt_text_short.short_description = "Prompt"

    # Example custom actions:
    actions = ['bulk_delete_outdated']

    def bulk_delete_outdated(self, request, queryset):
        """
        Bulk deletion of outdated LLM queries.
        """
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Deleted {count} LLM query log(s).")

