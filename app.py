from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/research_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# API Configuration
API_BASE_URL = 'http://localhost:8000/api/v1'  # Your Laravel API base URL

class Research(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    authors = db.Column(db.String(200), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    publication_date = db.Column(db.DateTime, nullable=False)
    keywords = db.Column(db.String(200))
    review = db.Column(db.Text)
    doi = db.Column(db.String(100), unique=True)  # Adding DOI field with unique constraint

def fetch_laravel_materials():
    try:
        # Get all materials from Laravel API
        response = requests.get(f'{API_BASE_URL}/materials')
        if response.status_code == 200:
            materials = response.json()['data']
            
            # Filter materials to only include Research Papers with DOI
            research_papers = [
                m for m in materials 
                if m.get('category') == 'Research Paper' 
                and m.get('isbnOrDoi') is not None 
                and m.get('isbnOrDoi').strip() != ''
            ]
            
            # Get all existing DOIs from our database
            existing_dois = {paper.doi for paper in Research.query.with_entities(Research.doi).all()}
            
            # Filter out materials that already exist in our database
            new_materials = [m for m in research_papers if m.get('isbnOrDoi') not in existing_dois]
            
            return new_materials
        return []
    except requests.exceptions.RequestException:
        return []

@app.route('/')
def index():
    research_papers = Research.query.order_by(Research.publication_date.desc()).all()
    materials = fetch_laravel_materials()
    return render_template('index.html', research_papers=research_papers, materials=materials)

@app.route('/research/<int:id>')
def research_detail(id):
    research = Research.query.get_or_404(id)
    return render_template('research_detail.html', research=research)

@app.route('/material/<int:id>')
def material_detail(id):
    try:
        response = requests.get(f'{API_BASE_URL}/materials/{id}')
        if response.status_code == 200:
            material = response.json()['data']
            return render_template('material_detail.html', material=material)
        return render_template('material_detail.html', error='Material not found')
    except requests.exceptions.RequestException as e:
        return render_template('material_detail.html', error=str(e))

# API Endpoints for Laravel Integration
@app.route('/api/research/search', methods=['GET'])
def api_search_research():
    query = request.args.get('query', '')
    filters = request.args.get('filters', {})
    
    if not query:
        return jsonify({'data': []})
    
    # Search in title, abstract, authors, and keywords
    search_term = f"%{query}%"
    research_papers = Research.query.filter(
        (Research.title.like(search_term)) |
        (Research.abstract.like(search_term)) |
        (Research.authors.like(search_term)) |
        (Research.keywords.like(search_term))
    ).all()
    
    results = []
    for paper in research_papers:
        results.append({
            'id': paper.id,
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'publication_date': paper.publication_date.isoformat() if paper.publication_date else None,
            'keywords': paper.keywords,
            'doi': paper.doi
        })
        
    return jsonify({'data': results})

@app.route('/api/research/<int:id>', methods=['GET'])
def api_get_research(id):
    research = Research.query.get_or_404(id)
    
    result = {
        'id': research.id,
        'title': research.title,
        'authors': research.authors,
        'abstract': research.abstract,
        'publication_date': research.publication_date.isoformat() if research.publication_date else None,
        'keywords': research.keywords,
        'review': research.review,
        'doi': research.doi
    }
    
    return jsonify({'data': result})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 
