# Spinoza-Me

An application that allows users to chat with Spinoza about his Ethics.

## Overview

Spinoza-Me is a chatbot application that uses Graph RAG (Retrieval-Augmented Generation) on several translations of Spinoza's Ethics to provide context to conversations. Users can ask questions about Spinoza's philosophical work, and the application will provide informed responses based on the content of the Ethics.

## Features

- **PDF Extraction**: Extract text from PDF files containing translations of Spinoza's Ethics
- **Graph RAG Database**: Store the structure and relationships of the Ethics in a Neo4J graph database
- **Chatbot Interface**: Interact with Spinoza's ideas through a conversational interface

## Project Structure

- `ingest_ethics.py`: Script for extracting text from PDFs and creating the Neo4J graph database
- `main.py`: Main application entry point
- `.env.example`: Example environment variables configuration

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Neo4J database (local or remote)
- PDF files of Spinoza's Ethics translations

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/spinoza-me.git
   cd spinoza-me
   ```

2. Install dependencies:
   ```
   pip install -e .
   ```

3. Create a `.env` file based on `.env.example` and configure your Neo4J database and PDF path:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Usage

1. Run the ingest script to process PDF files and create the graph database:
   ```
   python ingest_ethics.py
   ```

2. Run the main application:
   ```
   python main.py
   ```

## Data Model

The Neo4J graph database has the following structure:

- **Nodes**:
  - `Part`: Represents a part of the Ethics
  - `Definition`: Represents a definition
  - `Proposition`: Represents a proposition
  - `Axiom`: Represents an axiom
  - `Demonstration`: Represents a demonstration
  - `Scholium`: Represents a scholium
  - `Corollary`: Represents a corollary

- **Relationships**:
  - `(Part)-[:CONTAINS]->(Definition/Proposition/Axiom/Corollary)`: A part contains elements
  - `(Proposition)-[:HAS]->(Demonstration/Scholium/Corollary)`: A proposition has related elements
  - `(Proposition/Definition)-[:REFERENCES]->(Proposition/Definition/Axiom)`: An element references another

## Future Development

- Support for multiple translations in different languages
- Enhanced reference detection
- Web interface with Next.js, Tailwind, and Supabase
- Deployment to Vercel

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
