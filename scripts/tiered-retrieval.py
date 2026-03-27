#!/usr/bin/env python3
"""
tiered-retrieval.py - Tiered knowledge retrieval system

Implements 3-tier retrieval:
1. Check entity summary.md first (fast)
2. Query QMD if summary insufficient (semantic search)
3. Load specific facts from items.json (detailed)

Usage:
    python3 tiered-retrieval.py "Who is Ian?"
    python3 tiered-retrieval.py --entity ian "What does Ian do?"
    python3 tiered-retrieval.py --deep "Tell me about water polo friends"
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

LIFE_DIR = Path.home() / "clawd" / "life"
AREAS_DIR = LIFE_DIR / "areas"

def search_summary(entity_name: str) -> str:
    """Tier 1: Load entity summary directly"""
    # Check people first
    people_path = AREAS_DIR / "people" / entity_name / "summary.md"
    if people_path.exists():
        with open(people_path, 'r') as f:
            return f.read()
    
    # Check companies
    companies_path = AREAS_DIR / "companies" / entity_name / "summary.md"
    if companies_path.exists():
        with open(companies_path, 'r') as f:
            return f.read()
    
    return None

def search_qmd(query: str, collection: str = "life", limit: int = 5) -> str:
    """Tier 2: Semantic search using QMD"""
    cmd = ["qmd", "search", query, "-c", collection, "-n", str(limit)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error searching QMD: {e.stderr}"

def load_facts(entity_name: str, fact_categories: list = None) -> dict:
    """Tier 3: Load detailed atomic facts from items.json"""
    # Check people first
    people_path = AREAS_DIR / "people" / entity_name / "items.json"
    if people_path.exists():
        json_path = people_path
    else:
        # Check companies
        companies_path = AREAS_DIR / "companies" / entity_name / "items.json"
        if companies_path.exists():
            json_path = companies_path
        else:
            return None
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Filter by categories if specified
    if fact_categories:
        filtered_facts = [
            fact for fact in data.get("facts", [])
            if fact.get("category") in fact_categories
        ]
        data["facts"] = filtered_facts
    
    # Update access metadata
    for fact in data.get("facts", []):
        fact["lastAccessed"] = "2026-02-01"  # TODO: Use actual date
        fact["accessCount"] = fact.get("accessCount", 0) + 1
    
    # Save updated access metadata
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return data

def tiered_search(query: str, entity: str = None, deep: bool = False):
    """Execute tiered retrieval"""
    print(f"Query: {query}\n")
    
    # Tier 1: If entity specified, try summary first
    if entity:
        print(f"[Tier 1] Checking {entity} summary...")
        summary = search_summary(entity)
        if summary:
            print(f"\n{summary}\n")
            if not deep:
                return
        else:
            print(f"No summary found for {entity}\n")
    
    # Tier 2: Semantic search
    print("[Tier 2] Searching knowledge base with QMD...")
    qmd_results = search_qmd(query)
    print(f"\n{qmd_results}\n")
    
    # Tier 3: Deep dive if requested
    if deep and entity:
        print(f"[Tier 3] Loading detailed facts for {entity}...")
        facts = load_facts(entity)
        if facts:
            print(f"\nEntity: {facts['entity']}")
            print(f"Type: {facts['entityType']}")
            print(f"Category: {facts['category']}")
            print(f"\nFacts ({len(facts['facts'])}):")
            for fact in facts['facts']:
                print(f"  [{fact['id']}] {fact['fact']}")
                print(f"    Category: {fact['category']} | Source: {fact['source']} | Status: {fact['status']}")
        else:
            print(f"No detailed facts found for {entity}")

def main():
    parser = argparse.ArgumentParser(
        description="Tiered knowledge retrieval system"
    )
    parser.add_argument(
        "query",
        help="Search query"
    )
    parser.add_argument(
        "--entity", "-e",
        help="Specific entity to search (e.g., 'ian', 'jacky', 'george-st-growth')"
    )
    parser.add_argument(
        "--deep", "-d",
        action="store_true",
        help="Load detailed atomic facts (Tier 3)"
    )
    parser.add_argument(
        "--collection", "-c",
        default="life",
        help="QMD collection to search (default: life)"
    )
    
    args = parser.parse_args()
    
    tiered_search(args.query, args.entity, args.deep)

if __name__ == "__main__":
    main()
