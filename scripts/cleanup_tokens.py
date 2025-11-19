#!/usr/bin/env python3
"""
Unified Token Cleanup Script

Cleanup operations:
1. Delete tokens by status (abandoned, etc.)
2. Delete tokens by tags (nft, memes, gamefi, etc.)
3. Standardize tag names (defi/DeFi -> defi, stablecoin/Stablecoin -> stablecoin)
"""

import json
import shutil
from pathlib import Path
from typing import List, Tuple, Set


def find_tokens_by_status(tokens_dir: Path, statuses: Set[str]) -> List[Tuple[Path, str, str]]:
    """Find tokens by status."""
    found_tokens = []

    for network_dir in sorted(tokens_dir.iterdir()):
        if not network_dir.is_dir() or network_dir.name.startswith('.'):
            continue

        for token_dir in sorted(network_dir.iterdir()):
            if not token_dir.is_dir() or token_dir.name.startswith('.'):
                continue

            info_file = token_dir / 'info.json'
            if not info_file.exists():
                continue

            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if data.get('status') in statuses:
                    token_name = data.get('name', 'Unknown')
                    found_tokens.append((token_dir, token_name, f"status={data.get('status')}"))
            except Exception as e:
                print(f"  Warning: Error reading {info_file}: {e}")

    return found_tokens


def find_tokens_by_tags(tokens_dir: Path, unwanted_tags: Set[str]) -> List[Tuple[Path, str, str]]:
    """Find tokens by tags."""
    found_tokens = []

    for network_dir in sorted(tokens_dir.iterdir()):
        if not network_dir.is_dir() or network_dir.name.startswith('.'):
            continue

        for token_dir in sorted(network_dir.iterdir()):
            if not token_dir.is_dir() or token_dir.name.startswith('.'):
                continue

            info_file = token_dir / 'info.json'
            if not info_file.exists():
                continue

            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                tags = data.get('tags', [])
                matching_tags = [tag for tag in tags if tag in unwanted_tags]

                if matching_tags:
                    token_name = data.get('name', 'Unknown')
                    found_tokens.append((token_dir, token_name, f"tags={','.join(matching_tags)}"))
            except Exception as e:
                print(f"  Warning: Error reading {info_file}: {e}")

    return found_tokens


def find_tokens_without_tags(tokens_dir: Path) -> List[Tuple[Path, str, str]]:
    """Find tokens without tags."""
    found_tokens = []

    for network_dir in sorted(tokens_dir.iterdir()):
        if not network_dir.is_dir() or network_dir.name.startswith('.'):
            continue

        for token_dir in sorted(network_dir.iterdir()):
            if not token_dir.is_dir() or token_dir.name.startswith('.'):
                continue

            info_file = token_dir / 'info.json'
            if not info_file.exists():
                continue

            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                tags = data.get('tags', None)

                if tags is None or len(tags) == 0:
                    token_name = data.get('name', 'Unknown')
                    found_tokens.append((token_dir, token_name, "no tags"))
            except Exception as e:
                print(f"  Warning: Error reading {info_file}: {e}")

    return found_tokens


def delete_tokens(tokens: List[Tuple[Path, str, str]], dry_run: bool = True) -> int:
    """Delete token directories."""
    deleted_count = 0

    for token_dir, token_name, reason in tokens:
        network = token_dir.parent.name
        token_id = token_dir.name

        if dry_run:
            print(f"[DRY RUN] Would delete: {network}/{token_id} - {token_name} ({reason})")
        else:
            try:
                shutil.rmtree(token_dir)
                print(f"✓ Deleted: {network}/{token_id} - {token_name} ({reason})")
                deleted_count += 1
            except Exception as e:
                print(f"✗ Error deleting {network}/{token_id}: {e}")

    return deleted_count


def standardize_tags(tokens_dir: Path, tag_mappings: dict, dry_run: bool = True) -> int:
    """Standardize tag names."""
    updated_count = 0

    for network_dir in sorted(tokens_dir.iterdir()):
        if not network_dir.is_dir() or network_dir.name.startswith('.'):
            continue

        for token_dir in sorted(network_dir.iterdir()):
            if not token_dir.is_dir() or token_dir.name.startswith('.'):
                continue

            info_file = token_dir / 'info.json'
            if not info_file.exists():
                continue

            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                tags = data.get('tags', [])
                if not tags:
                    continue

                # Check if any tags need updating
                updated_tags = [tag_mappings.get(tag, tag) for tag in tags]

                if updated_tags != tags:
                    if dry_run:
                        print(f"[DRY RUN] Would update: {network_dir.name}/{token_dir.name} - {data.get('name', 'Unknown')}")
                        print(f"  Tags: {tags} -> {updated_tags}")
                    else:
                        data['tags'] = updated_tags
                        with open(info_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=4, ensure_ascii=False)
                        print(f"✓ Updated: {network_dir.name}/{token_dir.name} - {data.get('name', 'Unknown')}")
                        print(f"  Tags: {tags} -> {updated_tags}")
                        updated_count += 1

            except Exception as e:
                print(f"  Warning: Error processing {info_file}: {e}")

    return updated_count


def main():
    """Main execution function."""
    import sys

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    tokens_dir = project_root / 'tokens'

    print("Unified Token Cleanup Script")
    print("=" * 60)
    print(f"Tokens directory: {tokens_dir}")
    print("=" * 60)
    print()

    if not tokens_dir.exists():
        print(f"Error: Tokens directory not found: {tokens_dir}")
        return 1

    # Step 1: Delete tokens with unwanted tags
    print("Step 1: Finding tokens with unwanted tags...")
    unwanted_tags = {'memes', 'gamefi', 'deflationary', 'dapp', 'defletionary', 'privacy'}
    tokens_to_delete = find_tokens_by_tags(tokens_dir, unwanted_tags)

    print(f"Found {len(tokens_to_delete)} tokens with unwanted tags")
    print()

    if tokens_to_delete:
        response = input("Delete these tokens? (yes/no): ").strip().lower()
        if response == 'yes':
            deleted = delete_tokens(tokens_to_delete, dry_run=False)
            print(f"✓ Deleted {deleted} tokens with unwanted tags")
        else:
            print("Skipped deletion")

    print()

    # Step 2: Delete tokens without tags
    print("Step 2: Finding tokens without tags...")
    tokens_without_tags = find_tokens_without_tags(tokens_dir)

    print(f"Found {len(tokens_without_tags)} tokens without tags")
    print()

    if tokens_without_tags:
        response = input("Delete these tokens? (yes/no): ").strip().lower()
        if response == 'yes':
            deleted = delete_tokens(tokens_without_tags, dry_run=False)
            print(f"✓ Deleted {deleted} tokens without tags")
        else:
            print("Skipped deletion")

    print()

    # Step 3: Standardize tags
    print("Step 3: Standardizing tag names...")
    tag_mappings = {
        'DeFi': 'defi',
        'Stablecoin': 'stablecoin'
    }

    updated = standardize_tags(tokens_dir, tag_mappings, dry_run=False)
    print(f"✓ Standardized tags in {updated} tokens")
    print()

    print("=" * 60)
    print("✓ Cleanup completed successfully!")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    import sys

    # Support dry-run mode
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        tokens_dir = project_root / 'tokens'

        print("DRY RUN MODE - No changes will be made")
        print("=" * 60)
        print()

        print("Finding tokens with unwanted tags...")
        unwanted_tags = {'memes', 'gamefi', 'deflationary', 'dapp', 'defletionary', 'privacy'}
        tokens_to_delete = find_tokens_by_tags(tokens_dir, unwanted_tags)
        print(f"Found {len(tokens_to_delete)} tokens with unwanted tags")
        if tokens_to_delete:
            delete_tokens(tokens_to_delete[:10], dry_run=True)
            if len(tokens_to_delete) > 10:
                print(f"... and {len(tokens_to_delete) - 10} more")

        print()
        print("Finding tokens without tags...")
        tokens_without_tags = find_tokens_without_tags(tokens_dir)
        print(f"Found {len(tokens_without_tags)} tokens without tags")
        if tokens_without_tags:
            delete_tokens(tokens_without_tags[:10], dry_run=True)
            if len(tokens_without_tags) > 10:
                print(f"... and {len(tokens_without_tags) - 10} more")

        print()
        print("Finding tags to standardize...")
        tag_mappings = {'DeFi': 'defi', 'Stablecoin': 'stablecoin'}
        standardize_tags(tokens_dir, tag_mappings, dry_run=True)

        sys.exit(0)

    sys.exit(main())
