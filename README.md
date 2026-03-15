# Cellhasher Scripts

Official community scripts for the [Cellhasher Controller](https://github.com/lukewrightmain/CellhasherController) app.

Scripts in this repo are loaded directly into the **Cellhasher Scripts** tab inside the app.

---

## Submitting a Script

### From the App (Easiest)

1. Open **Cellhasher Controller**
2. Go to **Scripts** > **My Scripts** or **Cellhasher Scripts** tab
3. Click the **Submit** button
4. Fill in the metadata (name, description, language, warnings, your username)
5. Click **Submit to Cellhasher** — this opens a GitHub issue with your script JSON pre-filled
6. That's it! The team will review and merge it

### Manual Submission

1. Fork this repo
2. Add your script as a `.json` file in the root directory (see format below)
3. Open a Pull Request with a description of what your script does

---

## Script JSON Format

All scripts use this JSON format. The app exports scripts in this exact format when you use the Submit button.

### No-Code Script

```json
{
  "id": "my-script-name",
  "name": "My Script Name",
  "description": "What the script does",
  "category": "Utility",
  "type": "NoCode",
  "version": "1.0.0",
  "author": "YourUsername",
  "commands": [
    { "type": "shell", "command": "echo hello" },
    { "type": "wait", "duration": 2 },
    { "type": "keyevent", "keyCode": "26" },
    { "type": "shell", "command": "input tap 500 500" }
  ],
  "effects": {
    "power": { "reboot": false, "shutdown": false },
    "security": { "modifiesLockScreen": false }
  }
}
```

### Python Script

```json
{
  "id": "my-python-script",
  "name": "My Python Script",
  "description": "What the script does",
  "category": "Custom",
  "type": "Python",
  "version": "1.0.0",
  "author": "YourUsername",
  "commands": [],
  "pythonScript": "print('Hello from Cellhasher!')\n# Your Python code here\n"
}
```

### Lua Script

```json
{
  "id": "my-lua-script",
  "name": "My Lua Script",
  "description": "What the script does",
  "category": "Custom",
  "type": "Lua",
  "version": "1.0.0",
  "author": "YourUsername",
  "commands": [],
  "luaScript": "print('Hello from Cellhasher!')\n-- Your Lua code here\n"
}
```

You can also submit standalone `.py` or `.lua` files — they'll be auto-detected by the app.

---

## Fields Reference

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (lowercase, hyphens, no spaces) |
| `name` | Yes | Display name shown in the app |
| `description` | Yes | Short description of what the script does |
| `category` | Yes | One of: `Utility`, `Setup`, `Mining`, `Automation`, `Security`, `Network`, `Custom` |
| `type` | Yes | `NoCode`, `Python`, or `Lua` |
| `version` | Yes | Semver string (e.g. `1.0.0`) |
| `author` | Yes | Your GitHub username or display name |
| `commands` | Yes* | Array of commands (required for NoCode, empty array for Python/Lua) |
| `pythonScript` | No | Python source code (for Python type) |
| `luaScript` | No | Lua source code (for Lua type) |
| `effects` | No | Warnings about what the script does (see below) |

### Effects / Warnings

If your script reboots the device, shuts it down, or modifies the lock screen, declare it in the `effects` field:

```json
"effects": {
  "power": { "reboot": true, "shutdown": false },
  "security": { "modifiesLockScreen": true }
}
```

These are displayed as warning badges in the app so users know what to expect.

### Command Types (NoCode)

| Type | Parameters | Description |
|------|-----------|-------------|
| `shell` | `command` | Run a shell command via ADB |
| `wait` | `duration` (seconds) | Wait/delay |
| `keyevent` | `keyCode` | Send Android key event |
| `input_text` | `text` | Type text input |
| `touch` | `x`, `y` | Tap screen coordinates |
| `swipe` | `x`, `y`, `endX`, `endY` | Swipe gesture |
| `reboot` | — | Reboot the device |
| `poweroff` | — | Power off the device |
| `sleep` | — | Put device to sleep |

---

## Guidelines

- **Test your script** on at least one device before submitting
- **Include accurate warnings** — if it reboots, say so
- **Use clear names and descriptions** — other users need to understand what it does
- **Keep it focused** — one script should do one thing well
- **No malicious scripts** — scripts that brick devices, steal data, or cause harm will be rejected and the author banned

---

## License

Scripts submitted to this repo are shared under the [MIT License](LICENSE) unless otherwise specified by the author.
