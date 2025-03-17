from django.core.management.base import BaseCommand, CommandError
from slra.models import SearchQuery, DigitalLibrarySearch, SearchResult

class Command(BaseCommand):
    help = "Performs a digital library search using an existing SearchQuery ID."

    def add_arguments(self, parser):
        parser.add_argument('--query-id', type=int, required=True, help='SearchQuery ID')
        parser.add_argument('--library', type=str, required=True, help='Library name (ACM, Elsevier, etc.)')

    def handle(self, *args, **options):
        query_id = options['query_id']
        library = options['library']

        try:
            sq = SearchQuery.objects.get(pk=query_id)
        except SearchQuery.DoesNotExist:
            raise CommandError(f"No SearchQuery with ID {query_id}.")

        # For demonstration, we pretend we found 5 results:
        found_count = 5

        # Create a DigitalLibrarySearch record
        dl_search = DigitalLibrarySearch.objects.create(
            search_query=sq,
            library_name=library,
            total_results_found=found_count
        )

        # Possibly create dummy SearchResult objects
        for i in range(1, found_count + 1):
            SearchResult.objects.create(
                library_search=dl_search,
                url=f"https://example.com/paper-{i}",
                title=f"Fake Paper {i} for {library}",
                authors="Doe, J",
                abstract="This is a dummy abstract."
            )

        self.stdout.write(self.style.SUCCESS(
            f"Library search complete. Created DigitalLibrarySearch (ID {dl_search.id}) with {found_count} results."
        ))
