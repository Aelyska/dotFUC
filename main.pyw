# Meow
import sys
import hashlib
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
def generate_password_hash(password):
    """Generate SHA-256 hash from the password."""
    return hashlib.sha256(password.encode()).digest()
def encrypt_data(data, password):
    """Encrypt data using AES-256."""
    iv = os.urandom(16)
    cipher = AES.new(password, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(pad(data, AES.block_size))
def decrypt_data(data, password):
    """Decrypt data using AES-256."""
    iv = data[:16]
    cipher = AES.new(password, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(data[16:]), AES.block_size)
def open_fuc_file(file_path=None):
    """Function to open and decrypt .FUC file"""
    if not file_path:
        file_path = filedialog.askopenfilename(filetypes=[("FUC Files", "*.fuc")])
        if not file_path:
            return
    password = simpledialog.askstring("Password", "Enter password to open the image:", show='*')
    if not password:
        return
    with open(file_path, 'rb') as fuc_file:
        stored_password_hash = fuc_file.read(32)
        if generate_password_hash(password) != stored_password_hash:
            messagebox.showerror("Error", "Incorrect password!")
            return
        width = int.from_bytes(fuc_file.read(4), 'big')
        height = int.from_bytes(fuc_file.read(4), 'big')
        encrypted_data = fuc_file.read()
        decrypted_data = decrypt_data(encrypted_data, stored_password_hash)
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        index = 0
        for y in range(height):
            for x in range(width):
                pixels[x, y] = (decrypted_data[index], decrypted_data[index+1], decrypted_data[index+2])
                index += 3
        image.show()
def convert_image_to_fuc():
    """Convert image to encrypted .FUC file"""
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if not file_path:
        return
    password = simpledialog.askstring("Password", "Enter a password to encrypt:", show='*')
    if not password:
        return
    password_hash = generate_password_hash(password)
    image = Image.open(file_path).convert("RGB")
    width, height = image.size
    save_path = filedialog.asksaveasfilename(defaultextension=".fuc", filetypes=[("FUC Files", "*.fuc")])
    if not save_path:
        return
    image_data = bytearray()
    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            image_data.extend([r, g, b])
    encrypted_data = encrypt_data(image_data, password_hash)
    with open(save_path, 'wb') as fuc_file:
        fuc_file.write(password_hash)
        fuc_file.write(width.to_bytes(4, 'big'))
        fuc_file.write(height.to_bytes(4, 'big'))
        fuc_file.write(encrypted_data)
    messagebox.showinfo("Success", f"Image saved as {save_path}")
def convert_fuc_to_image():
    """Convert .FUC file to image"""
    file_path = filedialog.askopenfilename(filetypes=[("FUC Files", "*.fuc")])
    if not file_path:
        return
    password = simpledialog.askstring("Password", "Enter password to convert the image:", show='*')
    if not password:
        return
    with open(file_path, 'rb') as fuc_file:
        stored_password_hash = fuc_file.read(32)
        if generate_password_hash(password) != stored_password_hash:
            messagebox.showerror("Error", "Incorrect password!")
            return
        width = int.from_bytes(fuc_file.read(4), 'big')
        height = int.from_bytes(fuc_file.read(4), 'big')
        encrypted_data = fuc_file.read()
        decrypted_data = decrypt_data(encrypted_data, stored_password_hash)
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        index = 0
        for y in range(height):
            for x in range(width):
                pixels[x, y] = (decrypted_data[index], decrypted_data[index+1], decrypted_data[index+2])
                index += 3
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("BMP Files", "*.bmp")])
        if save_path:
            image.save(save_path)
            messagebox.showinfo("Success", f"Image saved as {save_path}")
if len(sys.argv) > 1:
    file_path = sys.argv[1]
    open_fuc_file(file_path)
else:
    root = tk.Tk()
    root.title("FUC Image Converter")
    root.geometry("400x250")
    root.iconbitmap("icon.ico")
    root.configure(bg="white")
    tk.Label(root, text="FUC Image Converter", font=("Arial", 16), bg="white").pack(pady=10)
    tk.Button(root, text="Convert Image to .FUC", command=convert_image_to_fuc, font=("Arial", 12), bg="#f0f0f0").pack(pady=10)
    tk.Button(root, text="Convert FUC to Image", command=convert_fuc_to_image, font=("Arial", 12), bg="#f0f0f0").pack(pady=10)
    tk.Button(root, text="Open .FUC File", command=open_fuc_file, font=("Arial", 12), bg="#f0f0f0").pack(pady=10)
    root.mainloop()
