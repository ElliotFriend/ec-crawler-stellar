# Electric Capital Crypto Ecosystems Crawler

## Overview

This crawler script, designed for the Electric Capital Crypto Ecosystems repository, automates the process of updating the list of Aave-related projects on GitHub. It identifies new projects using specific Aave dependencies, compares them with the existing list in aave.toml, and creates a pull request in the Electric Capital repository with new projects list of Aave.

## Features

- **Automated GitHub Crawling:** Searches for specific Aave-related keywords in package.json, package-lock.json, yarn.lock, and .sol files.
- **Intelligent Filtering:** Adds only new projects not already listed in aave.toml.
- **Automated Pull Requests:** Creates a pull request with updates on a forked Electric Capital repository.
- **Rate Limit Handling:** Manages GitHub API rate limits.

## Requirements

- Python 3.x
- requirements.txt
- A GitHub personal access token

## Setup

1. **Environment Variables:** Set ```GITHUB_TOKEN``` and ```GITHUB_USERNAME``` in a .env file. (You can copy .env.example to .env, and edit it)
2. **Dependencies:** Install required Python libraries with ```pip install -r requirements.txt``` command.

## Usage

Run ```python3 main.py``` on the root folder. The script then,

1. Initializes and loads environment variables.
2. Searches GitHub for repositories with specified Aave-related criteria.
3. Compares and filters found repositories against aave.toml.
4. Synchronizes the forked repository with the upstream repository.
5. Creates a pull request with new entries in the forked repository.

## Output

- Logs of the process.
- A link to pull request in the forked repository with aave.toml updates.

## Error Handling

- Handles GitHub API rate limits and HTTP request failures.

## Contribution

Contribute by forking the repository, making changes, and submitting a pull request.

---

Note: Comply with GitHub's API policies and rate limits when using this script.
