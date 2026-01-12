# Androguard GUI

**Androguard GUI** is a professional, high-performance desktop interface for the [Androguard](https://github.com/androguard/androguard) reverse engineering framework. Built with Python and PyQt6, it provides a comprehensive suite for analyzing Android APKs, decompiling bytecode, and security auditing.

## 🚀 Key Features

### 🔍 Analysis & Reverse Engineering
*   **Integrated Decompiler**: View decompiled Java source code (DAD) with syntax highlighting.
*   **Smali Bytecode Viewer**: Access raw Dalvik instructions when decompilation isn't enough.
*   **Frida Hook Generator**: Right-click any method to instantly generate and copy a Frida hooking snippet.
*   **Full-Text Code Search**: Scan the entire decompiled codebase for keywords, API calls, or logic.
*   **Bulk Export to Java**: Convert the entire APK structure into a Java project with one click.
*   **Method XRefs & CFG**: Find callers and visualize logic flow with Control Flow Graphs.

### 🛡️ Security & Auditing
*   **Security Hotspot Scanner**: Automatically scan for sensitive APIs (Crypto, Network, Reflection, WebView, SMS).
*   **Certificate & Signature Viewer**: Inspect app signatures, fingerprints, and developer details.
*   **AndroidManifest.xml**: View decoded, syntax-highlighted manifest with entry point analysis.
*   **Resources Decoder**: Inspect and decode `resources.arsc` XML data.

### 📦 APK Internals
*   **Files & Hex Viewer**: Browse all files inside the APK and inspect them in a built-in Hex Viewer.
*   **Project Explorer**: Hierarchical view of DEX structures, packages, and classes.

### 📱 Workflow & Aesthetics
*   **Professional Dark Mode**: High-contrast dark interface for long analysis sessions.
*   **ADB Integration**: List, search, and pull APKs directly from devices.
*   **Navigation History**: Browser-style navigation through analyzed symbols.
*   **Recent Files**: Quick access to your latest analysis projects.

## 📋 Prerequisites

*   **Python 3.8+**
*   **ADB** (Android Debug Bridge) - For device integration.
*   **Graphviz** - For CFG visualization.

## 🛠️ Installation

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

### Power User Tips
*   **Right-Click**: Use the context menu in the Project tree for XRefs, CFGs, Smali, and Frida hooks.
*   **Global Search**: `Ctrl+Shift+F` for symbols or full-text code scanning.
*   **Aesthetics**: Use the "Toggle Dark Mode" button in the toolbar for a pro look.

## 📄 License

This is free and unencumbered software released into the public domain. See [LICENSE](LICENSE) for more information.