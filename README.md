# JolTax-CLI

**JolTax-CLI** is an interactive "Taxonomic Shell" for exploring and querying taxonomies. It is built on top of the [`JolTax`](https://github.com/SweBiTS/JolTax) library, leveraging vectorized operations and binary caches to provide nearly instantaneous results even for massive datasets like the NCBI taxonomy.

## Key Features

- **Interactive REPL:** A persistent shell environment with context-aware auto-completion, command history, and a real-time status bar.
- **Sleek UX:** Features syntax highlighting, interactive taxonomy selection, and live memory usage tracking.
- **High Performance:** Utilizes the `JolTax` vectorized backend for $O(1)$ and $O(\log N)$ taxonomic queries.
- **Flexible Configuration:** Manage multiple taxonomy caches (e.g., NCBI, GTDB) and switch between them seamlessly.
- **Direct Build:** Create optimized binary caches directly from NCBI-style `.dmp` files.

## Installation

Currently, JolTax-CLI can be installed from source:

```bash
git clone https://github.com/SweBiTS/JolTax-CLI.git
cd JolTax-CLI
pip install -e .
```

Ensure you have the `JolTax` backend and other core dependencies (`polars`, `psutil`, `pygments`) installed.

## Quick Start

1. **Launch the shell:**
   ```bash
   joltax
   ```
   *On your first run, a **Setup Wizard** will guide you through configuring your cache directory.*

2. **Build a taxonomy cache:**
   ```text
   joltax> build ncbi /path/to/ncbi_taxonomy/
   ```

3. **Load and use the taxonomy:**
   ```text
   joltax> use ncbi
   joltax(ncbi)> summary
   joltax(ncbi)> annotate 9606
   ```

## Command Reference

| Command | Description |
| :--- | :--- |
| `use <name>` | Switch between available binary caches in your cache directory. |
| `build <name> <dir> [names]` | Build a new optimized binary cache from NCBI `.dmp` files. |
| `remove <name>` | Permanently delete a cached taxonomy from the disk. |
| `annotate <id>...` | Pretty-print canonical ranks (Domain, Phylum, etc.) for one or more IDs. |
| `find <query>` | Fuzzy search for taxonomic names using the RapidFuzz index. |
| `lineage <id>` | Display a visual tree of the taxonomic path to the root. |
| `config` | Re-run the interactive setup wizard to change the cache directory. |
| `summary` | Overview of node counts, versions, and provenance metadata. |
| `help` | List all available commands. |
| `exit` / `quit` | Exit the interactive shell. |

## Configuration

JolTax-CLI stores its configuration in `~/.joltax-cli/config.yaml` by default. You can modify the `cache_dir` setting to change where taxonomy binaries are stored.
