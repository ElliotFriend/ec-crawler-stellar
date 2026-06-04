# Stellar Electric Capital Crawler

## Overview

This crawler script, designed for the Electric Capital
[Open Dev Data](https://github.com/electric-capital/open-dev-data) repository
(formerly `crypto-ecosystems`), assists in the process of updating the list of
Stellar-related projects on GitHub. It identifies new projects using specific
Stellar dependencies, compares them against the current Stellar taxonomy, and
writes any newly discovered projects to a new taxonomy **mutations file**.

## Features

- **Intelligent Filtering:** Adds only new repositories not already tracked in
  the exported Stellar taxonomy.
- **Rate Limit Handling:** Uses the `pygithub` package, which handles
  pagination, rate limiting, and authentication.
- **Sub-Ecosystem Crawling:** Recurses into the sub-ecosystems found in the
  exported taxonomy (via each repo's `branch`) and crawls them the same way.
- **Mutations Output:** Writes additions as `repadd` lines in a single dated
  mutations file under the Open Dev Data `migrations/` directory, ready to be
  validated and submitted as a PR.

## Requirements

- Python 3.x (v3.12 is probably best)
- This package was made using [uv](https://docs.astral.sh/uv/). You'll probably
  have the best results if you use it for this, too.
- A GitHub personal access token
- A local clone of [Open Dev Data](https://github.com/electric-capital/open-dev-data)
  and [`uv`](https://docs.astral.sh/uv/) installed (the Open Dev Data CLI, which
  this script shells out to for taxonomy exports, runs via `uv`).

## Setup

1. **Clone the Open Dev Data Repository:** If you haven't already, make a local
   clone of the
   [Open Dev Data repo](https://github.com/electric-capital/open-dev-data) (or
   your own fork, more likely).
2. **Create a new branch:** You're best off checking out a new branch of the
   Open Dev Data repo before you run this script. Base it off `main` (and make
   sure that's up-to-date, while you're at it), and call it whatever you like.
   The script writes a new mutations file rather than editing existing files, so
   the diff stays clean and easy to review.
3. **Environment Variables:** Set `GITHUB_TOKEN` and `BASE_REPO_PATH` (the
   absolute path to your Open Dev Data clone) in a `.env` file. (You can copy
   `.env.example` to `.env`, and edit it.)
4. **Dependencies:** Install required Python libraries with the `uv sync`
   command.

## How the taxonomy works now

Open Dev Data no longer bundles ecosystems into `*.toml` files. Instead, the
taxonomy is built from an ordered series of **migration files** that use a small
domain-specific language (DSL), e.g.:

```text
ecoadd Stellar
repadd Stellar https://github.com/stellar/stellar-core
ecocon Stellar "Aquarius (AQUA token)"
```

This crawler reads the current state by **exporting** the taxonomy to JSONL
(shelling out to `./run.sh export -e Stellar <file>` in the Open Dev Data repo),
and writes its additions as a new mutations file full of `repadd` lines.

## Usage

### GitHub Crawl

This script searches GitHub code for various Stellar-related dependencies and
proposes any newly found repositories as taxonomy additions.

Run `uv run crawl` in the root folder. The script then:

1. Initializes and loads environment variables.
2. Exports the current Stellar taxonomy to JSONL (via the Open Dev Data CLI) and
   reads the set of already-tracked repositories.
3. Recurses into every sub-ecosystem found in the export (via each repo's
   `branch`).
4. Searches GitHub for repositories using specified Stellar-related packages
   (see `SEARCH_QUERIES` in `crawler/constants.py`).
5. Compares and filters found repositories against the exported taxonomy.
6. Writes any new repositories as `repadd` lines into a single dated mutations
   file under `<BASE_REPO_PATH>/migrations/`.

After running, validate the result from the Open Dev Data repo with
`./run.sh validate`, then open a PR with the new mutations file.

### Ecosystem Repositories Count

This script can count the currently tracked repositories for the ecosystem (as
well as sub-ecosystems).

Run `uv run count_repos` in the root folder. The script then:

1. Initializes and loads environment variables.
2. Exports the current Stellar taxonomy to JSONL (via the Open Dev Data CLI).
3. Counts all repositories within the given ecosystem, logging the info.
4. Follows the same process for every sub-ecosystem found in the export (and
   their sub-ecosystems, too).

### Ecosystem Contributors Count

> This will also run the `count_repos` script as part of the process.

This script can count the recent (within the previous 30 days) contributors in
the ecosystem (as well as sub-ecosystems).

Run `uv run count_contrib` in the root folder. The script then:

1. Runs the repository count functionality as outlined above.
2. Iterates through all retrieved repositories for the parent and sub
   ecosystems.
3. For all un-archived Github repos, it searches for the previous 28-days-worth
   of commits, and tracks unique committers.
4. Filters out `[bot]` committers and logs a count of unique ecosystem-wide
   contributors.

## Output

- Logs of the process.
- A new dated mutations file under `<BASE_REPO_PATH>/migrations/` containing
  `repadd` lines for the newly discovered repositories (in the case of the
  GitHub Crawl script).

## Error Handling

- Handles GitHub API rate limits and HTTP request failures.

## Source

This script is a **heavily** customized fork of a similar Aave-related
repository by
**[@tolgayayci](https://github.com/tolgayayci/ec-crawler-aave)**.

---

Note: Comply with GitHub's API policies and rate limits when using this script.
