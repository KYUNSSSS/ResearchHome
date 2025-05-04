import requests
from datetime import datetime
from app import app, db, Research
import random
import time

def fetch_random_papers(num_papers=20):
    """
    Fetch random research papers from arXiv API and add them to the database
    """
    # arXiv API endpoint
    base_url = "http://export.arxiv.org/api/query"
    
    # List of categories to choose from
    categories = [
        'cs.AI', 'cs.CL', 'cs.CV', 'cs.LG', 'cs.SE',  # Computer Science
        'math.CO', 'math.PR', 'math.ST',               # Mathematics
        'physics.acc-ph', 'physics.ao-ph',             # Physics
        'q-bio.BM', 'q-bio.GN', 'q-bio.QM'            # Quantitative Biology
    ]
    
    try:
        # Select random categories
        selected_categories = random.sample(categories, 3)
        category_query = ' OR '.join(f'cat:{cat}' for cat in selected_categories)
        
        # Parameters for the API request
        params = {
            'search_query': category_query,
            'max_results': num_papers,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        # Make the API request
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        # Parse the XML response
        from xml.etree import ElementTree as ET
        root = ET.fromstring(response.content)
        
        # Define the namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}
        
        # Process each paper
        for entry in root.findall('.//atom:entry', ns):
            # Extract paper information
            title = entry.find('atom:title', ns).text.strip()
            abstract = entry.find('atom:summary', ns).text.strip()
            
            # Extract authors
            authors = []
            for author in entry.findall('atom:author/atom:name', ns):
                authors.append(author.text.strip())
            
            # Extract publication date
            published = entry.find('atom:published', ns).text
            pub_date = datetime.strptime(published, '%Y-%m-%dT%H:%M:%SZ')
            
            # Extract DOI (arXiv ID)
            doi = entry.find('atom:id', ns).text.split('/')[-1]
            
            # Extract categories as keywords
            categories = []
            for category in entry.findall('arxiv:primary_category', ns):
                categories.append(category.get('term'))
            for category in entry.findall('atom:category', ns):
                categories.append(category.get('term'))
            
            # Create new research paper entry
            new_paper = Research(
                title=title,
                authors=', '.join(authors) if authors else 'Unknown',
                abstract=abstract,
                publication_date=pub_date,
                keywords=', '.join(set(categories)) if categories else '',
                doi=f"10.48550/arXiv.{doi}"  # Format arXiv ID as DOI
            )
            
            # Check if paper with this DOI already exists
            existing_paper = Research.query.filter_by(doi=new_paper.doi).first()
            if not existing_paper:
                db.session.add(new_paper)
                print(f"Added paper: {new_paper.title}")
            else:
                print(f"Paper already exists: {new_paper.title}")
            
            # Be nice to the API
            time.sleep(3)
        
        # Commit all changes
        db.session.commit()
        print(f"Successfully added {num_papers} papers to the database")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching papers: {e}")
    except Exception as e:
        print(f"Error processing papers: {e}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        # Fetch 5 random papers
        fetch_random_papers(5)