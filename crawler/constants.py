"""
Constants
---------

This module is where the relevant constants are stored, to be accessed from any
other module that needs access to them.
"""

import os

GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")
BASE_REPO_PATH: str = os.getenv("BASE_REPO_PATH")

SEARCH_QUERIES: dict[str, list[dict[str, str]]] = {
    "cheesecake-labs": [
        {"filename": "package.json", "keyword": "stellar-plus"},
    ],
    "paltalabs": [
        # Javascript packages
        {"filename": "package.json", "keyword": '\\"mercury-sdk'},
    ],
    "soneso": [],
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
