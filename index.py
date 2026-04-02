"""
Vercel serverless function entry point wrapper.
This file must be inside the api/ directory for Vercel to detect it.
"""
import sys
import os

# Add the project root to the Python path so our modules can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
