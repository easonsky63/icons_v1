#!/usr/bin/env python3
"""
Token Aggregation Script

Aggregates all token information from the tokens directory and outputs to a single JSON file.
Adds chainId, chainSlug, and logo_url fields to each token.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


# Chain ID mapping - special handling for non-standard chains
SPECIAL_CHAIN_IDS = {
    'ripple': -99,
    'solana': -101,  # Solana mainnet
    'sui': -102,     # Sui mainnet
}

# Chain name mapping - for directories that don't match chainSlug exactly
CHAIN_NAME_MAPPING = {
    'avalanchec': 'avalanche',    # avalanchec → Avalanche C-Chain
    'zksync': 'zksync era',       # zksync → zkSync Mainnet
}


def load_chainlist(chainlist_path: Path) -> Dict[str, int]:
    """Load chainlist.json and create a mapping of chainSlug to chainId."""
    chain_id_map = {}

    try:
        with open(chainlist_path, 'r', encoding='utf-8') as f:
            chainlist = json.load(f)

        for chain in chainlist:
            chain_slug = chain.get('chainSlug', '').lower()
            chain_id = chain.get('chainId')

            if chain_slug and chain_id is not None:
                chain_id_map[chain_slug] = chain_id

    except Exception as e:
        print(f"Warning: Error loading chainlist.json: {e}")

    return chain_id_map


def get_chain_id(chain_name: str, chain_id_map: Dict[str, int]) -> int:
    """Get chainId for a given chain name."""
    chain_name_lower = chain_name.lower()

    # Check special mappings first
    if chain_name_lower in SPECIAL_CHAIN_IDS:
        return SPECIAL_CHAIN_IDS[chain_name_lower]

    # Check if chain name needs mapping
    mapped_chain_name = CHAIN_NAME_MAPPING.get(chain_name_lower, chain_name_lower)

    # Check chainlist mapping
    if mapped_chain_name in chain_id_map:
        return chain_id_map[mapped_chain_name]

    # Default to 0 if not found
    print(f"Warning: No chainId found for '{chain_name}' (mapped: '{mapped_chain_name}'), using 0")
    return 0


def aggregate_tokens(tokens_dir: Path, chain_id_map: Dict[str, int]) -> List[Dict]:
    """Aggregate all tokens from the tokens directory."""
    all_tokens = []

    # Iterate through each chain directory
    for chain_dir in sorted(tokens_dir.iterdir()):
        if not chain_dir.is_dir() or chain_dir.name.startswith('.'):
            continue

        chain_name = chain_dir.name
        chain_slug = chain_name.lower()
        chain_id = get_chain_id(chain_name, chain_id_map)

        print(f"Processing chain: {chain_name} (chainId: {chain_id})")

        token_count = 0

        # Iterate through each token directory
        for token_dir in sorted(chain_dir.iterdir()):
            if not token_dir.is_dir() or token_dir.name.startswith('.'):
                continue

            info_file = token_dir / 'info.json'
            if not info_file.exists():
                continue

            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    token_info = json.load(f)

                # Add chain-related fields
                token_info['chainId'] = chain_id
                token_info['chainSlug'] = chain_slug
                token_info['logo_url'] = f"https://raw.githubusercontent.com/easonsky63/icons_v1/refs/heads/main/tokens/{chain_name}/{token_dir.name}/logo.png"

                all_tokens.append(token_info)
                token_count += 1

            except Exception as e:
                print(f"  Warning: Error reading {info_file}: {e}")

        print(f"  Found {token_count} tokens")

    return all_tokens


def main():
    """Main execution function."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    tokens_dir = project_root / 'tokens'
    chainlist_file = project_root / 'chains' / 'chainlist.json'
    output_dir = script_dir / 'output'
    output_file = output_dir / 'aggregated_tokens.json'

    print("Token Aggregation Script")
    print("=" * 60)
    print(f"Tokens directory: {tokens_dir}")
    print(f"Chainlist file: {chainlist_file}")
    print(f"Output file: {output_file}")
    print("=" * 60)
    print()

    # Check if tokens directory exists
    if not tokens_dir.exists():
        print(f"Error: Tokens directory not found: {tokens_dir}")
        return 1

    # Load chainlist for chainId mapping
    chain_id_map = load_chainlist(chainlist_file)
    print(f"Loaded {len(chain_id_map)} chains from chainlist.json")
    print()

    # Aggregate all tokens
    all_tokens = aggregate_tokens(tokens_dir, chain_id_map)

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_tokens, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 60)
    print(f"✓ Successfully aggregated {len(all_tokens)} tokens")
    print(f"✓ Output saved to: {output_file}")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
