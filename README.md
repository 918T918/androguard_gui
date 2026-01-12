# Androguard GUI

**Androguard GUI** is a modern, feature-rich desktop interface for the [Androguard](https://github.com/androguard/androguard) reverse engineering framework. Built with Python and PyQt6, it provides a user-friendly environment for analyzing Android APKs, decompiling bytecode, and inspecting application internals.

## 🚀 Features

*   **Static Analysis**: Deep inspection of APK files, extracting metadata, permissions, and component definitions.
*   **Integrated Decompiler**: View decompiled Java source code using the DAD decompiler, complete with syntax highlighting.
*   **AndroidManifest.xml**: Dedicated tab with syntax-highlighted XML view of the decoded manifest.
*   **Project Explorer**: Navigable tree view of the DEX structure, organized by package and class.
*   **Method XRefs (Cross-References)**: Right-click any method in the tree view to find all its callers across the entire APK.
*   **Control Flow Graphs (CFG)**: Visualize the logic of any method with an interactive graph view (requires Graphviz).
*   **Global Symbol Search**: Powerful search (Ctrl+Shift+F) to find classes and methods by name across the whole project.
*   **Navigation History**: Browser-like Back and Forward buttons to navigate between analyzed classes.
*   **Strings & XRefs**: Powerful search for string constants with instant cross-reference navigation.
*   **ADB Integration**: Connect your Android device to:
    *   List all installed packages.
    *   Filter and search for specific apps.
    *   **Pull and analyze** APKs directly from the device in one click.
*   **Dashboard**: Quick overview of app versions, SDK targets, permissions, and components.
*   **Professional Error Handling**: Global exception tracking and detailed logging for stability.

## 📋 Prerequisites

*   **Python 3.8+**
*   **ADB** (Android Debug Bridge) - Required for device integration features.
*   **Graphviz** - Required for Control Flow Graph (CFG) visualization.
    *   Linux: `sudo apt install graphviz`
    *   Windows/Mac: [Download here](https://graphviz.org/download/)

## 🛠️ Installation

### Quick Install (Linux)

You can use the included installation script to set up everything automatically:

```bash
git clone https://github.com/918T918/androguard_gui.git
cd androguard_gui
sudo ./install.sh
```

This will install dependencies and create a system-wide command: `androguard-gui`

### Manual Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/918T918/androguard_gui.git
    cd androguard_gui
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python3 main.py
    ```

## 💻 Usage

### Starting the App
Run the application from your terminal:
```bash
androguard-gui
```

### Analyzing an App from a Device
1.  Ensure your Android device is connected via USB and USB Debugging is enabled.
2.  Go to **Device > List Packages**.
3.  Select your device, search for the app, and click **Pull & Analyze**.

### Advanced Analysis
*   **XRefs:** Right-click a method in the Project Structure tree and select "Find Usages".
*   **CFG:** Right-click a method and select "View Control Flow Graph".
*   **Search:** Press `Ctrl+Shift+F` to search for any class or method name.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This is free and unencumbered software released into the public domain. See [LICENSE](LICENSE) for more information.