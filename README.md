# Stellar Electric Capital Crawler

## Overview

This crawler script, designed for the Electric Capital Crypto Ecosystems
repository, assists in the process of updating the list of Stellar-related
projects on GitHub. It identifies new projects using specific Stellar
dependencies, compares them with the existing list in `stellar.toml`, and
updates the local copy of `stellar.toml` with newly discovered projects.

## Features

- **Intelligent Filtering:** Adds only new projects not already listed in
  `stellar.toml`.
- **Rate Limit Handling:** Uses the `pygithub` package, which handles
  pagination, rate limiting, and authentication.
- **Github Organization Crawling:** Crawls for all public repositories in
  defined Github organizations, adding new repositories to the toml file.
- **Sub-Ecosystem Crawling:** Recurses into the relevant `*.toml` files for
  defined sub-ecosystems, and does the same crawl for them.

## Requirements

- Python 3.x (v3.12 is probably best)
- This package was made using [Poetry](https://python-poetry.org/). You'll
  probably have the best results if you use it for this, too.
- A GitHub personal access token

## Setup

1. **Clone the EC Repository:** If you haven't already, you should make a local
   clone of the [EC repo](https://github.com/electric-capital/crypto-ecosystems)
   (or your own fork of it, more likely).
2. **Create a new EC Branch:** You're probably best off checking out a new
   branch of the EC repo before you run this script. Base it off `master` (and
   make sure that's up-to-date, while you're at it), and call it whatever you
   like.
3. **Environment Variables:** Set `GITHUB_TOKEN` and `BASE_REPO_PATH` in
   a `.env` file. (You can copy `.env.example` to `.env`, and edit it)
4. **Dependencies:** Install required Python libraries with `poetry install`
   command.

## Usage

### GitHub Crawl

This script can search github for newly added Organization repositories, as well
as gather search results for various relevant dependencies.

Run `poetry run crawl` in the root folder. The script then:

1. Initializes and loads environment variables.
2. Reads the local `stellar.toml` file.
3. Searches defined GitHub organizations, retrieving all public repositories.
4. Searches GitHub for repositories with specified Stellar-related packages.
5. Compares and filters found repositories against `stellar.toml`.
6. Sorts all repositories, so you can more easily pass `make validate` in the EC
   repo.
7. Updates the `stellar.toml` file **in-place**, overwriting current contents.
8. Follows the same process for all defined `sub_ecosystems` in the
   `stellar.toml` file (and `sub_sub_etc_ecosystems`, too).

### Ecosystem Repositories Count

This script can count the currently tracked repositories for the ecosystem (as
well as sub-ecosystems).

Run `poetry run count_repos` in the root folder. The script then:

1. Initializes and loads environment variables.
2. Reads the local `stellar.toml` file.
3. Searches defined GitHub organizations, retrieving all public repositories.
4. Counts all repositories within the given ecosystem, logging the info.
5. Follows the same process for all defined `sub_ecosystems` in the
   `stellar.toml` file (and `sub_sub_etc_ecosystems`, too).

### Ecosystem Contributors Count

> This will also run the repositories count script as part of the process.

This script can count the recent (within the previous 28 days) contributors in
the ecosystem (as well as sub-ecosystems).

Run `poetry run count_contrib` in the root folder. The script then:

1. Runs the repository count functionality as outlined above.
2. Iterates through all retrieved repositories for the parent and sub
   ecosystems.
3. For all un-archived Github repos, it searches for the previous 28-days-worth
   of commits, and tracks unique committers.
4. Filters out `[bot]` committers and logs a count of unique ecosystem-wide
   contributors.

## Output

- Logs of the process.
- Updates any relevant `*.toml` file **in-place** (in the case of the Github
  Crawl script).

## Error Handling

- Handles GitHub API rate limits and HTTP request failures.

## Source

This script is a **heavily** customized fork of a similar Aave-related
repository by
**[@tolgayayci](https://github.com/tolgayayci/ec-crawler-aave)**.

---

Note: Comply with GitHub's API policies and rate limits when using this script.
