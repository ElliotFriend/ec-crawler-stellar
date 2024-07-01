"""
Constants
---------

This module is where the relevant constants are stored, to be accessed from any
other module that needs access to them.

To customize this package for use in other ecosystems, you "should" only have to
modify the constants here (or in the `.env` file) before you're off to the
races!
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Constants and configurations
GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN")
BASE_REPO_PATH: str | None = os.getenv("BASE_REPO_PATH")
BASE_GITHUB_URL: str = "https://github.com/"
BASE_ECOSYSTEM: str = "Stellar"

SEARCH_QUERIES: dict[str, list[dict[str, str]]] = {
    "cheesecake-labs": [
        {"filename": "package.json", "keyword": "stellar-plus"},
    ],
    "paltalabs": [
        # Javascript packages
        {"filename": "package.json", "keyword": '\\"mercury-sdk'},
    ],
    "stellar": [
        ## All of our various SDKs
        ## See: https://developers.stellar.org/docs/tools/sdks/library
        # JavaScript/Typescript
        {"filename": "package.json", "keyword": "stellar-sdk"},
        {"filename": "package.json", "keyword": "stellar-base"},
        {"filename": "package.json", "keyword": "@stellar/typescript-wallet-sdk"},
        {"filename": "package.json", "keyword": "as-soroban-sdk"},
        # Python
        {"filename": "requirements.txt", "keyword": "stellar_sdk"},
        {"filename": "pyproject.toml", "keyword": "stellar_sdk"},
        {"filename": "requirements.txt", "keyword": "stellar-sdk"},
        {"filename": "pyproject.toml", "keyword": "stellar-sdk"},
        # Rust
        {"filename": "Cargo.toml", "keyword": "soroban-sdk"},
        # Kotlin
        {"filename": "build.gradle.kts", "keyword": "org.stellar:wallet-sdk"},
        # Flutter
        {"filename": "pubspec.yaml", "keyword": "stellar_flutter_sdk"},
        {"filename": "pubspec.yaml", "keyword": "stellar_wallet_flutter_sdk"},
        # Swift
        {"filename": "Package.swift", "keyword": "stellar-ios-mac-sdk"},
        {"filename": "Cartfile", "keyword": "stellar-ios-mac-sdk"},
        {"filename": "Podfile", "keyword": "stellar-ios-mac-sdk"},
        # PHP
        {"filename": "composer.json", "keyword": "stellar-php-sdk"},
        # Elixir
        {"filename": "mix.exs", "keyword": "soroban"},
        {"filename": "mix.exs", "keyword": "stellar_sdk"},
        # Java
        {"filename": "pom.xml", "keyword": "stellar-sdk"},
        {"filename": "build.gradle", "keyword": "stellar-sdk"},
        # Go
        {"filename": "go.mod", "keyword": "stellar/go/txnbuild"},
        {"filename": "go.mod", "keyword": "stellar/go/clients/horizonclient"},
        # Ruby
        {"filename": "Gemfile", "keyword": "stellar-sdk"},
        # C#
        {"filename": "packages.config", "keyword": "stellar-dotnet-sdk"},
        {"filename": "packages.config", "keyword": "dotnet-stellar-sdk"},
        {"path": "*.nuspec", "keyword": "stellar-dotnet-sdk"},
        {"path": "*.nuspec", "keyword": "dotnet-stellar-sdk"},
        {"path": "*.csproj", "keyword": "stellar-dotnet-sdk"},
        {"path": "*.csproj", "keyword": "dotnet-stellar-sdk"},
        # Scala
        # (this has been unmaintained for a while, but is it useful to still include?)
        {"filename": "build.sbt", "keyword": "scala-stellar-sdk"},
        # Qt/C++
        # (this has been unmaintained for a while, but is it useful to still include?)
        {"path": "*.pro", "keyword": "StellarQtSDK.pri"},
    ],
}

DISCLAIMER_MESSAGE: str = """Welcome to the Stellar EC Scraper!

This script will modify the relevant ecosystem TOML file(s) **in place**. So,
it's really important that you have done three (3) things:

1. You have specified in the `.env` file, the absolute path to your local clone
   of the EC repo, and
2. Your local clone's `master` branch is up-to-date with the upstream EC repo,
   and
3. You should also check out a new branch your changes can be applied to. (This
   script won't apply any changes to your repo, but it could make it easier on
   you later if you're already on a new branch.)

If you haven't done those three (3) things, you could possibly screw up your
local clone. So, you might just double-check...

Please confirm below with '[y]es' or '[n]o'
"""