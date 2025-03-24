from django.db import models

# ------------------------------------------------------------------------
# 1. Core Models for Systematic Review
# ------------------------------------------------------------------------

class SystematicReview(models.Model):
    """
    Represents a single Systematic Review project that encompasses
    steps from problem formulation to analysis.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="A unique name/title for this systematic review."
    )
    problem_statement = models.TextField(
        blank=True,
        null=True,
        help_text="High-level description of the problem domain."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last updated."
    )

    def __str__(self):
        return self.name


class ResearchQuestion(models.Model):
    """
    Stores each research question (Step 1: Problem Formulation).
    """
    systematic_review = models.ForeignKey(
        SystematicReview,
        on_delete=models.CASCADE,
        related_name='research_questions',
        help_text="Link to the parent systematic review."
    )
    question_text = models.TextField(
        help_text="Full text of the research question."
    )

    def __str__(self):
        return f"RQ for {self.systematic_review.name}: {self.question_text[:50]}..."


class HypothesisKeyword(models.Model):
    """
    Stores the keywords/hypotheses selected in Step 2 (Initial Hypotheses).
    """
    systematic_review = models.ForeignKey(
        SystematicReview,
        on_delete=models.CASCADE,
        related_name='hypothesis_keywords',
        help_text="Link to the parent systematic review."
    )
    keyword = models.CharField(
        max_length=255,
        help_text="The keyword or phrase relevant to initial hypotheses."
    )

    def __str__(self):
        return self.keyword


# ------------------------------------------------------------------------
# 2. Venue & Venue Quality
# ------------------------------------------------------------------------

class VenueQualitySource(models.Model):
    """
    Describes a source or service that provides venue-quality metrics,
    such as SJR, Scopus, JCR, etc.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the quality source (e.g., SJR, Scopus, etc.)."
    )
    base_url = models.URLField(
        blank=True,
        null=True,
        help_text="Endpoint or homepage for the quality source."
    )
    usage_instructions = models.TextField(
        blank=True,
        null=True,
        help_text="How to query or retrieve data from this source."
    )

    def __str__(self):
        return self.name


class Venue(models.Model):
    """
    Represents a publication venue (journal, conference, workshop, etc.).
    We can link multiple PrimaryStudies to a single Venue. Additional
    metadata/metrics (SJR score, Impact Factor, etc.) can be associated here.
    """
    VENUE_TYPE_CHOICES = (
        ('journal', 'Journal'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('unknown', 'Unknown'),
    )
    name = models.CharField(
        max_length=255,
        help_text="Name of the journal or conference."
    )
    venue_type = models.CharField(
        max_length=50,
        choices=VENUE_TYPE_CHOICES,
        default='unknown',
        help_text="Type of venue (journal, conference, etc.)."
    )
    # If you want to store a single, universal metric:
    # e.g., 'sjr_rank', 'impact_factor'
    # You can add them here or store them in a separate model referencing 'VenueQualitySource'

    # For a more flexible approach (e.g., multiple metrics from multiple sources),
    # you might create a 'VenueQualityRecord' with references to 'Venue' & 'VenueQualitySource'.

    def __str__(self):
        return f"{self.name} ({self.get_venue_type_display()})"


# ------------------------------------------------------------------------
# 3. Primary Study
# ------------------------------------------------------------------------

class PrimaryStudy(models.Model):
    """
    Represents a primary study identified in Step 3 (Initial Data Collection).
    """
    systematic_review = models.ForeignKey(
        SystematicReview,
        on_delete=models.CASCADE,
        related_name='primary_studies',
        help_text="Link to the parent systematic review."
    )
    source = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Data source (e.g., 'Google Scholar', 'PubMed')."
    )
    url = models.URLField(
        max_length=2000,
        blank=True,
        null=True,
        help_text="Direct link to the paper if available."
    )
    title = models.TextField(
        help_text="Full title of the study."
    )
    abstract = models.TextField(
        blank=True,
        null=True,
        help_text="Study abstract."
    )
    keywords = models.TextField(
        blank=True,
        null=True,
        help_text="Comma-separated or free-form keywords from the study."
    )

    # Instead of storing 'venue' as a string, we reference the new Venue model.
    venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Venue (journal, conference, etc.) associated with this study."
    )

    publication_type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Type of publication (journal, conference, book chapter)."
    )
    publication_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Year of publication."
    )
    citations = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of citations reported."
    )
    RELEVANCY_CHOICES = (
        ('H', 'High'),
        ('M', 'Medium'),
        ('L', 'Low'),
        ('N', 'Not Evaluated'),
    )
    relevancy_level = models.CharField(
        max_length=1,
        choices=RELEVANCY_CHOICES,
        default='N',
        help_text="Overall relevancy level after initial screening."
    )

    def __str__(self):
        return self.title[:80]


# ------------------------------------------------------------------------
# 4. Search Queries & Libraries
# ------------------------------------------------------------------------

class SearchQuery(models.Model):
    """
    Stores the search queries defined in Step 4 (Query String Definition).
    """
    systematic_review = models.ForeignKey(
        SystematicReview,
        on_delete=models.CASCADE,
        related_name='search_queries',
        help_text="Link to the parent systematic review."
    )
    query_string = models.TextField(
        help_text="The exact query string used for searching digital libraries."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this query was recorded."
    )

    def __str__(self):
        return f"Query for {self.systematic_review.name}: {self.query_string[:50]}..."


class DigitalLibrary(models.Model):
    """
    Describes a digital library or database (e.g., Google Scholar, Arxiv, IEEE, etc.)
    with details about how to query it, any required credentials, etc.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the digital library (e.g., 'Google Scholar', 'Arxiv')."
    )
    base_url = models.URLField(
        blank=True,
        null=True,
        help_text="Optional base URL or endpoint for API calls."
    )
    usage_method = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Method of usage: 'web-scraping', 'official API', etc."
    )
    credentials = models.TextField(
        blank=True,
        null=True,
        help_text="Any credentials or tokens needed for this library."
    )
    usage_instructions = models.TextField(
        blank=True,
        null=True,
        help_text="Documentation or instructions on how to query this library."
    )

    def __str__(self):
        return self.name


class DigitalLibrarySearch(models.Model):
    """
    Records each search performed in Step 5 (Digital Library Exploration),
    now referencing a 'DigitalLibrary' object instead of just a name.
    """
    search_query = models.ForeignKey(
        SearchQuery,
        on_delete=models.CASCADE,
        related_name='library_searches',
        help_text="The query that was used for this library search."
    )
    library = models.ForeignKey(
        DigitalLibrary,
        on_delete=models.CASCADE,
        related_name='performed_searches',
        help_text="The digital library used for this search."
    )
    search_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this search was performed."
    )
    total_results_found = models.PositiveIntegerField(
        default=0,
        help_text="Number of results returned by the library for this query."
    )

    def __str__(self):
        return (f"Search on '{self.library.name}' "
                f"({self.search_date.strftime('%Y-%m-%d %H:%M:%S')}) "
                f"- Query ID: {self.search_query.id}")


class SearchResult(models.Model):
    """
    If you want to capture each result returned by a digital library,
    store it here. Later, you can decide whether to include it as a PrimaryStudy.
    """
    library_search = models.ForeignKey(
        DigitalLibrarySearch,
        on_delete=models.CASCADE,
        related_name='search_results',
        help_text="The digital library search that returned this result."
    )
    url = models.URLField(
        max_length=2000,
        help_text="Link to the publication or resource."
    )
    title = models.TextField(
        blank=True,
        null=True,
        help_text="Title of the publication."
    )
    authors = models.TextField(
        blank=True,
        null=True,
        help_text="Authors listed for the publication."
    )
    abstract = models.TextField(
        blank=True,
        null=True,
        help_text="Abstract or summary of the publication."
    )

    def __str__(self):
        return f"Result from {self.library_search.library.name}: {self.title[:50]}"


# ------------------------------------------------------------------------
# 5. Relevancy Evaluations
# ------------------------------------------------------------------------

class RelevancyEvaluation(models.Model):
    """
    Manages the Step 6 (Relevancy Evaluation) process explicitly.
    Useful if multiple people or multiple rounds are involved in reviewing a study.
    """
    primary_study = models.ForeignKey(
        PrimaryStudy,
        on_delete=models.CASCADE,
        related_name='relevancy_evaluations',
        help_text="Reference to the study being evaluated."
    )
    evaluator = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Name or ID of the person/system performing the evaluation."
    )
    RELEVANCY_CHOICES = (
        ('H', 'High'),
        ('M', 'Medium'),
        ('L', 'Low'),
        ('X', 'Exclude')
    )
    relevancy = models.CharField(
        max_length=1,
        choices=RELEVANCY_CHOICES,
        default='H',
        help_text="Final relevancy decision made by the evaluator."
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Any notes or rationale for the relevancy decision."
    )
    evaluated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this evaluation was recorded."
    )

    def __str__(self):
        return f"{self.primary_study.title[:50]} - {self.get_relevancy_display()}"


# ------------------------------------------------------------------------
# 6. LLM-Related Models
# ------------------------------------------------------------------------

class LLMProvider(models.Model):
    """
    Stores metadata about the provider or platform hosting LLMs,
    e.g. 'Ollama' (local), 'together.ai', 'OpenAI'.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Provider name, e.g., 'Ollama', 'together.ai', 'OpenAI'."
    )
    base_url = models.URLField(
        blank=True,
        null=True,
        help_text="Optional base URL or endpoint for API calls."
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Short description of this provider or service."
    )

    def __str__(self):
        return self.name


class LLMModel(models.Model):
    """
    Stores information about specific LLM versions/models,
    e.g. 'llama3.1' using Ollama, or 'chatGPT-3.5' using OpenAI.
    Credentials might be stored here if each model needs its own key.
    """
    provider = models.ForeignKey(
        LLMProvider,
        on_delete=models.CASCADE,
        related_name='models',
        help_text="The provider platform for this LLM."
    )
    model_name = models.CharField(
        max_length=255,
        help_text="The name or identifier for the LLM, e.g., 'llama3.1'."
    )
    version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Version tag if applicable (e.g., 'v3.1', 'GPT-3.5')."
    )
    usage_method = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Method of usage, e.g., 'local Docker', 'API call', etc."
    )
    credentials = models.TextField(
        blank=True,
        null=True,
        help_text="Any credentials needed. Use a secure storage approach in production!"
    )
    usage_instructions = models.TextField(
        blank=True,
        null=True,
        help_text="Documentation or instructions on how to call this model."
    )

    class Meta:
        unique_together = ('provider', 'model_name', 'version')

    def __str__(self):
        version_str = f" (v{self.version})" if self.version else ""
        return f"{self.provider.name} - {self.model_name}{version_str}"


class LLMQueryLog(models.Model):
    """
    Stores queries sent to an LLM and the corresponding responses.
    Allows you to track usage in each phase of the systematic review.
    """
    PHASE_CHOICES = (
        (1, 'Problem Formulation'),
        (2, 'Initial Hypotheses'),
        (3, 'Initial Data Collection'),
        (4, 'Query String Definition'),
        (5, 'Digital Library Exploration'),
        (6, 'Relevancy Evaluation'),
        # Extend if needed
    )

    systematic_review = models.ForeignKey(
        SystematicReview,
        on_delete=models.CASCADE,
        related_name='llm_query_logs',
        help_text="Systematic review context for this query."
    )
    llm_model = models.ForeignKey(
        LLMModel,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Which LLM model was used for this query?"
    )
    phase = models.PositiveSmallIntegerField(
        choices=PHASE_CHOICES,
        help_text="Which step or phase of the review does this query pertain to?"
    )
    prompt_text = models.TextField(
        help_text="Full text of the prompt or question sent to the LLM."
    )
    response_text = models.TextField(
        blank=True,
        null=True,
        help_text="LLM's response to the prompt."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this query was made."
    )

    def __str__(self):
        return f"LLM Query (Step {self.phase}) for {self.systematic_review.name}"
