#!/usr/bin/env python3
"""
Chain Information Aggregation Script

This script aggregates chain information from individual info.json files
and merges them with data from chainlist.json to create a comprehensive
chain information database.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


def load_json_file(file_path: Path) -> Optional[Dict]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return None


def get_chain_folder_name(directory: Path) -> str:
    """Extract chain folder name from directory name."""
    # Remove _info suffix if present
    name = directory.name
    if name.endswith('_info'):
        name = name[:-5]
    return name


def find_chainlist_entry(chainlist_data: List[Dict], chain_info: Dict, folder_name: str) -> Optional[Dict]:
    """
    Find matching entry in chainlist.json based on various criteria.

    Try matching by:
    1. Chain name (exact match)
    2. Chain slug
    3. Short name
    4. Partial name match
    """
    if not chainlist_data:
        return None

    chain_name = chain_info.get('name', '').lower()

    # Try exact name match
    for entry in chainlist_data:
        if entry.get('name', '').lower() == chain_name:
            return entry

    # Try chainSlug match with folder name
    for entry in chainlist_data:
        if entry.get('chainSlug', '').lower() == folder_name.lower():
            return entry

    # Try shortName match
    for entry in chainlist_data:
        if entry.get('shortName', '').lower() == folder_name.lower():
            return entry

    # Try partial name match
    for entry in chainlist_data:
        entry_name = entry.get('name', '').lower()
        if chain_name in entry_name or entry_name in chain_name:
            return entry

    return None


def merge_chain_info(chain_info: Dict, chainlist_entry: Optional[Dict], folder_name: str) -> Dict:
    """
    Merge chain info from info.json with chainlist.json data.

    Returns optimized structure with chain info and native token info separated.
    """
    # Base structure
    merged = {
        "name": chain_info.get('name', ''),
        "shortName": chainlist_entry.get('shortName', '') if chainlist_entry else '',
        "chain": chainlist_entry.get('chain', '') if chainlist_entry else '',
        "chainSlug": chainlist_entry.get('chainSlug', folder_name) if chainlist_entry else folder_name,
        "chainId": chainlist_entry.get('chainId', 0) if chainlist_entry else 0,
        "logo": f"https://raw.githubusercontent.com/easonsky63/icons_v1/refs/heads/main/chains/{folder_name}_info/logo.png",
        "website": chain_info.get('website', ''),
        "description": chain_info.get('description', ''),
        "explorer": chain_info.get('explorer', ''),
    }

    # Extract native currency info
    # Prefer chainlist.json nativeCurrency, fallback to info.json fields
    if chainlist_entry and 'nativeCurrency' in chainlist_entry:
        native_currency = chainlist_entry['nativeCurrency']
    else:
        # Build from info.json
        native_currency = {
            "name": chain_info.get('name', ''),
            "symbol": chain_info.get('symbol', ''),
            "decimals": chain_info.get('decimals', 18)
        }

    merged["nativeCurrency"] = {
        "name": native_currency.get('name', ''),
        "symbol": native_currency.get('symbol', ''),
        "decimals": native_currency.get('decimals', 18)
    }

    return merged


def aggregate_chains(chains_dir: Path, chainlist_path: Path, output_dir: Path) -> Dict:
    """
    Aggregate all chain information into a single structure.

    Args:
        chains_dir: Directory containing chain info folders
        chainlist_path: Path to chainlist.json
        output_dir: Directory to save output

    Returns:
        Dictionary containing aggregated chain data
    """
    # Load chainlist.json
    chainlist_data = load_json_file(chainlist_path)
    if not chainlist_data:
        print("Warning: Could not load chainlist.json")
        chainlist_data = []

    aggregated_chains = []

    # Iterate through all chain directories
    for chain_dir in sorted(chains_dir.iterdir()):
        if not chain_dir.is_dir() or chain_dir.name.startswith('.'):
            continue

        # Look for info.json in this directory
        info_json_path = chain_dir / 'info.json'
        if not info_json_path.exists():
            print(f"Warning: No info.json found in {chain_dir.name}")
            continue

        # Load chain info
        chain_info = load_json_file(info_json_path)
        if not chain_info:
            continue

        # Get folder name for logo URL
        folder_name = get_chain_folder_name(chain_dir)

        # Find matching entry in chainlist.json
        chainlist_entry = find_chainlist_entry(chainlist_data, chain_info, folder_name)

        if not chainlist_entry:
            print(f"Warning: No chainlist.json entry found for {chain_info.get('name', folder_name)}")

        # Merge and create optimized structure
        merged_chain = merge_chain_info(chain_info, chainlist_entry, folder_name)
        aggregated_chains.append(merged_chain)

        print(f"✓ Processed: {merged_chain['name']}")

    # Create output structure
    output = {
        "version": "1.0.0",
        "updated": None,  # Will be set when saved
        "chains": aggregated_chains
    }

    return output


def save_output(data: Dict, output_path: Path) -> None:
    """Save aggregated data to JSON file."""
    from datetime import datetime, timezone

    # Add timestamp
    data["updated"] = datetime.now(timezone.utc).isoformat()

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save with pretty formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Aggregated data saved to: {output_path}")
    print(f"✓ Total chains: {len(data['chains'])}")


def main():
    """Main execution function."""
    # Define paths relative to script location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    chains_dir = project_root / 'chains'
    chainlist_path = chains_dir / 'chainlist.json'
    output_dir = script_dir / 'output'
    output_path = output_dir / 'aggregated_chains.json'

    print("Chain Information Aggregation Script")
    print("=" * 50)
    print(f"Chains directory: {chains_dir}")
    print(f"Chainlist file: {chainlist_path}")
    print(f"Output directory: {output_dir}")
    print("=" * 50)
    print()

    # Validate paths
    if not chains_dir.exists():
        print(f"Error: Chains directory not found: {chains_dir}")
        return 1

    if not chainlist_path.exists():
        print(f"Error: chainlist.json not found: {chainlist_path}")
        return 1

    # Aggregate chain information
    try:
        aggregated_data = aggregate_chains(chains_dir, chainlist_path, output_dir)

        # Save output
        save_output(aggregated_data, output_path)

        print("\n✓ Aggregation completed successfully!")
        return 0

    except Exception as e:
        print(f"\n✗ Error during aggregation: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
