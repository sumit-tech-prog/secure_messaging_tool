import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from cryptography.fernet import Fernet, InvalidToken
import os
import pyperclip
import sys
import ctypes
import base64
import threading
import time

# Hide terminal window (Windows)
if sys.platform == "win32":
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass

class SecureMessagingTool:
    def __init__(self, key_file="encryption_key.txt"):
        self.key_file = key_file
        try:
            if not os.path.exists(self.key_file):
                self.key = Fernet.generate_key()
                with open(self.key_file, "wb") as f:
                    f.write(self.key)
                try:
                    os.chmod(self.key_file, 0o600)
                except Exception:
                    pass
                messagebox.showinfo("Info", f"New key generated! Share {self.key_file} with your friend!")
            else:
                with open(self.key_file, "rb") as f:
                    self.key = f.read()
            self.cipher_suite = Fernet(self.key)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load key: {e}")
            sys.exit(1)

    # KEEP message text flow unchanged
    def encrypt_message(self, message: str) -> str:
        encrypted_message = self.cipher_suite.encrypt(message.encode())
        return base64.b64encode(encrypted_message).decode()

    def decrypt_message(self, encrypted_message: str) -> str:
        try:
            encrypted_message = base64.b64decode(encrypted_message.encode())
            decrypted_message = self.cipher_suite.decrypt(encrypted_message)
            return decrypted_message.decode()
        except InvalidToken:
            raise ValueError("Invalid encrypted message or wrong key!")
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def encrypt_file(self, input_file_path: str, output_file_path: str):
        with open(input_file_path, "rb") as f:
            file_data = f.read()
        encrypted_data = self.cipher_suite.encrypt(file_data)
        with open(output_file_path, "wb") as f:
            f.write(encrypted_data)

    def decrypt_file(self, input_file_path: str, output_file_path: str):
        with open(input_file_path, "rb") as f:
            encrypted_data = f.read()
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        except InvalidToken:
            raise InvalidToken
        with open(output_file_path, "wb") as f:
            f.write(decrypted_data)

def show_toast(root, message: str, duration=1500):
    # simple centered toast at top of app
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    try:
        toast.attributes("-alpha", 0.95)
    except Exception:
        pass
    frame = tk.Frame(toast, bg="#111827", bd=1, relief=tk.RIDGE)
    frame.pack(fill=tk.BOTH, expand=True)
    label = tk.Label(frame, text=message, font=("Helvetica", 10, "bold"), bg="#111827", fg="#a5b4fc", padx=12, pady=8)
    label.pack()
    root.update_idletasks()
    rx = root.winfo_rootx()
    ry = root.winfo_rooty()
    rw = root.winfo_width()
    rh = root.winfo_height()
    tw = toast.winfo_reqwidth()
    # place near top center
    x = rx + (rw - tw) // 2
    y = ry + int(rh * 0.06)
    toast.geometry(f"+{x}+{y}")
    toast.after(duration, toast.destroy)

# small helper to add hover behaviour to tk.Button
def add_hover(btn, normal_bg, hover_bg):
    def on_enter(e):
        try:
            btn.config(bg=hover_bg)
        except Exception:
            pass
    def on_leave(e):
        try:
            btn.config(bg=normal_bg)
        except Exception:
            pass
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

class EncryptionWindow:
    def __init__(self, parent, secure_messaging_tool, root, title_label):
        self.parent = parent
        self.secure_messaging_tool = secure_messaging_tool
        self.root = root
        self.title_label = title_label
        self.build_ui()

    def build_ui(self):
        # Use grid for responsiveness inside paned window
        self.parent.configure(bg="#0b1220")
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        # Use a PanedWindow horizontally inside the tab for resizable panes
        paned = tk.PanedWindow(self.parent, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg="#0b1220", sashwidth=6)
        paned.grid(sticky="nsew", padx=12, pady=10)

        left = tk.Frame(paned, bg="#0b1220")
        right = tk.Frame(paned, bg="#071027")
        paned.add(left, minsize=260)
        paned.add(right, minsize=260)

        # Left side (input + buttons)
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)
        msg_label = tk.Label(left, text="Enter message:", bg="#0b1220", fg="#dbeafe", font=("Segoe UI", 11, "bold"))
        msg_label.grid(row=0, column=0, sticky="w", padx=6, pady=(6,4))

        self.message_text = tk.Text(left, height=8, bg="#081129", fg="#e6f0ff", insertbackground="#e6f0ff", wrap=tk.WORD, relief=tk.FLAT)
        self.message_text.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,8))

        btn_frame = tk.Frame(left, bg="#0b1220")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=6, pady=(0,8))
        btn_frame.grid_columnconfigure((0,1,2), weight=1)

        encrypt_btn = tk.Button(btn_frame, text="Encrypt", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), command=self.encrypt_message, bd=0, padx=12, pady=6)
        encrypt_btn.grid(row=0, column=0, sticky="w", padx=(0,8))
        add_hover(encrypt_btn, "#2563eb", "#1d4ed8")

        copy_btn = tk.Button(btn_frame, text="Copy Encrypted", bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"), command=self.copy_code, bd=0, padx=12, pady=6)
        copy_btn.grid(row=0, column=1, sticky="w", padx=(0,8))
        add_hover(copy_btn, "#10b981", "#059669")

        save_btn = tk.Button(btn_frame, text="Save .enc", bg="#ef4444", fg="white", font=("Segoe UI", 10, "bold"), command=self.save_encrypted_message, bd=0, padx=12, pady=6)
        save_btn.grid(row=0, column=2, sticky="w")
        add_hover(save_btn, "#ef4444", "#dc2626")

        # Right side (encrypted output + file ops)
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)
        enc_label = tk.Label(right, text="Encrypted output:", bg="#071027", fg="#dbeafe", font=("Segoe UI", 11, "bold"))
        enc_label.grid(row=0, column=0, sticky="w", padx=6, pady=(6,4))

        self.encrypted_text = tk.Text(right, height=14, bg="#020617", fg="#c7d2fe", insertbackground="#c7d2fe", wrap=tk.WORD, relief=tk.FLAT)
        self.encrypted_text.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,8))

        file_label = tk.Label(right, text="File operations:", bg="#071027", fg="#dbeafe", font=("Segoe UI", 11, "bold"))
        file_label.grid(row=2, column=0, sticky="w", padx=6, pady=(6,4))

        file_frame = tk.Frame(right, bg="#071027")
        file_frame.grid(row=3, column=0, sticky="ew", padx=6, pady=(0,10))
        sel_file_btn = tk.Button(file_frame, text="Select File to Encrypt", bg="#7c3aed", fg="white", font=("Segoe UI", 10, "bold"), command=self.select_file_to_encrypt, bd=0, padx=10, pady=6)
        sel_file_btn.pack(side=tk.LEFT)
        add_hover(sel_file_btn, "#7c3aed", "#6d28d9")

    def encrypt_message(self):
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Message cannot be empty!")
            return
        try:
            encrypted_message = self.secure_messaging_tool.encrypt_message(message)
            self.encrypted_text.delete("1.0", tk.END)
            self.encrypted_text.insert(tk.END, encrypted_message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to encrypt: {e}")

    def copy_code(self):
        encrypted_message = self.encrypted_text.get("1.0", tk.END).strip()
        if not encrypted_message:
            messagebox.showerror("Error", "No message to copy!")
            return
        try:
            pyperclip.copy(encrypted_message)
            show_toast(self.root, "Encrypted message copied to clipboard")
        except Exception:
            # fallback: show a small window for manual copy
            popup = tk.Toplevel(self.root)
            popup.title("Copy Encrypted")
            tk.Label(popup, text="Clipboard unavailable. Copy from box below:", padx=8, pady=8).pack()
            text = tk.Text(popup, height=6, width=60)
            text.pack(padx=8, pady=(0,8))
            text.insert(tk.END, encrypted_message)

    def save_encrypted_message(self):
        encrypted_message = self.encrypted_text.get("1.0", tk.END).strip()
        if not encrypted_message:
            messagebox.showerror("Error", "No encrypted message to save!")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".enc", filetypes=[("Encrypted Files", "*.enc")])
        if output_path:
            try:
                with open(output_path, "w") as f:
                    f.write(encrypted_message)
                show_toast(self.root, "Encrypted file saved")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

    def select_file_to_encrypt(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            output_path = filedialog.asksaveasfilename(defaultextension=".enc")
            if output_path:
                try:
                    self.secure_messaging_tool.encrypt_file(file_path, output_path)
                    show_toast(self.root, "File encrypted successfully")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to encrypt file: {e}")

class DecryptionWindow:
    def __init__(self, parent, secure_messaging_tool, root, title_label):
        self.parent = parent
        self.secure_messaging_tool = secure_messaging_tool
        self.root = root
        self.title_label = title_label
        self.build_ui()

    def build_ui(self):
        self.parent.configure(bg="#071027")
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        paned = tk.PanedWindow(self.parent, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg="#071027", sashwidth=6)
        paned.grid(sticky="nsew", padx=12, pady=10)

        left = tk.Frame(paned, bg="#071027")
        right = tk.Frame(paned, bg="#081129")
        paned.add(left, minsize=260)
        paned.add(right, minsize=260)

        # Left: encrypted input & controls
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)
        enc_label = tk.Label(left, text="Paste encrypted text:", bg="#071027", fg="#dbeafe", font=("Segoe UI", 11, "bold"))
        enc_label.grid(row=0, column=0, sticky="w", padx=6, pady=(6,4))

        self.encrypted_text = tk.Text(left, height=8, bg="#020617", fg="#c7d2fe", insertbackground="#c7d2fe", wrap=tk.WORD, relief=tk.FLAT)
        self.encrypted_text.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,8))

        btn_frame = tk.Frame(left, bg="#071027")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=6, pady=(0,8))
        decrypt_btn = tk.Button(btn_frame, text="Decrypt", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), command=self.decrypt_message, bd=0, padx=12, pady=6)
        decrypt_btn.pack(side=tk.LEFT, padx=(0,8))
        add_hover(decrypt_btn, "#2563eb", "#1d4ed8")

        load_btn = tk.Button(btn_frame, text="Load .enc", bg="#ef4444", fg="white", font=("Segoe UI", 10, "bold"), command=self.load_encrypted_message, bd=0, padx=12, pady=6)
        load_btn.pack(side=tk.LEFT)
        add_hover(load_btn, "#ef4444", "#dc2626")

        # Right: decrypted output & file ops
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)
        out_label = tk.Label(right, text="Decrypted output:", bg="#081129", fg="#dbeafe", font=("Segoe UI", 11, "bold"))
        out_label.grid(row=0, column=0, sticky="w", padx=6, pady=(6,4))

        self.decrypted_text = tk.Text(right, height=8, bg="#081129", fg="#e6f0ff", insertbackground="#e6f0ff", wrap=tk.WORD, relief=tk.FLAT)
        self.decrypted_text.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,8))

        file_frame = tk.Frame(right, bg="#081129")
        file_frame.grid(row=2, column=0, sticky="ew", padx=6, pady=(0,8))
        sel_file_btn = tk.Button(file_frame, text="Select File to Decrypt", bg="#7c3aed", fg="white", font=("Segoe UI", 10, "bold"), command=self.select_file_to_decrypt, bd=0, padx=10, pady=6)
        sel_file_btn.pack(side=tk.LEFT)
        add_hover(sel_file_btn, "#7c3aed", "#6d28d9")

    def decrypt_message(self):
        encrypted_message = self.encrypted_text.get("1.0", tk.END).strip()
        if not encrypted_message:
            messagebox.showerror("Error", "Encrypted message cannot be empty!")
            return
        try:
            decrypted_message = self.secure_messaging_tool.decrypt_message(encrypted_message)
            self.decrypted_text.delete("1.0", tk.END)
            self.decrypted_text.insert(tk.END, decrypted_message)
            show_toast(self.root, "Decryption successful")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decrypt: {e}")

    def load_encrypted_message(self):
        file_path = filedialog.askopenfilename(filetypes=[("Encrypted Files", "*.enc")])
        if not file_path:
            return
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            try:
                text = data.decode('utf-8').strip()
                self.encrypted_text.delete("1.0", tk.END)
                self.encrypted_text.insert(tk.END, text)
                show_toast(self.root, "Loaded encrypted file (text)")
            except UnicodeDecodeError:
                out_path = filedialog.asksaveasfilename(title="Save decrypted file as...", defaultextension="", filetypes=[("All files", "*.*")])
                if not out_path:
                    return
                try:
                    self.secure_messaging_tool.decrypt_file(file_path, out_path)
                    show_toast(self.root, f"File decrypted and saved to:\n{out_path}", duration=2200)
                except InvalidToken:
                    messagebox.showerror("Error", "Decryption failed: Invalid key or corrupted file (InvalidToken).")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to decrypt file: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def select_file_to_decrypt(self):
        file_path = filedialog.askopenfilename(filetypes=[("Encrypted Files", "*.enc")])
        if file_path:
            output_path = filedialog.asksaveasfilename(defaultextension="", filetypes=[("All files", "*.*")])
            if output_path:
                try:
                    self.secure_messaging_tool.decrypt_file(file_path, output_path)
                    show_toast(self.root, f"File decrypted and saved to {output_path}")
                except InvalidToken:
                    messagebox.showerror("Error", "Decryption failed: Invalid key or corrupted file (InvalidToken).")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to decrypt file: {e}")

# Animate title padding to "rise" effect on tab change
def animate_title_raise(title_label, raise_up=True, steps=4, dist=8, step_delay=30):
    # current pad may be tuple (top,bottom) or int; store in attribute
    current = getattr(title_label, "_pad_top", 14)
    target = 14 - dist if raise_up else 14
    # clamp
    target = max(6, target)
    step = (target - current) / steps
    def step_anim(i=0):
        nonlocal current
        if i >= steps:
            title_label._pad_top = target
            title_label.pack_configure(pady=(int(title_label._pad_top), 6))
            # final font weight
            if raise_up:
                title_label.config(font=("Segoe UI", 16, "bold"))
            else:
                title_label.config(font=("Segoe UI", 16, "normal"))
            return
        current += step
        title_label._pad_top = current
        title_label.pack_configure(pady=(int(current), 6))
        title_label.after(step_delay, step_anim, i+1)
    step_anim()

def show_banner():
    banner = """
 ███████╗███████╗ ██████╗██╗   ██╗██████╗ ███████╗██████╗
 ██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗
 ███████╗█████╗  ██║     ██║   ██║██████╔╝█████╗  ██║  ██║
 ╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██╔══╝  ██║  ██║
 ███████║███████╗╚██████╗╚██████╔╝██║  ██║███████╗██████╔╝
 ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝
"""
    print(banner)

if __name__ == "__main__":
    show_banner()

    root = tk.Tk()
    root.withdraw()

    secure_messaging_tool = SecureMessagingTool()

    root.title("Secure Messaging Tool - Professional Edition")
    root.geometry("1000x700")
    root.minsize(700, 480)
    root.configure(bg="#081129")
    try:
        root.attributes("-alpha", 0.98)
    except Exception:
        pass

    root.deiconify()

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Top title area (will animate on tab change)
    top_frame = tk.Frame(root, bg="#081129")
    top_frame.pack(fill="x")
    title_label = tk.Label(top_frame, text="Secure Messaging Tool", font=("Segoe UI", 16, "normal"), bg="#081129", fg="#e6f0ff")
    title_label._pad_top = 14
    title_label.pack(pady=(title_label._pad_top, 6))

    status_var = tk.StringVar(value="Ready")
    status_label = tk.Label(root, textvariable=status_var, bg="#081129", fg="#9ca3af", anchor="w")
    status_label.pack(fill=tk.X, side=tk.BOTTOM)

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both", padx=12, pady=(6,12))

    encryption_tab = tk.Frame(tab_control, bg="#0b1220")
    decryption_tab = tk.Frame(tab_control, bg="#071027")
    tab_control.add(encryption_tab, text="Encryption")
    tab_control.add(decryption_tab, text="Decryption")

    # Build windows, pass title_label for animations
    encryption_window = EncryptionWindow(encryption_tab, secure_messaging_tool, root, title_label)
    decryption_window = DecryptionWindow(decryption_tab, secure_messaging_tool, root, title_label)

    # Bind tab change to animate title and update status / visual
    def on_tab_changed(event):
        current = tab_control.index(tab_control.select())
        if current == 0:
            status_var.set("Encryption tab active")
            # rise the title a bit for emphasis
            animate_title_raise(title_label, raise_up=True)
        else:
            status_var.set("Decryption tab active")
            animate_title_raise(title_label, raise_up=False)
    tab_control.bind("<<NotebookTabChanged>>", on_tab_changed)

    # initial animation for the default tab
    root.after(300, lambda: animate_title_raise(title_label, raise_up=True))

    root.mainloop()
