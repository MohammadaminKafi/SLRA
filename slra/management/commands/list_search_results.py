from django.core.management.base import BaseCommand, CommandError
from slra.models import SearchQuery, DigitalLibrarySearch, SearchResult

class Command(BaseCommand):
    help = "Lists search results for a given SearchQuery ID."

    def add_arguments(self, parser):
        parser.add_argument('--query-id', type=int, required=True, help='SearchQuery ID')

    def handle(self, *args, **options):
        query_id = options['query_id']
        try:
            sq = SearchQuery.objects.get(pk=query_id)
        except SearchQuery.DoesNotExist:
            raise CommandError(f"No SearchQuery with ID {query_id}.")

        library_searches = DigitalLibrarySearch.objects.filter(search_query=sq)
        if not library_searches.exists():
            self.stdout.write(self.style.WARNING(f"No library searches found for SearchQuery ID {query_id}."))
            return

        for ls in library_searches:
            self.stdout.write(self.style.SUCCESS(
                f"DigitalLibrarySearch (ID {ls.id}) - {ls.library_name}, found {ls.total_results_found}"
            ))
            results = SearchResult.objects.filter(library_search=ls)
            for r in results:
                self.stdout.write(f"   - {r.title[:50]} (URL: {r.url})")
