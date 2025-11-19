# Chain Aggregation Scripts

This directory contains scripts for processing and aggregating blockchain chain information.

## Scripts

### aggregate_chains.py

Aggregates chain information from individual `info.json` files in the `chains/` directory and merges them with data from `chainlist.json` to create a comprehensive chain database.

#### Usage

```bash
python3 scripts/aggregate_chains.py
```

Or make it executable and run directly:

```bash
chmod +x scripts/aggregate_chains.py
./scripts/aggregate_chains.py
```

#### What it does

1. **Reads all chain directories**: Scans the `chains/` directory for folders ending in `_info`
2. **Loads info.json files**: Reads the `info.json` from each chain directory
3. **Merges with chainlist.json**: Looks up additional information from `chains/chainlist.json`
4. **Generates optimized structure**: Creates a standardized format with:
   - Chain information (name, chainId, website, description, explorer)
   - Native token information (name, symbol, decimals)
5. **Outputs aggregated data**: Saves to `scripts/output/aggregated_chains.json`

#### Output Structure

The script generates a JSON file with the following structure:

```json
{
  "version": "1.0.0",
  "updated": "2025-11-18T07:54:23.154444+00:00",
  "chains": [
    {
      "name": "BNB Smart Chain",
      "shortName": "bnb",
      "chain": "BSC",
      "chainSlug": "binance",
      "chainId": 56,
      "logo": "https://raw.githubusercontent.com/easonsky63/icons_v1/refs/heads/main/chains/smartchain_info/logo.png",
      "website": "https://www.bnbchain.world/en/smartChain",
      "description": "A blockchain with a full-fledged environment...",
      "explorer": "https://bscscan.com/",
      "nativeCurrency": {
        "name": "BNB Chain Native Token",
        "symbol": "BNB",
        "decimals": 18
      }
    }
  ]
}
```

#### Data Sources

- **Primary source**: `chains/{chain_folder}/info.json` files
- **Supplementary data**: `chains/chainlist.json`
- **Logo URLs**: Generated automatically based on folder name

#### Logo URL Format

Logos are referenced using the pattern:
```
https://raw.githubusercontent.com/easonsky63/icons_v1/refs/heads/main/chains/{folder_name}_info/logo.png
```

For example:
- `chains/smartchain_info/logo.png` → `https://raw.githubusercontent.com/.../chains/smartchain_info/logo.png`

#### Matching Strategy

The script matches chains from `info.json` with `chainlist.json` entries using multiple strategies:

1. **Exact name match**: Direct comparison of chain names
2. **Chain slug match**: Matches folder name with `chainSlug` field
3. **Short name match**: Matches folder name with `shortName` field
4. **Partial name match**: Fuzzy matching for similar names

If no match is found in `chainlist.json`, the script will still process the chain using data from `info.json` only.

#### Important Notes

- **Original files preserved**: The script never modifies the original `info.json` files in chain directories
- **Output directory**: All output is saved to `scripts/output/`
- **Warnings**: The script will warn about chains not found in `chainlist.json` but will continue processing
- **Error handling**: Invalid JSON files are skipped with warning messages

#### Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

#### Output Location

```
scripts/
└── output/
    └── aggregated_chains.json
```


新增 token 后，只需运行以下命令即可重新聚合：

  python3 scripts/aggregate_tokens.py

  操作步骤：

  1. 新增 token 文件夹
  tokens/{chain_name}/{token_address}/
  ├── info.json
  └── logo.png
  2. 执行脚本
  cd /Users/zhengwang/Programming/icons_v1
  python3 scripts/aggregate_tokens.py
  3. 输出
    - 更新后的聚合文件: scripts/output/aggregated_tokens.json