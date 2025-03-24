from scholarly import scholarly
import requests
from bs4 import BeautifulSoup

def get_paper_details(paper):
   
    title = paper.get('bib', {}).get('title', 'No title available')
    authors = paper.get('bib', {}).get('author', 'No authors available')
    url = paper.get('pub_url', 'No URL available')
    citations = paper.get('num_citations', 0)
    
    abstract = paper.get("bib", {}).get("abstract", "No abstract available"),
    if url != 'No URL available':
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            abstract_tag = soup.find('div', class_='abstract')
            if abstract_tag:
                abstract = abstract_tag.get_text(strip=True)
        except Exception as e:
            print(f"Error fetching abstract: {e}")
    
    return {
        'title': title,
        'authors': authors,
        'url': url,
        'citations': citations,
        'abstract': abstract
    }

def search_google_scholar(query, max_results=5):
    """
    Searches Google Scholar for papers related to the query and returns their details.
    """
    search_query = scholarly.search_pubs(query)
    results = []
    
    for i, paper in enumerate(search_query):
        if i >= max_results:
            break
        paper_details = get_paper_details(paper)
        results.append(paper_details)
    
    return results

if __name__ == "__main__":
    question = input("Enter your research question: ")
    
    papers = search_google_scholar(question)
    
    for i, paper in enumerate(papers):
        print(f"\nPaper {i+1}:")
        print(f"Title: {paper['title']}")
        print(f"Authors: {paper['authors']}")
        print(f"URL: {paper['url']}")
        print(f"Citations: {paper['citations']}")
        print(f"Abstract: {paper['abstract']}")
