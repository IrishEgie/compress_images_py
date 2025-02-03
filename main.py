import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor


class ImageCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Compressor")
        self.root.geometry("500x300")

        # Input Directory
        self.input_dir_label = tk.Label(root, text="Input Directory:")
        self.input_dir_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_dir_entry = tk.Entry(root, width=40)
        self.input_dir_entry.grid(row=0, column=1, padx=10, pady=10)
        self.input_dir_button = tk.Button(root, text="Browse", command=self.browse_input_dir)
        self.input_dir_button.grid(row=0, column=2, padx=10, pady=10)

        # Output Directory
        self.output_dir_label = tk.Label(root, text="Output Directory:")
        self.output_dir_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.output_dir_entry = tk.Entry(root, width=40)
        self.output_dir_entry.grid(row=1, column=1, padx=10, pady=10)
        self.output_dir_button = tk.Button(root, text="Browse", command=self.browse_output_dir)
        self.output_dir_button.grid(row=1, column=2, padx=10, pady=10)

        # Progress Bar
        self.progress_label = tk.Label(root, text="Progress:")
        self.progress_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=2, column=1, columnspan=2, padx=10, pady=10)

        # Start Button
        self.start_button = tk.Button(root, text="Start Compression", command=self.start_compression)
        self.start_button.grid(row=3, column=1, padx=10, pady=20)

        # Status Label
        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.grid(row=4, column=1, padx=10, pady=10)

    def browse_input_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir_entry.delete(0, tk.END)
            self.input_dir_entry.insert(0, directory)

    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)

    def compress_image(self, input_path, output_path, max_size_kb=53*1024, min_quality=30):
        """Compress and resize the image to target size while maintaining acceptable quality."""
        img = Image.open(input_path)
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        width, height = img.size
        new_size = (int(width * 0.25), int(height * 0.25))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

        quality = 75
        min_quality = max(min_quality, 30)

        while quality >= min_quality:
            buffer = BytesIO()
            img.save(buffer, 'JPEG', quality=quality)
            buffer.seek(0)

            size_kb = len(buffer.getvalue()) / 1024
            if size_kb <= max_size_kb:
                with open(output_path, 'wb') as f:
                    f.write(buffer.getvalue())
                break
            quality -= 5

    def process_image(self, input_path, output_path, max_size_kb=53*1024, min_quality=30):
        """Helper function to process each image."""
        try:
            self.compress_image(input_path, output_path, max_size_kb, min_quality)
            return (input_path, output_path, "Success")
        except Exception as e:
            return (input_path, None, f"Error: {str(e)}")

    def start_compression(self):
        input_dir = Path(self.input_dir_entry.get().strip())
        output_dir = Path(self.output_dir_entry.get().strip())

        if not input_dir.exists():
            messagebox.showerror("Error", f"Input directory '{input_dir}' does not exist!")
            return

        output_dir.mkdir(parents=True, exist_ok=True)

        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        input_files = [
            file for file in input_dir.iterdir()
            if file.is_file() and file.suffix.lower() in supported_formats
        ]

        if not input_files:
            messagebox.showinfo("Info", "No supported image files found in the input directory.")
            return

        self.progress_bar["maximum"] = len(input_files)
        self.progress_bar["value"] = 0
        self.status_label.config(text="Processing...")

        processed_count = 0
        skipped_count = 0

        def update_progress(future):
            nonlocal processed_count, skipped_count
            input_path, output_path, status = future.result()

            if output_path:
                processed_count += 1
            else:
                skipped_count += 1

            self.progress_bar["value"] += 1
            self.root.update_idletasks()

            if self.progress_bar["value"] == len(input_files):
                self.status_label.config(text="Compression Complete!")
                messagebox.showinfo("Info", f"Successfully processed: {processed_count} images\nSkipped/Failed: {skipped_count} files")

        with ThreadPoolExecutor() as executor:
            for input_path in input_files:
                output_filename = input_path.stem + '.jpg'
                output_path = output_dir / output_filename
                future = executor.submit(self.process_image, input_path, output_path)
                future.add_done_callback(update_progress)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCompressorApp(root)
    root.mainloop()