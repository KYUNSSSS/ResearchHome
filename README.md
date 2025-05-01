# Research Portal

A simple web application for displaying academic research papers and their details.

## Setup Instructions

1. Create a MySQL database named `research_db` (Run XAMPP MySQL)
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Update the database connection string in `app.py` with your MySQL credentials:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/research_db'
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Access the application at `http://localhost:5000`

## Features

- Display list of research papers
- View detailed information about each research paper
- Clean and modern user interface
- MySQL database integration

## Database Schema

The application uses a single table `research` with the following columns:
- id (Primary Key)
- title
- authors
- abstract
- publication_date
- keywords
- review 