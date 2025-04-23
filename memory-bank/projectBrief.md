# Project Brief

## Overview
Building an app that will allow its users to chat with Spinoza about his Ethics. The app will use Graph RAG on several translations of the Ethics to provide context to the conversations.

## Core Features
- Data processing Python scripts to ingest different translations of the Ethics (PDF files) into a Graph RAG DB
  - Created `ingest_ethics.py` script for PDF extraction and Neo4J graph creation
  - Will process a text-based French translation PDF initially
  - Uses pdfminer.six for text extraction
- Neo4J Graph RAG DB to store every element of the Ethics and their relations (in several languages)
  - Graph structure represents parts, definitions, propositions, axioms, demonstrations, scholia, corollaries
  - Captures references between elements (e.g., when a proposition references another)
  - Node types: Part, Definition, Proposition, Axiom, Demonstration, Scholium, Corollary
  - Relationship types: CONTAINS, HAS, REFERENCES
- Next.js + Tailwind + Supabase chat app deployed in Vercel (future development)

## Target Users
Anyone interested in Spinoza's Ethics

## Technical Stack
- Python 3.12+ for backend processing
- Dependencies (added to pyproject.toml):
  - pdfminer.six for PDF text extraction
  - neo4j for database connection
  - langchain for RAG functionality
  - langchain-neo4j for Neo4J integration
  - tqdm for progress tracking
  - python-dotenv for environment management
- Neo4J for graph database
- LangChain to connect everything
- Next.js, Tailwind, and Supabase for frontend (future development)

## Implementation Progress

### Completed
1. Updated project dependencies in pyproject.toml
2. Created `ingest_ethics.py` script with:
   - Data models for Ethics elements (Part, Definition, Proposition, etc.)
   - PDF text extraction using pdfminer.six
   - Text parsing to identify structural elements
   - Reference detection between elements
   - Neo4J database setup and graph creation
   - LangChain integration for RAG capabilities
3. Enhanced `main.py` with a simple command-line interface for:
   - Checking database connection
   - Running the ingest script
   - Displaying help information
4. Created `.env.example` with configuration templates
5. Updated `README.md` with comprehensive documentation

### Next Steps
1. Enhance the parsing logic for the specific format of the French translation PDF
2. Develop the chat interface using Next.js, Tailwind, and Supabase
3. Deploy the application to Vercel

## Current Status
- Basic implementation of the PDF extraction and Neo4J graph creation is complete
- The application can be run with `python main.py`
- Next phase will focus on developing the chat interface
