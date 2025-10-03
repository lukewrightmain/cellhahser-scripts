import os
import time
import subprocess
import tempfile
import urllib.request
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Get environment variables from Cellhasher
ADB = os.environ.get("adb_path", "adb")
devices = os.environ.get("devices", "").split()

# GitHub API endpoint for Acurast processor releases
GITHUB_API_URL = "https://api.github.com/repos/Acurast/acurast-processor-update/releases/latest"

def get_latest_acurast_lite_apk():
    """
    Fetch the latest Acurast Lite APK download URL from GitHub releases
    """
    try:
        print("[*] Fetching latest Acurast Lite release from GitHub...")
        
        with urllib.request.urlopen(GITHUB_API_URL) as response:
            release_data = json.loads(response.read().decode())
        
        # Find the processor-lite APK in the assets
        for asset in release_data.get("assets", []):
            if "processor-lite" in asset["name"].lower() and asset["name"].endswith(".apk"):
                apk_url = asset["browser_download_url"]
                apk_name = asset["name"]
                print(f"[✓] Found latest APK: {apk_name}")
                print(f"[✓] Download URL: {apk_url}")
                return apk_url, apk_name
        
        raise Exception("Could not find processor-lite APK in latest release")
    
    except Exception as e:
        print(f"[✗] Error fetching release info: {e}")
        raise

def download_apk(apk_url, apk_name):
    """
    Download the APK to a temporary location
    """
    try:
        # Create temporary file for the APK
        temp_dir = tempfile.gettempdir()
        local_apk_path = os.path.join(temp_dir, apk_name)
        
        print(f"[*] Downloading {apk_name}...")
        print(f"[*] Saving to: {local_apk_path}")
        
        urllib.request.urlretrieve(apk_url, local_apk_path)
        
        # Verify the file was downloaded
        file_size = os.path.getsize(local_apk_path)
        print(f"[✓] Downloaded successfully! Size: {file_size / (1024 * 1024):.2f} MB")
        
        return local_apk_path
    
    except Exception as e:
        print(f"[✗] Error downloading APK: {e}")
        raise

def install_apk_on_device(device_id, apk_path):
    """
    Install or update Acurast Lite APK on a single device using ADB
    """
    try:
        print(f"[{device_id}] Starting Acurast Lite installation/update...")
        
        # Install the APK (adb install -r for update/replace)
        print(f"[{device_id}] Installing APK...")
        result = subprocess.run(
            f'"{ADB}" -s {device_id} install -r "{apk_path}"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 or "Success" in result.stdout:
            print(f"[{device_id}] ✓ Acurast Lite installed/updated successfully!")
            return f"[{device_id}] Success"
        else:
            error_msg = result.stderr or result.stdout
            print(f"[{device_id}] ✗ Installation failed: {error_msg}")
            return f"[{device_id}] Failed: {error_msg}"
    
    except Exception as e:
        print(f"[{device_id}] ✗ Error: {e}")
        return f"[{device_id}] Error: {e}"

def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("    Acurast Lite - Install/Update Script")
    print("=" * 60)
    
    if not devices:
        print("[✗] No devices found in environment variable 'devices'")
        print("[!] Please select devices in Cellhasher before running this script")
        return
    
    print(f"[*] Target devices: {len(devices)}")
    for idx, device in enumerate(devices, 1):
        print(f"    {idx}. {device}")
    print()
    
    try:
        # Step 1: Get latest APK download URL
        apk_url, apk_name = get_latest_acurast_lite_apk()
        
        # Step 2: Download the APK
        apk_path = download_apk(apk_url, apk_name)
        
        # Step 3: Install on all devices in parallel
        print()
        print("=" * 60)
        print(f"[*] Installing Acurast Lite on {len(devices)} device(s) in parallel...")
        print("=" * 60)
        print()
        
        max_workers = max(1, len(devices))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_device = {
                executor.submit(install_apk_on_device, device_id, apk_path): device_id 
                for device_id in devices
            }
            
            for future in as_completed(future_to_device):
                device_id = future_to_device[future]
                try:
                    result = future.result()
                    print(result)
                except Exception as exc:
                    print(f"[{device_id}] Generated an exception: {exc}")
        
        # Step 4: Cleanup - remove downloaded APK
        print()
        print("[*] Cleaning up temporary files...")
        if os.path.exists(apk_path):
            os.unlink(apk_path)
            print(f"[✓] Removed temporary APK: {apk_path}")
        
        print()
        print("=" * 60)
        print("[✓] Acurast Lite installation/update completed on all devices!")
        print("=" * 60)
    
    except Exception as e:
        print(f"[✗] Script failed: {e}")
        return

if __name__ == "__main__":
    main()