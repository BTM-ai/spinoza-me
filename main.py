#!/usr/bin/env python3
"""
main.py - Main entry point for the Spinoza-Me application.

This script provides a simple interface to interact with the Spinoza-Me application,
which allows users to chat with Spinoza about his Ethics.
"""

import os
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain.graphs import Neo4jGraph

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


def check_database_connection():
    """Check if the Neo4J database is accessible."""
    logger.info(f"Checking connection to Neo4J database at {NEO4J_URI}")
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) AS count").single()
            count = result["count"]
            logger.info(f"Successfully connected to Neo4J database. Found {count} nodes.")
        driver.close()
        return True
    except Exception as e:
        logger.error(f"Error connecting to Neo4J database: {e}")
        return False


def display_welcome_message():
    """Display a welcome message for the application."""
    print("\n" + "=" * 80)
    print("Welcome to Spinoza-Me!")
    print("A chatbot application to discuss Spinoza's Ethics.")
    print("=" * 80 + "\n")


def display_database_status():
    """Display the status of the Neo4J database."""
    if check_database_connection():
        print("✅ Neo4J database is connected and accessible.")
    else:
        print("❌ Neo4J database is not accessible. Please check your configuration.")
        print("   You may need to run the ingest_ethics.py script first to set up the database.")


def display_help():
    """Display help information for the application."""
    print("\nAvailable commands:")
    print("  help     - Display this help message")
    print("  ingest   - Run the ingest_ethics.py script to process PDF files")
    print("  exit     - Exit the application")
    print("")


def run_ingest_script():
    """Run the ingest_ethics.py script."""
    print("\nRunning ingest_ethics.py script...")
    try:
        import subprocess
        result = subprocess.run(["python", "ingest_ethics.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ingest script completed successfully.")
        else:
            print("❌ Ingest script failed with the following error:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running ingest script: {e}")


def main():
    """Main function for the Spinoza-Me application."""
    display_welcome_message()
    display_database_status()
    display_help()
    
    while True:
        command = input("\nEnter a command (or 'help' for available commands): ").strip().lower()
        
        if command == "help":
            display_help()
        elif command == "ingest":
            run_ingest_script()
        elif command == "exit":
            print("\nThank you for using Spinoza-Me. Goodbye!")
            break
        else:
            print(f"Unknown command: {command}")
            display_help()


if __name__ == "__main__":
    main()
