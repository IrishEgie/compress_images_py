import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed


class ImageCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Compressor")
        self.root.geometry("600x400")  # Increased height
        self.root.minsize(600, 400)    # Set minimum window size
        
        # Try to set Windows 10 dark title bar if running on Windows
        try:
            from ctypes import windll
            windll.dwmapi.DwmSetWindowAttribute(
                windll.user32.GetParent(root.winfo_id()), 
                20,  # DWMWA_USE_IMMERSIVE_DARK_MODE
                byref(c_int(2)), 
                sizeof(c_int)
            )
        except:
            pass  # Silently fail if not on Windows or if it doesn't work

        # Center the window on the screen
        self.center_window()

        # Notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Configure grid weights to make the layout more responsive
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Main Tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main")
        
        # Configure main tab grid
        self.main_tab.grid_columnconfigure(1, weight=1)

        # Input Directory
        self.input_dir_label = tk.Label(self.main_tab, text="Input Directory:")
        self.input_dir_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_dir_entry = tk.Entry(self.main_tab)
        self.input_dir_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.input_dir_button = tk.Button(self.main_tab, text="Browse", command=self.browse_input_dir)
        self.input_dir_button.grid(row=0, column=2, padx=10, pady=10)

        # Output Directory
        self.output_dir_label = tk.Label(self.main_tab, text="Output Directory:")
        self.output_dir_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.output_dir_entry = tk.Entry(self.main_tab)
        self.output_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.output_dir_button = tk.Button(self.main_tab, text="Browse", command=self.browse_output_dir)
        self.output_dir_button.grid(row=1, column=2, padx=10, pady=10)

        # Quality Settings
        self.quality_label = tk.Label(self.main_tab, text="Quality Settings:")
        self.quality_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Image Multiplier
        self.multiplier_label = tk.Label(self.main_tab, text="Image Multiplier:")
        self.multiplier_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.multiplier_entry = tk.Entry(self.main_tab, width=10)
        self.multiplier_entry.insert(0, "1.0")
        self.multiplier_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Compression Quality
        self.quality_entry_label = tk.Label(self.main_tab, text="Compression Quality (0-100):")
        self.quality_entry_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.quality_entry = tk.Entry(self.main_tab, width=10)
        self.quality_entry.insert(0, "75")
        self.quality_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Progress Bar - Thinner and aligned with browse button
        self.progress_label = tk.Label(self.main_tab, text="Progress:")
        self.progress_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.progress_bar = ttk.Progressbar(
            self.main_tab, 
            orient="horizontal", 
            length=350,  # Adjusted length
            mode="determinate",
            style="Thin.Horizontal.TProgressbar"  # Custom style for thinner bar
        )
        self.progress_bar.grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky="w")

        # Configure thin progress bar style
        style = ttk.Style()
        style.configure("Thin.Horizontal.TProgressbar", thickness=6)  # Make progress bar thinner

        # Start Button
        self.start_button = tk.Button(self.main_tab, text="Start Compression", command=self.start_compression)
        self.start_button.grid(row=6, column=1, padx=10, pady=20)

        # Status Label
        self.status_label = tk.Label(self.main_tab, text="", fg="blue")
        self.status_label.grid(row=7, column=1, padx=10, pady=10)

        # More Options Tab
        self.more_options_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.more_options_tab, text="More Options")
        
        # Configure more options tab grid
        self.more_options_tab.grid_columnconfigure(1, weight=1)

        # Max Size (KB)
        self.max_size_label = tk.Label(self.more_options_tab, text="Max Size (KB):")
        self.max_size_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.max_size_entry = tk.Entry(self.more_options_tab, width=10)
        self.max_size_entry.insert(0, "54208")
        self.max_size_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Min Quality
        self.min_quality_label = tk.Label(self.more_options_tab, text="Min Quality (0-100):")
        self.min_quality_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.min_quality_entry = tk.Entry(self.more_options_tab, width=10)
        self.min_quality_entry.insert(0, "30")
        self.min_quality_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # New Options Added
        # Output Format Selection
        self.format_label = tk.Label(self.more_options_tab, text="Output Format:")
        self.format_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.format_var = tk.StringVar(value="jpg")
        self.format_combo = ttk.Combobox(
            self.more_options_tab, 
            textvariable=self.format_var,
            values=["jpg", "png", "webp"],
            width=7
        )
        self.format_combo.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Maintain EXIF Data
        self.maintain_exif_var = tk.BooleanVar(value=True)
        self.maintain_exif_check = ttk.Checkbutton(
            self.more_options_tab,
            text="Maintain EXIF Data",
            variable=self.maintain_exif_var
        )
        self.maintain_exif_check.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Auto-rotate based on EXIF
        self.auto_rotate_var = tk.BooleanVar(value=True)
        self.auto_rotate_check = ttk.Checkbutton(
            self.more_options_tab,
            text="Auto-rotate Images",
            variable=self.auto_rotate_var
        )
        self.auto_rotate_check.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Preserve Creation Date
        self.preserve_date_var = tk.BooleanVar(value=True)
        self.preserve_date_check = ttk.Checkbutton(
            self.more_options_tab,
            text="Preserve Creation Date",
            variable=self.preserve_date_var
        )
        self.preserve_date_check.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Color Mode
        self.color_mode_label = tk.Label(self.more_options_tab, text="Color Mode:")
        self.color_mode_label.grid(row=6, column=0, padx=10, pady=10, sticky="w")
        self.color_mode_var = tk.StringVar(value="RGB")
        self.color_mode_combo = ttk.Combobox(
            self.more_options_tab,
            textvariable=self.color_mode_var,
            values=["RGB", "Grayscale"],
            width=7
        )
        self.color_mode_combo.grid(row=6, column=1, padx=10, pady=10, sticky="w")

        # Thread pool for background tasks
        self.executor = ThreadPoolExecutor()
        self.futures = []

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

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

    def compress_image(self, input_path, output_path, image_multiplier, quality, max_size_kb, min_quality):
        """Compress and resize the image based on user settings."""
        img = Image.open(input_path)
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # Resize the image based on the multiplier
        width, height = img.size
        new_size = (int(width * image_multiplier), int(height * image_multiplier))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Compress the image with quality adjustment
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

    def process_image(self, input_path, output_path, image_multiplier, quality, max_size_kb, min_quality):
        """Helper function to process each image."""
        try:
            self.compress_image(input_path, output_path, image_multiplier, quality, max_size_kb, min_quality)
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

        # Get user settings
        try:
            image_multiplier = float(self.multiplier_entry.get())
            quality = int(self.quality_entry.get())
            max_size_kb = float(self.max_size_entry.get())
            min_quality = int(self.min_quality_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid input in settings fields!")
            return

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

        # Clear previous futures
        self.futures = []

        # Submit tasks to the thread pool
        for input_path in input_files:
            output_filename = input_path.stem + '.jpg'
            output_path = output_dir / output_filename
            future = self.executor.submit(
                self.process_image, input_path, output_path, image_multiplier, quality, max_size_kb, min_quality
            )
            self.futures.append(future)

        # Start monitoring the progress
        self.monitor_progress()

    def monitor_progress(self):
        """Monitor the progress of the compression tasks and update the GUI."""
        processed_count = 0
        skipped_count = 0

        for future in as_completed(self.futures):
            input_path, output_path, status = future.result()

            if output_path:
                processed_count += 1
            else:
                skipped_count += 1

            self.progress_bar["value"] += 1
            self.root.update_idletasks()

        # Update status when all tasks are complete
        self.status_label.config(text="Compression Complete!")
        messagebox.showinfo("Info", f"Successfully processed: {processed_count} images\nSkipped/Failed: {skipped_count} files")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCompressorApp(root)
    root.mainloop()