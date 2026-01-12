# Androguard GUI

**Androguard GUI** is a modern, feature-rich desktop interface for the [Androguard](https://github.com/androguard/androguard) reverse engineering framework. Built with Python and PyQt6, it provides a user-friendly environment for analyzing Android APKs, decompiling bytecode, and inspecting application internals.

## 🚀 Features

*   **Static Analysis**: Deep inspection of APK files, extracting metadata, permissions, and component definitions.
*   **Integrated Decompiler**: View decompiled Java source code using the DAD decompiler, complete with syntax highlighting.
*   **Project Explorer**: Navigable tree view of the DEX structure, organized by package and class.
*   **Strings & XRefs**: Powerful search for string constants with instant cross-reference (XRef) navigation. Double-click a string to jump to its usage in the code.
*   **ADB Integration**: Connect your Android device to:
    *   List all installed packages.
    *   Filter and search for specific apps.
    *   **Pull and analyze** APKs directly from the device in one click.
*   **Dashboard**: Quick overview of:
    *   App Version (Name & Code)
    *   SDK targets (Min/Target)
    *   Permissions
    *   Activities, Services, Receivers, and Providers.
*   **Responsive UI**: Multithreaded analysis ensures the interface remains smooth even when processing large APKs.

## 📋 Prerequisites

*   **Python 3.8+**
*   **ADB** (Android Debug Bridge) - Required for device integration features.
    *   Linux: `sudo apt install adb`
    *   Windows/Mac: Install via Android Studio or Platform Tools.

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

### Analyzing a Local APK
1.  Go to **File > Open APK** (or press `Ctrl+O`).
2.  Select your `.apk` file.
3.  Wait for the analysis to complete (progress is shown in the status bar).

### Analyzing an App from a Device
1.  Ensure your Android device is connected via USB and USB Debugging is enabled.
2.  Go to **Device > List Packages**.
3.  Select your device from the dropdown.
4.  Search for the target application in the list.
5.  Select the app and click **Pull & Analyze**.
6.  The APK will be downloaded to a temporary location and automatically loaded.

### Navigating Code
*   **Project Structure (Left Panel):** Browse packages and classes. Click a class to decompile it.
*   **Strings Tab:** Search for text. Double-click a row to see which method uses that string.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License



This is free and unencumbered software released into the public domain. See [LICENSE](LICENSE) for more information.
