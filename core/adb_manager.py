import subprocess
import shutil
import os

class ADBManager:
    def __init__(self, adb_path="adb"):
        # If adb is in path, "adb" works. Otherwise user might need to specify.
        # Since we found it in a specific path, we might want to use that or rely on PATH.
        # The user's env seems to have it in PATH based on 'which adb'.
        self.adb_path = adb_path

    def get_devices(self):
        """Returns a list of device serials."""
        try:
            output = subprocess.check_output([self.adb_path, "devices"]).decode("utf-8")
            devices = []
            for line in output.splitlines()[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == "device":
                        devices.append(parts[0])
            return devices
        except Exception as e:
            raise Exception(f"Failed to list devices: {e}")

    def get_packages(self, serial):
        """Returns a list of (package_name, path) tuples."""
        try:
            cmd = [self.adb_path, "-s", serial, "shell", "pm", "list", "packages", "-f"]
            output = subprocess.check_output(cmd).decode("utf-8")
            packages = []
            for line in output.splitlines():
                if line.startswith("package:"):
                    # format: package:/data/app/com.example-1/base.apk=com.example
                    line = line[8:]
                    if "=" in line:
                        path, name = line.rsplit("=", 1)
                        packages.append((name, path))
            return sorted(packages, key=lambda x: x[0])
        except Exception as e:
            raise Exception(f"Failed to list packages: {e}")

    def pull_apk(self, serial, remote_path, local_path):
        """Pulls the APK from the device to local_path."""
        try:
            subprocess.check_call([self.adb_path, "-s", serial, "pull", remote_path, local_path])
        except subprocess.CalledProcessError as e:
             raise Exception(f"Failed to pull APK: {e}")
