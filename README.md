# Androguard GUI

**Androguard GUI** is a modern, feature-rich desktop interface for the [Androguard](https://github.com/androguard/androguard) reverse engineering framework. Built with Python and PyQt6, it provides a user-friendly environment for analyzing Android APKs, decompiling bytecode, and inspecting application internals.

## 🚀 Features

### 🔍 Analysis & Reverse Engineering
*   **Integrated Decompiler**: View decompiled Java source code using the DAD decompiler, complete with syntax highlighting.
*   **Full-Text Code Search**: Search for any keyword (API calls, variable names) inside the decompiled Java source across the entire APK.
*   **Bulk Export to Java**: Decompile and export the entire APK structure to a local directory in one click.
*   **Method XRefs (Cross-References)**: Right-click any method in the tree view to find all its callers.
*   **Control Flow Graphs (CFG)**: Visualize method logic with interactive graphs (requires Graphviz).
*   **Strings & XRefs**: Powerful search for string constants with instant usage navigation.

### 📦 APK Internals
*   **AndroidManifest.xml**: Dedicated tab with syntax-highlighted XML view of the decoded manifest.
*   **Files & Hex Viewer**: Browse all files inside the APK (DEX, resources, assets) and inspect them in a built-in Hex Viewer.
*   **Certificate Viewer**: Inspect app signatures, fingerprints (SHA1/SHA256), and developer certificate details.
*   **Project Explorer**: Navigable tree view of the DEX structure organized by package and class.

### 📱 Device & Workflow
*   **ADB Integration**: List packages, search, and **pull APKs directly from connected devices** for instant analysis.
*   **Recent Files**: Quick access to previously analyzed APKs from the File menu.
*   **Navigation History**: Browser-like Back and Forward buttons for seamless code navigation.
*   **Professional Error Handling**: Global exception tracking and detailed logging (`androguard_gui.log`) for maximum stability.

## 📋 Prerequisites

*   **Python 3.8+**
*   **ADB** (Android Debug Bridge) - For device integration features.
*   **Graphviz** - For Control Flow Graph (CFG) visualization.
    *   Linux: `sudo apt install graphviz`
    *   Windows/Mac: [Download here](https://graphviz.org/download/)

## 🛠️ Installation

### Quick Install (Linux)

```bash
git clone https://github.com/918T918/androguard_gui.git
cd androguard_gui
sudo ./install.sh
```

## 💻 Usage

### Starting the App
```bash
androguard-gui
```

### Advanced Features
*   **Search**: Press `Ctrl+Shift+F` to search for symbols or perform a **Full-Text** scan of the entire codebase.
*   **Export**: Use **File > Export to Java...** to convert the entire APK into a Java project.
*   **Hex View**: Go to the **Files** tab and double-click any file to see its raw hex dump.

## 📄 License

This is free and unencumbered software released into the public domain. See [LICENSE](LICENSE) for more information.
