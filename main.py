#!/usr/bin/env python
"""
Main entry point for the Smart Recommendation System application.
This script initializes the database and runs the Flask application.
"""

from app import app
from seed_data import df
import os

def main():
    """Initialize and run the Smart Recommendation System"""
    
    # Ensure data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Seed initial data if books.csv doesn't exist
    if not os.path.exists('data/books.csv'):
        print("Initializing database with sample books...")
        # Books data will be created by seed_data.py
        df.to_csv('data/books.csv', index=False)
        print("[OK] Database initialized with 28 sample books")
    else:
        print("[OK] Database already exists")
    
    print("\n" + "="*60)
    print("Starting Smart Recommendation System...")
    print("="*60)
    print("Open your browser and go to: http://localhost:5001")
    print("Default routes:")
    print("  - Login: http://localhost:5001/login")
    print("  - Sign up: http://localhost:5001/signup")
    print("="*60 + "\n")
    
    # Run the Flask application
    app.run(debug=True, port=5001, host='localhost')

if __name__ == '__main__':
    main()
