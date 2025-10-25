import arxiv
from datetime import datetime, timedelta
from app import db
from app.models import Source, Idea
from app.services.idea_extractor import IdeaExtractor

class ArxivScraper:
    """Scraper for arXiv papers"""
    
    def __init__(self, config):
        self.config = config
        self.max_results = config.get('ARXIV_MAX_RESULTS', 50)
        self.idea_extractor = IdeaExtractor(config)
    
    def scrape(self, categories=['cs.AI', 'cs.LG', 'stat.ML'], days_back=7):
        """Scrape recent papers from arXiv"""
        results = []
        
        # Create or get source
        source = Source.query.filter_by(
            name='arXiv',
            type='arxiv'
        ).first()
        
        if not source:
            source = Source(
                name='arXiv',
                url='https://arxiv.org',
                type='arxiv'
            )
            db.session.add(source)
            db.session.commit()
        
        # Build search query
        category_query = ' OR '.join([f'cat:{cat}' for cat in categories])
        
        # Search arXiv
        search = arxiv.Search(
            query=category_query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        for result in search.results():
            # Check if paper is recent
            if result.published < datetime.now() - timedelta(days=days_back):
                continue
            
            # Check if already exists
            existing = Idea.query.filter_by(
                source_id=source.id,
                title=result.title
            ).first()
            
            if existing:
                continue
            
            # Extract keywords from categories
            keywords = [cat.term for cat in result.categories]
            
            # Create idea
            idea = Idea(
                source_id=source.id,
                title=result.title,
                abstract=result.summary,
                keywords=keywords
            )
            
            # Extract claim and embedding
            try:
                extracted = self.idea_extractor.extract(idea)
                idea.extracted_claim = extracted.get('claim')
                idea.confidence_score = extracted.get('confidence', 0.0)
                idea.embedding = extracted.get('embedding')
            except Exception as e:
                print(f"Failed to extract from idea: {str(e)}")
            
            db.session.add(idea)
            results.append(idea)
        
        db.session.commit()
        
        # Update source last_scraped
        source.last_scraped = datetime.utcnow()
        db.session.commit()
        
        return results

def run_scraper(config):
    """Run the arXiv scraper"""
    scraper = ArxivScraper(config)
    results = scraper.scrape()
    return {
        'count': len(results),
        'ideas': [idea.to_dict() for idea in results]
    }

