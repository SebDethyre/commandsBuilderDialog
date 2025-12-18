# 🖥️ Command Finder GUI / Interface de Recherche de Commandes
**Languages:**  [🇬🇧 EN](#-english) / [🇫🇷 FR](#-français)
  
---

## 🇬🇧 English
## Overview

**Command Finder GUI** is primarily an **ergonomic learning tool for Linux commands**.
It allows you to **search for and explore all commands stored on your disk** (as well as their options) via a smart input powered by **Chosen**. Commands are stored in a JSON file called `commands.json`.

With an intuitive dropdown, you can **discover commands, understand their usage, and practice executing them**, making it a practical companion for learning Linux efficiently.

## Installation

### 1. Create a Python virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install --upgrade pip PyQt5
```

### 3. Install xterm (required for command execution display)
```bash
sudo apt install xterm
```
## Usage

### 1. Generate or update your commands JSON ⚙️
```bash
python commands_generator.py
```

This populates `commands.json` with all available commands on your disk.

### 2. Launch the GUI
```bash
python command_finder_gui.py
```

### 3. Search, Learn & Execute 🚀
Type in the input box, select a command from the dropdown, and execute it in a terminal window.
This approach allows you to **practice commands in a safe and guided environment** while learning their syntax and effects.

## Features

* Ergonomic tool for **learning** Linux commands 📚
* Smart search with **Chosen** input
* JSON-based commands database
* Easy execution in **xterm**
* Simple update via `commands_generator.py`
  
---

<br>

---

## 🇫🇷 Français
## Présentation

Command Finder GUI est **avant tout un outil ergonomique pour apprendre les commandes Linux**.
Il permet de **rechercher et explorer toutes les commandes présentes sur votre disque** (ainsi que leurs options) grâce à un input intelligent de type **Chosen**. Les commandes sont stockées dans un fichier JSON appelé `commands.json`.

Grâce à un menu déroulant intuitif, vous pouvez **découvrir les commandes, comprendre leur usage et les exécuter en pratique**, faisant de cet outil un compagnon idéal pour apprendre Linux efficacement.

## Installation

### 1. Créer un environnement virtuel Python (recommandé)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Installer les dépendances
```bash
pip install --upgrade PyQt5
```

### 3. Installer xterm (nécessaire pour l’exécution des commandes)
```bash
sudo apt install xterm
```
## Utilisation

### 1. Générer ou mettre à jour votre JSON de commandes ⚙️
```bash
python commands_generator.py
```

Ce script remplira `commands.json` avec toutes les commandes disponibles sur votre disque.

### 2. Lancer l’interface graphique
```bash
python command_finder_gui.py
```

### 3. Rechercher, Apprendre & Exécuter 🚀
Tapez dans la barre de recherche, sélectionnez une commande et lancez-la dans un terminal xterm.
Cette approche permet de **pratiquer les commandes dans un environnement sûr et guidé**, tout en apprenant leur syntaxe et leurs effets.

## Fonctionnalités

* Outil ergonomique pour apprendre les commandes Linux 📚
* Recherche intelligente avec Chosen input
* Base de commandes JSON
* Exécution facile dans xterm
* Mise à jour simple via commands_generator.py
