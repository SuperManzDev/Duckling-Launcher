<p align="center">
  <img src="docs/duckling.png" width="96" height="96" alt="Duckling Launcher Logo"><br>
  <b>Duckling Launcher</b>
</p>

<p align="center">
  A cheerful, lightweight, blazing-fast Minecraft launcher written in Rust.<br>
  Supports all game releases, mod loaders, skins, capes, and peer-to-peer play in a single native binary.
</p>

<p align="center">
  <a href="https://github.com/SuperManzDev/Duckling-Launcher/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/SuperManzDev/Duckling-Launcher?style=flat-square&color=f59e0b"></a>
  <a href="https://github.com/SuperManzDev/Duckling-Launcher/actions/workflows/build-windows.yml"><img alt="Windows Build" src="https://img.shields.io/github/actions/workflow/status/SuperManzDev/Duckling-Launcher/build-windows.yml?branch=main&style=flat-square&label=windows%20build"></a>
  <a href="LICENSE"><img alt="License: GPL-3.0" src="https://img.shields.io/badge/license-GPL--3.0-fbbf24?style=flat-square"></a>
  <img alt="Windows, macOS and Linux" src="https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux-d97706?style=flat-square">
</p>

<p align="center">
  <a href="https://github.com/SuperManzDev/Duckling-Launcher/releases/latest"><b>Download</b></a> |
  <a href="docs/cli.md">Command Line Guide</a> |
  <a href="docs/building.md">Build Instructions</a>
</p>

Duckling Launcher is an open-source Minecraft launcher focused on speed, minimal memory usage, and direct native execution using Rust and egui. It is a fork of [arctic-launcher](https://github.com/brksfrb/arctic-launcher).

## Features

- Native performance: Built in pure Rust with egui and OpenGL, avoiding Electron or browser runtimes. Memory consumption remains low during gameplay.
- Version and runtime isolation: Downloads official Minecraft game manifests and isolated Java runtimes automatically.
- Account support: Sign in with Microsoft accounts or use local offline profiles for singleplayer and offline servers.
- Mod management: Create instances for Fabric, Quilt, NeoForge, and Forge. Search and install mods and modpacks directly from Modrinth.
- Mod conflict detection: Scans instances before launching to detect duplicates, missing dependencies, or incompatible mod versions.
- Peer-to-peer multiplayer: Share singleplayer worlds over direct encrypted connections or relays without port forwarding or dedicated servers.
- Cosmetics and skins: Apply skins and capes across both Microsoft and offline accounts with a 3D model preview.
- Proximity voice chat: Built-in spatial audio mixing and Opus voice codec support.
- CLI companion: Full headless CLI (`duckling`) with JSON output support for terminal workflows and automation.

## Installation

### Windows

1. Download `duckling-launcher-windows-x64.exe` from the [latest release](https://github.com/SuperManzDev/Duckling-Launcher/releases/latest).
2. Run the executable. No installer is required.

### macOS

1. Download `duckling-launcher-macos.zip` from the [latest release](https://github.com/SuperManzDev/Duckling-Launcher/releases/latest) and unpack it.
2. Move `Duckling Launcher.app` to your Applications directory. Universal builds support both Apple Silicon and Intel hardware.

### Linux

1. Download `duckling-launcher-linux-x64` from the [latest release](https://github.com/SuperManzDev/Duckling-Launcher/releases/latest).
2. Make the file executable and run:

```sh
chmod +x duckling-launcher-linux-x64
./duckling-launcher-linux-x64
```

Flatpak bundles are also available under `packaging/flatpak`.

## Command Line Interface

The launcher includes a headless command line tool (`duckling`):

```sh
# Launch latest release on the active profile
duckling launch

# Launch specific version with dedicated memory
duckling launch 1.20.1 --account Player --memory 6G

# Create a new Fabric instance
duckling instances create "Fabric" --version 1.21.4 --loader fabric

# Install mods from Modrinth
duckling mods install sodium --instance "Fabric"

# Scriptable JSON output
duckling instances list --json
```

Detailed CLI documentation is available in [docs/cli.md](docs/cli.md).

## Building From Source

Prerequisites:
- Rust 1.85+ (or latest stable)
- On Linux: `libasound2-dev` (ALSA for proximity audio)

```sh
git clone https://github.com/SuperManzDev/Duckling-Launcher.git
cd Duckling-Launcher

# Build the desktop application
cargo build --release -p duckling-app

# Build the CLI tool
cargo build --release -p duckling-cli
```

Binaries will be placed in `target/release/duckling-launcher` and `target/release/duckling`.

## Data Locations

- Windows: `%LOCALAPPDATA%\DucklingLauncher`
- macOS: `~/Library/Application Support/DucklingLauncher`
- Linux: `~/.local/share/DucklingLauncher`

The data directory location can be overridden at runtime using the `DUCKLING_DATA_DIR` environment variable.

## License

This project is licensed under the [GNU General Public License v3.0 or later](LICENSE).

Minecraft is a trademark of Mojang Synergies AB. Duckling Launcher is not affiliated with or endorsed by Mojang Studios or Microsoft.
