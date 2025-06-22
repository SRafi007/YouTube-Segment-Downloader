import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import subprocess
import sys


class YouTubeSegmentDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Segment Downloader")
        self.root.geometry("600x400")

        # Variables
        self.output_dir = tk.StringVar(value=os.getcwd())
        self.is_downloading = False

        self.setup_ui()
        self.check_dependencies()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # URL input
        ttk.Label(main_frame, text="YouTube URL:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.url_entry = ttk.Entry(main_frame, width=70)
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Time inputs
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(time_frame, text="Start Time (HH:MM:SS or MM:SS):").grid(
            row=0, column=0, sticky=tk.W
        )
        self.start_time_entry = ttk.Entry(time_frame, width=15)
        self.start_time_entry.grid(row=0, column=1, padx=(10, 20))

        ttk.Label(time_frame, text="End Time (HH:MM:SS or MM:SS):").grid(
            row=0, column=2, sticky=tk.W
        )
        self.end_time_entry = ttk.Entry(time_frame, width=15)
        self.end_time_entry.grid(row=0, column=3, padx=(10, 0))

        # Output directory
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(output_frame, text="Output Directory:").grid(
            row=0, column=0, sticky=tk.W
        )
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(
            row=1, column=0, sticky=(tk.W, tk.E)
        )
        ttk.Button(output_frame, text="Browse", command=self.browse_directory).grid(
            row=1, column=1, padx=(10, 0)
        )

        output_frame.columnconfigure(0, weight=1)

        # Quality selection
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(quality_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W)
        self.quality_var = tk.StringVar(value="best[height<=1080]")
        quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.quality_var,
            width=25,
            values=[
                "best[height<=1080]",
                "best[height<=720]",
                "best[height<=480]",
                "best[height<=360]",
                "best",
                "bestvideo[height<=1080]+bestaudio/best",
                "bestvideo[height<=720]+bestaudio/best",
            ],
        )
        quality_combo.grid(row=0, column=1, padx=(10, 0))

        # Format selection
        ttk.Label(quality_frame, text="Format:").grid(
            row=1, column=0, sticky=tk.W, pady=(5, 0)
        )
        self.format_var = tk.StringVar(value="mp4")
        format_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.format_var,
            width=10,
            values=["mp4", "mkv", "webm"],
        )
        format_combo.grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky=tk.W)

        # Download button
        self.download_btn = ttk.Button(
            main_frame, text="Download Segment", command=self.start_download
        )
        self.download_btn.grid(row=5, column=0, columnspan=2, pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Status text
        self.status_text = tk.Text(main_frame, height=8, width=70)
        self.status_text.grid(
            row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5
        )

        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(
            main_frame, orient="vertical", command=self.status_text.yview
        )
        scrollbar.grid(row=7, column=2, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def check_dependencies(self):
        """Check if yt-dlp and ffmpeg are installed"""
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
            self.log_status("✓ yt-dlp found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_status("✗ yt-dlp not found. Install with: pip install yt-dlp")

        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            self.log_status("✓ ffmpeg found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_status(
                "✗ ffmpeg not found. Download from: https://ffmpeg.org/download.html"
            )

    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)

    def log_status(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()

    def validate_time_format(self, time_str):
        """Validate time format (HH:MM:SS or MM:SS)"""
        if not time_str:
            return False

        parts = time_str.split(":")
        if len(parts) not in [2, 3]:
            return False

        try:
            for part in parts:
                int(part)
            return True
        except ValueError:
            return False

    def start_download(self):
        if self.is_downloading:
            return

        url = self.url_entry.get().strip()
        start_time = self.start_time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        if not start_time or not end_time:
            messagebox.showerror("Error", "Please enter both start and end times")
            return

        if not self.validate_time_format(start_time) or not self.validate_time_format(
            end_time
        ):
            messagebox.showerror("Error", "Invalid time format. Use HH:MM:SS or MM:SS")
            return

        # Start download in separate thread
        self.is_downloading = True
        self.download_btn.config(state="disabled")
        self.progress.start()

        thread = threading.Thread(
            target=self.download_segment, args=(url, start_time, end_time)
        )
        thread.daemon = True
        thread.start()

    def download_segment(self, url, start_time, end_time):
        try:
            self.log_status(f"Starting download from {start_time} to {end_time}...")

            # Build yt-dlp command
            quality_format = self.quality_var.get()
            output_format = self.format_var.get()
            output_path = os.path.join(
                self.output_dir.get(), f"segment_%(title)s_%(id)s.{output_format}"
            )

            cmd = [
                "yt-dlp",
                "--download-sections",
                f"*{start_time}-{end_time}",
                "-f",
                quality_format,
                "--merge-output-format",
                output_format,
                "--embed-metadata",
                "--no-playlist",
                "-o",
                output_path,
                url,
            ]

            self.log_status(f"Using format: {quality_format}")
            self.log_status(f"Output format: {output_format}")
            self.log_status(f"Running command: {' '.join(cmd)}")

            # Execute command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            # Read output line by line
            for line in process.stdout:
                self.log_status(line.strip())

            process.wait()

            if process.returncode == 0:
                self.log_status("✓ Download completed successfully!")
                messagebox.showinfo("Success", "Segment downloaded successfully!")
            else:
                self.log_status("✗ Download failed!")
                messagebox.showerror(
                    "Error", "Download failed. Check the log for details."
                )

        except Exception as e:
            self.log_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        finally:
            self.is_downloading = False
            self.root.after(0, self.reset_ui)

    def get_quality_format(self):
        # This method is no longer used, but kept for compatibility
        return self.quality_var.get()

    def reset_ui(self):
        self.download_btn.config(state="normal")
        self.progress.stop()


def main():
    root = tk.Tk()
    app = YouTubeSegmentDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
