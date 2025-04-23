# Technical Context

## Technologies Used

### Backend

- **Python 3.12+**: Core programming language for the backend components
- **pdfminer.six**: Library for extracting text from PDF files
- **Neo4j**: Graph database for storing the structured representation of Spinoza's Ethics
- **LangChain**: Framework for developing applications with language models
- **langchain-neo4j**: Neo4J integration for LangChain
- **tqdm**: Library for displaying progress bars
- **python-dotenv**: Library for loading environment variables from .env files

### Frontend (Planned)

- **Next.js**: React framework for building the web application
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Supabase**: Backend-as-a-Service for authentication and data storage
- **Vercel**: Platform for deploying the Next.js application

## Development Setup

### Environment Setup

1. **Python Environment**:
   - Python 3.12 or higher
   - Dependencies managed through pyproject.toml
   - Virtual environment recommended (using venv or similar)

2. **Neo4J Database**:
   - Neo4J instance (local or remote)
   - Authentication credentials stored in .env file
   - Database schema created by ingest_ethics.py

3. **Configuration**:
   - Environment variables stored in .env file
   - Example configuration provided in .env.example

### Project Structure

```
spinoza-me/
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore file
├── ingest_ethics.py       # Script for PDF extraction and graph creation
├── main.py                # Main application entry point
├── memory-bank/           # Documentation and context
├── pyproject.toml         # Python project configuration
└── README.md              # Project documentation
```

## Technical Constraints

### PDF Processing

- **Text-Based PDFs**: The current implementation is designed for text-based PDFs, not scanned images
- **Language-Specific Parsing**: The parsing logic may need to be adjusted for different languages and translations
- **Reference Detection**: Detecting references between elements relies on pattern matching, which may not catch all references

### Neo4J Database

- **Connection Requirements**: Requires a running Neo4J instance with appropriate credentials
- **Schema Constraints**: The database schema includes constraints and indexes that must be maintained
- **Query Performance**: Complex queries may require optimization for performance

### LangChain Integration

- **API Compatibility**: Depends on the compatibility between LangChain and Neo4J versions
- **Model Requirements**: May require specific language models for optimal performance
- **Context Window Limitations**: Limited by the context window size of the underlying language model

## Dependencies

### Core Dependencies

```toml
dependencies = [
    "pdfminer.six",  # For text-based PDF extraction
    "neo4j",         # For Neo4J database connection
    "langchain",     # Core LangChain functionality
    "langchain-neo4j",      # Neo4J integration for LangChain
    "tqdm",          # For progress bars
    "python-dotenv", # For environment management
]
```

### Dependency Relationships

- **pdfminer.six**: Used by the PDFExtractor class in ingest_ethics.py
- **neo4j**: Used by the Neo4JDatabase class in ingest_ethics.py
- **langchain** and **langchain-neo4j**: Used by the LangChainIntegration class in ingest_ethics.py
- **tqdm**: Used throughout ingest_ethics.py for progress tracking
- **python-dotenv**: Used in both ingest_ethics.py and main.py for loading environment variables

## Tool Usage Patterns

### PDF Extraction

```python
from pdfminer.high_level import extract_text

def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text
```

### Neo4J Database Operations

```python
from neo4j import GraphDatabase

# Connect to Neo4J
driver = GraphDatabase.driver(uri, auth=(username, password))

# Create nodes
with driver.session() as session:
    session.run(
        """
        MERGE (n:NodeType {id: $id})
        SET n.property = $value
        """,
        id=node_id,
        value=property_value
    )

# Create relationships
with driver.session() as session:
    session.run(
        """
        MATCH (a {id: $a_id})
        MATCH (b {id: $b_id})
        MERGE (a)-[:RELATIONSHIP_TYPE]->(b)
        """,
        a_id=source_id,
        b_id=target_id
    )
```

### LangChain Integration

```python
from langchain.graphs import Neo4jGraph

# Create Neo4jGraph instance
graph = Neo4jGraph(
    url=neo4j_uri,
    username=neo4j_username,
    password=neo4j_password
)

# Define a Cypher query for retrieving context
query = """
MATCH (p:Proposition)-[:REFERENCES]->(ref)
WHERE p.part_number = $part_number AND p.number = $number
RETURN ref.text AS context
"""
```

## Development Workflow

1. **Environment Setup**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/spinoza-me.git
   cd spinoza-me

   # Install dependencies
   pip install -e .

   # Create .env file
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **PDF Processing**:
   ```bash
   # Run the ingest script
   python ingest_ethics.py
   ```

3. **Application Testing**:
   ```bash
   # Run the main application
   python main.py
   ```

4. **Frontend Development** (future):
   ```bash
   # Navigate to frontend directory
   cd frontend

   # Install dependencies
   npm install

   # Run development server
   npm run dev
   ```

## Deployment Considerations

- **Neo4J Database**: Can be deployed on a cloud provider or self-hosted
- **Python Backend**: Can be deployed as a serverless function or traditional server
- **Next.js Frontend**: Can be deployed on Vercel or other hosting platforms
- **Environment Variables**: Must be properly configured in the deployment environment
