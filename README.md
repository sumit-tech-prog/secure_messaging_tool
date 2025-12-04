# Secure Messaging Tool

A desktop GUI tool to encrypt/decrypt text and files using `cryptography.Fernet`. Includes a dark "Matrix" background, responsive resizable UI, runtime translucency (glassy) controls, and easy save/load of `.enc` files.


## Requirements

* **Python 3.10+** recommended (works with Python 3.8+ in most cases). Check with:

  ```bash
  python --version
  # or
  python3 --version
  ```
* Python packages:

  * `cryptography`
  * `pyperclip`
* `tkinter` (standard library GUI). On some Linux distros this is a separate package (see Linux section).

---

## Installation

### Quick (pip)

```bash
# optional: use python or python3 depending on your system
pip install cryptography pyperclip
# then run
python secure_messaging_tool.py
```

### Recommended: Virtual environment

1. Create and activate a virtualenv:

   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Linux / macOS
   .\.venv\Scripts\activate     # Windows PowerShell
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Run:

   ```bash
   python secure_messaging_tool.py
   ```


If pip fails to install `cryptography` due to missing build dependencies:

```bash
sudo apt install build-essential libssl-dev libffi-dev python3-dev
```

### Windows extra steps

* Install Python from [https://python.org](https://python.org) (choose "Add Python to PATH").
* If clipboard fails, ensure `pyperclip` installed; on Windows it typically uses built-in clipboard APIs.

### macOS extra steps

* `tkinter` is usually available when you install Python from python.org. If using Homebrew Python, you may need to install `tcl-tk` and reinstall Python linking to it:

  ```bash
  brew install tcl-tk
  brew reinstall python --with-tcl-tk
  ```

---

## Running the app

From the project directory:

```bash
python secure_messaging_tool.py
```

You should see the GUI open with:

* Tabs: **Encryption**, **Decryption**
* Matrix background animation (toggle in the UI if implemented)
* A translucency slider and "Glassy style" toggle at the top

---

## Usage

### Encrypt a message

1. Switch to the **Encryption** tab.
2. Type or paste your plaintext into **Enter message**.
3. Click **Encrypt**.
4. The encrypted token (base64-wrapped Fernet token) will appear in **Encrypted output**.
5. Click **Copy Encrypted** to copy to clipboard or **Save .enc** to save to a file.

### Decrypt a message

1. Switch to the **Decryption** tab.
2. Paste the encrypted token into **Paste encrypted text** (or click **Load .enc** to open a saved encrypted text file).
3. Click **Decrypt** — the plaintext will appear in **Decrypted output**.

### Encrypt a file

1. In **Encryption** tab click **Select File to Encrypt**.
2. Choose a file and provide a `.enc` output filename when prompted.
3. The file will be encrypted with the same key and saved as binary.

### Decrypt a file

1. In **Decryption** tab click **Select File to Decrypt**.
2. Choose a `.enc` encrypted file and choose a location/filename to save the decrypted file.
3. If the file was encrypted with this tool’s key it will decrypt correctly; otherwise you will get `InvalidToken`.

### UI controls & tips

* Use the sash in the middle to resize left/right panes.
* Slider in the top-right sets window translucency (global `-alpha`); some platforms may ignore it.
* Checkbox “Glassy style” toggles a lighter color theme to approximate glass.
* Drag the window corners to resize — controls are responsive.
* Use the toast notifications for quick feedback.

---

## Configuration & files created

* `encryption_key.txt` — generated on first run in the working directory. **Share this file only with trusted recipients** (they must have the same key to decrypt messages/files).
* Encrypted files typically saved with `.enc` extension; encrypted messages saved as base64 text.

---

## Troubleshooting & common errors

**`ModuleNotFoundError: No module named 'cryptography'`**

```bash
pip install cryptography
# Or inside venv:
pip install -r requirements.txt
```

**`_tkinter.TclError: unknown color name ""`**

* This happens when a widget gets `bg=""`. The provided code avoids empty color strings, but if you modified UI ensure `bg` is a valid color string (e.g. `#071029`).

**`ImportError: No module named tkinter` or GUI doesn't open`**

* Install `python3-tk` (Linux) or ensure your Python install includes Tk:

  ```bash
  sudo apt install python3-tk
  ```

**Clipboard copy not working**

* On headless or minimal environments the clipboard may be unavailable. The app falls back to showing the encrypted text in a popup for manual copy.

**`InvalidToken` on decrypting files/messages**

* Causes:

  * Wrong key (different `encryption_key.txt`).
  * File corrupted or partially saved.
  * Trying to decrypt text data with the binary-file decryptor and vice versa.
* Confirm both sender and receiver use the same `encryption_key.txt` file (exact bytes).

**Permission issues when creating `encryption_key.txt`**

* On Unix-like systems the script sets `chmod 600` on the key file; ensure the user running the app has write permission in the folder.

---

## Packaging / Distributing

To create a standalone executable:

**PyInstaller**

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed secure_messaging_tool.py
# The exe will be in dist/
```

Notes:

* The Matrix background draws on a `Canvas`. When packaging, include any extra fonts if used (e.g., Consolas).
* Test the packaged app on target platform (Windows/macOS/Linux).

---

## Security notes

* **Key management**: The `encryption_key.txt` is the master key. Keep it secure. If the file is leaked, all messages and files encrypted with it can be decrypted.
* **Sharing key**: Use a secure channel (in-person, secure file transfer) to exchange the `encryption_key.txt`.
* **Do not base64-encode unencrypted secrets** as a security measure — the tool encrypts with Fernet (AES128+HMAC) and then base64-encodes the ciphertext for easy copy/paste.
* This tool is intended for educational and legitimate privacy uses. Follow local laws and policies.

---

## Development / Contributing

* Fork the repo and open pull requests for improvements (UI, platform-specific translucency, packaging scripts).
* If you add platform-native blur/ acrylic features, please keep them behind OS checks and document additional required packages.

---

## Changelog (summary)

* **v1.0** — Desktop GUI, encrypt/decrypt messages & files, generated `encryption_key.txt`.
* **v1.1** — Responsive panes, drag-sash resizing, improved error handling.
* **v1.2** — Matrix-style background animation, translucency slider, glassy theme toggle.
* (Add your own versions as you modify.)

---

## License

Choose a license that fits your needs. Example:

```
MIT License
See LICENSE file for details.
```

---

## requirements.txt

Create a `requirements.txt` with:

```
cryptography>=41.0.0
pyperclip>=1.8.0
```

(You can pin exact versions used in your development environment.)

---

## Example quick commands

Clone, setup and run (Linux / macOS):

```bash
git clone https://github.com/yourusername/secure-messaging-tool.git
cd secure-messaging-tool
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python secure_messaging_tool.py
```

Windows (PowerShell):

```powershell
git clone https://github.com/yourusername/secure-messaging-tool.git
cd secure-messaging-tool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python secure_messaging_tool.py
```

---

If you want, I can:

* Generate a `LICENSE` and `requirements.txt` file for your repo.
* Add an automated `install.sh` / `install.ps1` script to make setup a single command.
* Create a ready-to-add GitHub workflow for packaging with PyInstaller.

Tell me which of those you'd like next.
