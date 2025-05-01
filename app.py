from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
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

def fetch_laravel_materials():
    try:
        response = requests.get(f'{API_BASE_URL}/materials')
        if response.status_code == 200:
            return response.json()['data']
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 