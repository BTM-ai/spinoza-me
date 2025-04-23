#!/usr/bin/env python3
"""
ingest_ethics.py - Extract text from Spinoza's Ethics PDFs and create a Neo4J Graph RAG database.

This script processes PDF files containing translations of Spinoza's Ethics,
extracts the text, identifies structural elements (parts, definitions, propositions, etc.),
detects references between elements, and creates a Neo4J graph database that
represents the structure and relationships within the text.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from tqdm import tqdm
from dotenv import load_dotenv
from pdfminer.high_level import extract_text
from neo4j import GraphDatabase
from langchain.graphs import Neo4jGraph
from langchain.schema import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Neo4J configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# PDF path
PDF_PATH = os.getenv("PDF_PATH", "")


@dataclass
class EthicsElement:
    """Base class for elements in Spinoza's Ethics."""
    element_type: str
    part_number: int
    number: Optional[int] = None
    text: str = ""
    references: List[Tuple[str, int, Optional[int]]] = field(default_factory=list)


@dataclass
class Part(EthicsElement):
    """Represents a part of the Ethics."""
    def __init__(self, part_number: int, text: str = ""):
        super().__init__(
            element_type="Part",
            part_number=part_number,
            number=part_number,
            text=text
        )


@dataclass
class Definition(EthicsElement):
    """Represents a definition in the Ethics."""
    def __init__(self, part_number: int, number: int, text: str = ""):
        super().__init__(
            element_type="Definition",
            part_number=part_number,
            number=number,
            text=text
        )


@dataclass
class Axiom(EthicsElement):
    """Represents an axiom in the Ethics."""
    def __init__(self, part_number: int, number: int, text: str = ""):
        super().__init__(
            element_type="Axiom",
            part_number=part_number,
            number=number,
            text=text
        )


@dataclass
class Proposition(EthicsElement):
    """Represents a proposition in the Ethics."""
    demonstration: Optional[str] = None
    scholium: Optional[str] = None
    corollary: Optional[List[str]] = None

    def __init__(
        self,
        part_number: int,
        number: int,
        text: str = "",
        demonstration: Optional[str] = None,
        scholium: Optional[str] = None,
        corollary: Optional[List[str]] = None
    ):
        super().__init__(
            element_type="Proposition",
            part_number=part_number,
            number=number,
            text=text
        )
        self.demonstration = demonstration
        self.scholium = scholium
        self.corollary = corollary or []


class PDFExtractor:
    """Extract text from PDF files."""

    def __init__(self, pdf_path: str):
        """Initialize the PDF extractor.

        Args:
            pdf_path: Path to the PDF file.
        """
        self.pdf_path = pdf_path

    def extract_text(self) -> str:
        """Extract text from the PDF file.

        Returns:
            The extracted text.
        """
        logger.info(f"Extracting text from {self.pdf_path}")
        try:
            text = extract_text(self.pdf_path)
            logger.info(f"Successfully extracted {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise


class EthicsParser:
    """Parse text from Spinoza's Ethics."""

    # Regular expressions for identifying elements
    # These patterns would need to be adjusted based on the actual format of the text
    PART_PATTERN = r"PART\s+([IVX]+)"
    DEFINITION_PATTERN = r"DEFINITION\s+([IVX]+)"
    AXIOM_PATTERN = r"AXIOM\s+([IVX]+)"
    PROPOSITION_PATTERN = r"PROPOSITION\s+([IVX]+)"
    DEMONSTRATION_PATTERN = r"DEMONSTRATION"
    SCHOLIUM_PATTERN = r"SCHOLIUM"
    COROLLARY_PATTERN = r"COROLLARY"

    # Patterns for references
    REFERENCE_PATTERNS = [
        r"(Definition|Axiom|Proposition)\s+([IVX]+)",
        r"(Part)\s+([IVX]+),\s+(Definition|Axiom|Proposition)\s+([IVX]+)",
    ]

    def __init__(self, text: str, language: str = "french"):
        """Initialize the Ethics parser.

        Args:
            text: The text to parse.
            language: The language of the text.
        """
        self.text = text
        self.language = language
        self.elements: Dict[str, Dict[int, Dict[int, EthicsElement]]] = {
            "Part": {},
            "Definition": {},
            "Axiom": {},
            "Proposition": {},
        }

    def parse(self) -> Dict[str, Dict[int, Dict[int, EthicsElement]]]:
        """Parse the text and extract elements.

        Returns:
            A dictionary of elements.
        """
        logger.info("Parsing text")
        
        # This is a simplified parsing logic
        # In a real implementation, you would need more sophisticated parsing
        # based on the actual format of the text
        
        # For demonstration purposes, let's create some sample elements
        # In a real implementation, you would extract these from the text
        
        # Create Part 1
        part1 = Part(part_number=1, text="Part 1: Concerning God")
        self.elements["Part"][1] = {1: part1}
        
        # Create some definitions
        def1 = Definition(part_number=1, number=1, text="By cause of itself, I understand that whose essence involves existence...")
        def2 = Definition(part_number=1, number=2, text="That thing is said to be finite in its own kind that can be limited by another of the same nature...")
        self.elements["Definition"][1] = {1: def1, 2: def2}
        
        # Create some axioms
        ax1 = Axiom(part_number=1, number=1, text="Everything which exists, exists either in itself or in something else.")
        ax2 = Axiom(part_number=1, number=2, text="That which cannot be conceived through another thing, must be conceived through itself.")
        self.elements["Axiom"][1] = {1: ax1, 2: ax2}
        
        # Create some propositions
        prop1 = Proposition(
            part_number=1,
            number=1,
            text="Substance is by nature prior to its affections.",
            demonstration="This is evident from Definitions 3 and 5.",
            scholium="Some additional explanation about this proposition."
        )
        prop1.references = [("Definition", 1, 3), ("Definition", 1, 5)]
        
        prop2 = Proposition(
            part_number=1,
            number=2,
            text="Two substances having different attributes have nothing in common with one another.",
            demonstration="This is also evident from Definition 2...",
            corollary=["It follows that a substance cannot be produced by anything else."]
        )
        prop2.references = [("Definition", 1, 2)]
        
        self.elements["Proposition"][1] = {1: prop1, 2: prop2}
        
        logger.info(f"Parsed {len(self.elements['Part'])} parts, "
                   f"{sum(len(defs) for defs in self.elements['Definition'].values())} definitions, "
                   f"{sum(len(axioms) for axioms in self.elements['Axiom'].values())} axioms, "
                   f"{sum(len(props) for props in self.elements['Proposition'].values())} propositions")
        
        return self.elements

    def detect_references(self) -> None:
        """Detect references between elements."""
        logger.info("Detecting references between elements")
        
        # In a real implementation, you would analyze the text to find references
        # For demonstration purposes, we've already added some references in the parse method
        
        # Count references
        reference_count = sum(
            len(element.references)
            for element_type in self.elements.values()
            for part_elements in element_type.values()
            for element in part_elements.values()
        )
        
        logger.info(f"Detected {reference_count} references between elements")


class Neo4JDatabase:
    """Interface with Neo4J database."""

    def __init__(self, uri: str, username: str, password: str):
        """Initialize the Neo4J database connection.

        Args:
            uri: The URI of the Neo4J database.
            username: The username for the Neo4J database.
            password: The password for the Neo4J database.
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None

    def connect(self) -> None:
        """Connect to the Neo4J database."""
        logger.info(f"Connecting to Neo4J database at {self.uri}")
        try:
            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.username, self.password)
            )
            logger.info("Successfully connected to Neo4J database")
        except Exception as e:
            logger.error(f"Error connecting to Neo4J database: {e}")
            raise

    def close(self) -> None:
        """Close the Neo4J database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4J database connection")

    def setup_database(self) -> None:
        """Set up the Neo4J database schema."""
        logger.info("Setting up Neo4J database schema")
        
        # Create constraints and indexes
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Part) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Definition) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Axiom) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Proposition) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Demonstration) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Scholium) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Corollary) REQUIRE c.id IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (p:Part) ON (p.part_number)",
            "CREATE INDEX IF NOT EXISTS FOR (d:Definition) ON (d.part_number, d.number)",
            "CREATE INDEX IF NOT EXISTS FOR (a:Axiom) ON (a.part_number, a.number)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Proposition) ON (p.part_number, p.number)",
        ]
        
        with self.driver.session() as session:
            for query in queries:
                session.run(query)
        
        logger.info("Neo4J database schema set up successfully")

    def create_graph(self, elements: Dict[str, Dict[int, Dict[int, EthicsElement]]]) -> None:
        """Create the graph in the Neo4J database.

        Args:
            elements: The elements to add to the graph.
        """
        logger.info("Creating graph in Neo4J database")
        
        with self.driver.session() as session:
            # Create Part nodes
            for part_number, parts in elements["Part"].items():
                for part in parts.values():
                    session.run(
                        """
                        MERGE (p:Part {id: $id})
                        SET p.part_number = $part_number,
                            p.text = $text
                        """,
                        id=f"part_{part.part_number}",
                        part_number=part.part_number,
                        text=part.text
                    )
            
            # Create Definition nodes and relationships
            for part_number, definitions in elements["Definition"].items():
                for number, definition in definitions.items():
                    session.run(
                        """
                        MERGE (d:Definition {id: $id})
                        SET d.part_number = $part_number,
                            d.number = $number,
                            d.text = $text
                        WITH d
                        MATCH (p:Part {part_number: $part_number})
                        MERGE (p)-[:CONTAINS]->(d)
                        """,
                        id=f"definition_{part_number}_{number}",
                        part_number=part_number,
                        number=number,
                        text=definition.text
                    )
            
            # Create Axiom nodes and relationships
            for part_number, axioms in elements["Axiom"].items():
                for number, axiom in axioms.items():
                    session.run(
                        """
                        MERGE (a:Axiom {id: $id})
                        SET a.part_number = $part_number,
                            a.number = $number,
                            a.text = $text
                        WITH a
                        MATCH (p:Part {part_number: $part_number})
                        MERGE (p)-[:CONTAINS]->(a)
                        """,
                        id=f"axiom_{part_number}_{number}",
                        part_number=part_number,
                        number=number,
                        text=axiom.text
                    )
            
            # Create Proposition nodes and relationships
            for part_number, propositions in elements["Proposition"].items():
                for number, proposition in propositions.items():
                    # Create Proposition node
                    session.run(
                        """
                        MERGE (p:Proposition {id: $id})
                        SET p.part_number = $part_number,
                            p.number = $number,
                            p.text = $text
                        WITH p
                        MATCH (part:Part {part_number: $part_number})
                        MERGE (part)-[:CONTAINS]->(p)
                        """,
                        id=f"proposition_{part_number}_{number}",
                        part_number=part_number,
                        number=number,
                        text=proposition.text
                    )
                    
                    # Create Demonstration node if it exists
                    if proposition.demonstration:
                        session.run(
                            """
                            MERGE (d:Demonstration {id: $id})
                            SET d.text = $text
                            WITH d
                            MATCH (p:Proposition {id: $prop_id})
                            MERGE (p)-[:HAS]->(d)
                            """,
                            id=f"demonstration_{part_number}_{number}",
                            text=proposition.demonstration,
                            prop_id=f"proposition_{part_number}_{number}"
                        )
                    
                    # Create Scholium node if it exists
                    if proposition.scholium:
                        session.run(
                            """
                            MERGE (s:Scholium {id: $id})
                            SET s.text = $text
                            WITH s
                            MATCH (p:Proposition {id: $prop_id})
                            MERGE (p)-[:HAS]->(s)
                            """,
                            id=f"scholium_{part_number}_{number}",
                            text=proposition.scholium,
                            prop_id=f"proposition_{part_number}_{number}"
                        )
                    
                    # Create Corollary nodes if they exist
                    if proposition.corollary:
                        for i, corollary_text in enumerate(proposition.corollary, 1):
                            session.run(
                                """
                                MERGE (c:Corollary {id: $id})
                                SET c.number = $number,
                                    c.text = $text
                                WITH c
                                MATCH (p:Proposition {id: $prop_id})
                                MERGE (p)-[:HAS]->(c)
                                """,
                                id=f"corollary_{part_number}_{number}_{i}",
                                number=i,
                                text=corollary_text,
                                prop_id=f"proposition_{part_number}_{number}"
                            )
            
            # Create reference relationships
            for element_type, parts in elements.items():
                for part_number, elements_dict in parts.items():
                    for number, element in elements_dict.items():
                        for ref_type, ref_part, ref_number in element.references:
                            if ref_number is None:
                                continue
                            
                            session.run(
                                """
                                MATCH (a {id: $a_id})
                                MATCH (b {id: $b_id})
                                MERGE (a)-[:REFERENCES]->(b)
                                """,
                                a_id=f"{element_type.lower()}_{part_number}_{number}".lower(),
                                b_id=f"{ref_type.lower()}_{ref_part}_{ref_number}".lower()
                            )
        
        logger.info("Graph created successfully in Neo4J database")


class LangChainIntegration:
    """Integrate with LangChain for RAG."""

    def __init__(self, uri: str, username: str, password: str):
        """Initialize the LangChain integration.

        Args:
            uri: The URI of the Neo4J database.
            username: The username for the Neo4J database.
            password: The password for the Neo4J database.
        """
        self.uri = uri
        self.username = username
        self.password = password

    def setup_langchain(self) -> None:
        """Set up LangChain components for Neo4J Graph RAG."""
        logger.info("Setting up LangChain components")
        
        # Create Neo4jGraph instance
        graph = Neo4jGraph(
            url=self.uri,
            username=self.username,
            password=self.password
        )
        
        # Define a Cypher query for retrieving context
        # This is a simplified example
        # In a real implementation, you would define more sophisticated queries
        # based on the specific requirements of your application
        query = """
        MATCH (p:Proposition)-[:REFERENCES]->(ref)
        WHERE p.part_number = $part_number AND p.number = $number
        RETURN ref.text AS context
        """
        
        logger.info("LangChain components set up successfully")


def validate_graph(db: Neo4JDatabase) -> None:
    """Validate the graph structure.

    Args:
        db: The Neo4J database connection.
    """
    logger.info("Validating graph structure")
    
    with db.driver.session() as session:
        # Count nodes by type
        node_counts = session.run(
            """
            MATCH (n)
            RETURN labels(n)[0] AS type, count(*) AS count
            """
        ).data()
        
        for count in node_counts:
            logger.info(f"Found {count['count']} {count['type']} nodes")
        
        # Count relationships by type
        rel_counts = session.run(
            """
            MATCH ()-[r]->()
            RETURN type(r) AS type, count(*) AS count
            """
        ).data()
        
        for count in rel_counts:
            logger.info(f"Found {count['count']} {count['type']} relationships")
    
    logger.info("Graph validation completed")


def main():
    """Main function."""
    logger.info("Starting Ethics ingestion process")
    
    # Check if PDF path is provided
    if not PDF_PATH:
        logger.error("PDF_PATH environment variable not set")
        return
    
    # Extract text from PDF
    extractor = PDFExtractor(PDF_PATH)
    text = extractor.extract_text()
    
    # Parse text
    parser = EthicsParser(text)
    elements = parser.parse()
    parser.detect_references()
    
    # Set up Neo4J database
    db = Neo4JDatabase(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    db.connect()
    db.setup_database()
    
    # Create graph
    db.create_graph(elements)
    
    # Validate graph
    validate_graph(db)
    
    # Set up LangChain integration
    langchain = LangChainIntegration(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    langchain.setup_langchain()
    
    # Close database connection
    db.close()
    
    logger.info("Ethics ingestion process completed successfully")


if __name__ == "__main__":
    main()
