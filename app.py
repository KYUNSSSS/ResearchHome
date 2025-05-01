from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/research_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Research(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    authors = db.Column(db.String(200), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    publication_date = db.Column(db.DateTime, nullable=False)
    keywords = db.Column(db.String(200))
    review = db.Column(db.Text)

@app.route('/')
def index():
    research_papers = Research.query.order_by(Research.publication_date.desc()).all()
    return render_template('index.html', research_papers=research_papers)

@app.route('/research/<int:id>')
def research_detail(id):
    research = Research.query.get_or_404(id)
    return render_template('research_detail.html', research=research)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 