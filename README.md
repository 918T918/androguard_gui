# Androguard GUI

An advanced desktop GUI for Androguard, built with Python and PyQt6.

## Features

- **APK Analysis**: deep analysis of APK files using Androguard.
- **Project Structure**: View classes and resources in a tree view.
- **Decompiler**: View decompiled Java code (DAD) with syntax highlighting.
- **Strings View**: Search and filter strings found in the APK.
- **XRef Navigation**: Double-click a string to jump to the method where it is used.
- **Dashboard**: Quick overview of permissions, activities, services, etc.

## Requirements

- Python 3.8+
- androguard
- PyQt6
- Pygments

## Installation

```bash
pip install androguard PyQt6 Pygments
```

## Usage

Run the application:

```bash
python3 androguard_gui/main.py
```

1. Click **File > Open APK**.
2. Wait for analysis to complete (status bar will indicate progress).
3. Browse the **Project Structure** on the left.
4. Click classes to view decompiled code.
5. Check the **Strings** tab to search for text and find usages.
