#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root"
  exit 1
fi

echo "Installing Androguard GUI..."

# Install Dependencies
echo "Installing Python dependencies..."
pip3 install androguard PyQt6 Pygments

# Install Directory
INSTALL_DIR="/opt/androguard_gui"
echo "Installing application to $INSTALL_DIR..."
# Create directory if it doesn't exist
mkdir -p "$INSTALL_DIR"
# Copy project files (excluding .git and other non-essentials if possible, but cp -r is simple)
# We use rsync to avoid copying .git if available, or just simple cp
if command -v rsync >/dev/null 2>&1; then
    rsync -av --exclude='.git' --exclude='__pycache__' . "$INSTALL_DIR"
else
    cp -r . "$INSTALL_DIR"
fi

# Create Wrapper
WRAPPER_PATH="/usr/local/bin/androguard-gui"
echo "Creating launcher at $WRAPPER_PATH..."

cat > "$WRAPPER_PATH" <<EOF
#!/bin/bash
exec python3 $INSTALL_DIR/main.py "\$@"
EOF

chmod +x "$WRAPPER_PATH"

echo "Installation complete!"
echo "Run 'androguard-gui' to start."
