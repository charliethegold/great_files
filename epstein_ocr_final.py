#!/usr/bin/env python3
"""
ENHANCED OCR APP
With dark mode, progress tracking, and pause/resume
"""

from tkinter import *
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import time
import threading

class EnhancedOCR:
    def __init__(self):
        # Create window
        self.window = Tk()
        self.window.title("Enhanced OCR - Epstein Files Processing")
        self.window.geometry("900x700")
        self.window.configure(bg="#1e1e1e")
        
        # Variables
        self.folder = ""
        self.processing = False
        self.paused = False
        self.stop_requested = False
        
        # Setup UI
        self.setup_ui()
        
        # Run
        self.window.mainloop()
    
    def setup_ui(self):
        """Create the dark mode user interface"""
        
        # Colors (Dark Mode)
        bg_dark = "#1e1e1e"
        bg_medium = "#2d2d2d"
        bg_light = "#3d3d3d"
        text_color = "#ffffff"
        accent_blue = "#0078d4"
        accent_green = "#10b981"
        accent_orange = "#f59e0b"
        accent_red = "#ef4444"
        
        # Title Section
        title_frame = Frame(self.window, bg="#0078d4", pady=20)
        title_frame.pack(fill=X)
        
        Label(title_frame, text="🔍 Enhanced OCR Processor", 
              font=("Arial", 22, "bold"), bg="#0078d4", fg="white").pack()
        Label(title_frame, text="Batch OCR with Progress Tracking & Time Estimation", 
              font=("Arial", 11), bg="#0078d4", fg="#e0e0e0").pack()
        
        # Main container
        main_frame = Frame(self.window, bg=bg_dark, padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Folder Selection
        folder_frame = Frame(main_frame, bg=bg_medium, padx=15, pady=15)
        folder_frame.pack(fill=X, pady=(0, 15))
        
        Label(folder_frame, text="📁 Select Folder:", font=("Arial", 12, "bold"), 
              bg=bg_medium, fg=text_color).pack(anchor=W, pady=(0, 8))
        
        folder_inner = Frame(folder_frame, bg=bg_medium)
        folder_inner.pack(fill=X)
        
        self.folder_label = Label(folder_inner, text="No folder selected", 
                                 font=("Arial", 10), bg=bg_light, fg="#a0a0a0",
                                 anchor=W, padx=10, pady=8)
        self.folder_label.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        Button(folder_inner, text="Browse", command=self.select_folder,
               bg=accent_blue, fg="white", font=("Arial", 10, "bold"),
               padx=20, pady=8, cursor="hand2", relief=FLAT).pack(side=LEFT)
        
        # Stats Section
        stats_frame = Frame(main_frame, bg=bg_medium, padx=15, pady=15)
        stats_frame.pack(fill=X, pady=(0, 15))
        
        Label(stats_frame, text="📊 Processing Statistics", font=("Arial", 12, "bold"),
              bg=bg_medium, fg=text_color).pack(anchor=W, pady=(0, 10))
        
        stats_grid = Frame(stats_frame, bg=bg_medium)
        stats_grid.pack(fill=X)
        
        # Left column
        left_col = Frame(stats_grid, bg=bg_medium)
        left_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        Label(left_col, text="Total Files:", font=("Arial", 9),
              bg=bg_medium, fg="#a0a0a0").pack(anchor=W)
        self.total_files_label = Label(left_col, text="0", font=("Arial", 20, "bold"),
                                      bg=bg_medium, fg=accent_blue)
        self.total_files_label.pack(anchor=W)
        
        # Middle column
        mid_col = Frame(stats_grid, bg=bg_medium)
        mid_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        Label(mid_col, text="Processed:", font=("Arial", 9),
              bg=bg_medium, fg="#a0a0a0").pack(anchor=W)
        self.processed_label = Label(mid_col, text="0", font=("Arial", 20, "bold"),
                                    bg=bg_medium, fg=accent_green)
        self.processed_label.pack(anchor=W)
        
        # Right column
        right_col = Frame(stats_grid, bg=bg_medium)
        right_col.pack(side=LEFT, fill=BOTH, expand=True)
        
        Label(right_col, text="Remaining:", font=("Arial", 9),
              bg=bg_medium, fg="#a0a0a0").pack(anchor=W)
        self.remaining_label = Label(right_col, text="0", font=("Arial", 20, "bold"),
                                    bg=bg_medium, fg=accent_orange)
        self.remaining_label.pack(anchor=W)
        
        # Time Estimation (BIG AND PROMINENT)
        time_frame = Frame(main_frame, bg=bg_medium, padx=15, pady=15)
        time_frame.pack(fill=X, pady=(0, 15))
        
        Label(time_frame, text="⏱️ Time Tracking", font=("Arial", 12, "bold"),
              bg=bg_medium, fg=text_color).pack(anchor=W, pady=(0, 10))
        
        time_grid = Frame(time_frame, bg=bg_medium)
        time_grid.pack(fill=X)
        
        # Elapsed time
        elapsed_col = Frame(time_grid, bg=bg_medium)
        elapsed_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        Label(elapsed_col, text="Elapsed Time:", font=("Arial", 9),
              bg=bg_medium, fg="#a0a0a0").pack(anchor=W)
        self.elapsed_label = Label(elapsed_col, text="0:00:00", font=("Arial", 18, "bold"),
                                  bg=bg_medium, fg=text_color)
        self.elapsed_label.pack(anchor=W)
        
        # Estimated remaining
        remaining_col = Frame(time_grid, bg=bg_medium)
        remaining_col.pack(side=LEFT, fill=BOTH, expand=True)
        
        Label(remaining_col, text="Est. Remaining:", font=("Arial", 9),
              bg=bg_medium, fg="#a0a0a0").pack(anchor=W)
        self.est_remaining_label = Label(remaining_col, text="--:--:--", 
                                        font=("Arial", 18, "bold"),
                                        bg=bg_medium, fg=accent_orange)
        self.est_remaining_label.pack(anchor=W)
        
        # Progress Bar Section
        progress_frame = Frame(main_frame, bg=bg_medium, padx=15, pady=15)
        progress_frame.pack(fill=X, pady=(0, 15))
        
        Label(progress_frame, text="📈 Progress", font=("Arial", 12, "bold"),
              bg=bg_medium, fg=text_color).pack(anchor=W, pady=(0, 10))
        
        self.progress_percentage = Label(progress_frame, text="0%", 
                                        font=("Arial", 16, "bold"),
                                        bg=bg_medium, fg=accent_blue)
        self.progress_percentage.pack(anchor=W, pady=(0, 5))
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure("custom.Horizontal.TProgressbar", 
                       troughcolor=bg_light,
                       background=accent_blue,
                       bordercolor=bg_medium,
                       lightcolor=accent_blue,
                       darkcolor=accent_blue)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate',
                                           style="custom.Horizontal.TProgressbar",
                                           length=400)
        self.progress_bar.pack(fill=X, pady=(0, 8))
        
        self.current_file_label = Label(progress_frame, text="Ready to process...",
                                       font=("Arial", 9), bg=bg_medium, fg="#a0a0a0",
                                       anchor=W)
        self.current_file_label.pack(fill=X)
        
        # Completed Files List
        files_frame = Frame(main_frame, bg=bg_medium, padx=15, pady=15)
        files_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        Label(files_frame, text="✅ Recently Completed Files", font=("Arial", 12, "bold"),
              bg=bg_medium, fg=text_color).pack(anchor=W, pady=(0, 10))
        
        self.files_list = ScrolledText(files_frame, height=10, font=("Courier", 9),
                                      bg=bg_light, fg=text_color, wrap=WORD,
                                      insertbackground=text_color)
        self.files_list.pack(fill=BOTH, expand=True)
        self.files_list.insert(END, "No files processed yet...\n")
        self.files_list.config(state=DISABLED)
        
        # Control Buttons
        button_frame = Frame(main_frame, bg=bg_dark)
        button_frame.pack(fill=X)
        
        self.start_button = Button(button_frame, text="▶ Start Processing",
                                   command=self.start_processing,
                                   bg=accent_green, fg="white",
                                   font=("Arial", 12, "bold"),
                                   padx=25, pady=12, cursor="hand2", relief=FLAT)
        self.start_button.pack(side=LEFT, padx=(0, 10))
        
        self.pause_button = Button(button_frame, text="⏸ Pause",
                                   command=self.toggle_pause,
                                   bg=accent_orange, fg="white",
                                   font=("Arial", 12, "bold"),
                                   padx=25, pady=12, cursor="hand2",
                                   relief=FLAT, state=DISABLED)
        self.pause_button.pack(side=LEFT, padx=(0, 10))
        
        self.stop_button = Button(button_frame, text="⏹ Stop",
                                  command=self.stop_processing,
                                  bg=accent_red, fg="white",
                                  font=("Arial", 12, "bold"),
                                  padx=25, pady=12, cursor="hand2",
                                  relief=FLAT, state=DISABLED)
        self.stop_button.pack(side=LEFT)
    
    def select_folder(self):
        """Select folder with files"""
        folder = filedialog.askdirectory(title="Select folder with images/PDFs")
        if folder:
            self.folder = folder
            self.folder_label.config(text=folder, fg="white")
            
            # Count files
            folder_path = Path(self.folder)
            files = list(folder_path.rglob("*.jpg")) + \
                    list(folder_path.rglob("*.png")) + \
                    list(folder_path.rglob("*.jpeg")) + \
                    list(folder_path.rglob("*.pdf")) + \
                    list(folder_path.rglob("*.tiff")) + \
                    list(folder_path.rglob("*.JPG")) + \
                    list(folder_path.rglob("*.PNG")) + \
                    list(folder_path.rglob("*.JPEG")) + \
                    list(folder_path.rglob("*.PDF"))
            
            total = len(files)
            self.total_files_label.config(text=str(total))
            self.remaining_label.config(text=str(total))
            
            # Estimate time
            pdf_count = sum(1 for f in files if f.suffix.lower() == '.pdf')
            image_count = total - pdf_count
            estimated_seconds = (image_count * 2) + (pdf_count * 5)
            
            hours = int(estimated_seconds // 3600)
            minutes = int((estimated_seconds % 3600) // 60)
            seconds = int(estimated_seconds % 60)
            
            self.est_remaining_label.config(text=f"{hours}:{minutes:02d}:{seconds:02d}")
    
    def format_time(self, seconds):
        """Format seconds to HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}:{minutes:02d}:{secs:02d}"
    
    def add_to_file_list(self, message):
        """Add message to completed files list"""
        self.files_list.config(state=NORMAL)
        self.files_list.insert(END, message + "\n")
        self.files_list.see(END)
        self.files_list.config(state=DISABLED)
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="▶ Resume")
            self.current_file_label.config(text="⏸ PAUSED - Click Resume to continue")
        else:
            self.pause_button.config(text="⏸ Pause")
    
    def stop_processing(self):
        """Stop processing"""
        if messagebox.askyesno("Confirm Stop", "Are you sure you want to stop processing?"):
            self.stop_requested = True
            self.current_file_label.config(text="⏹ Stopping... Please wait")
    
    def start_processing(self):
        """Start processing in a thread"""
        if not self.folder:
            messagebox.showerror("Error", "Please select a folder first!")
            return
        
        if self.processing:
            messagebox.showwarning("Already Processing", "Processing is already in progress!")
            return
        
        # Reset state
        self.processing = True
        self.paused = False
        self.stop_requested = False
        
        # Update buttons
        self.start_button.config(state=DISABLED)
        self.pause_button.config(state=NORMAL)
        self.stop_button.config(state=NORMAL)
        
        # Clear file list
        self.files_list.config(state=NORMAL)
        self.files_list.delete(1.0, END)
        self.files_list.config(state=DISABLED)
        
        # Start processing thread
        thread = threading.Thread(target=self.process_files, daemon=True)
        thread.start()
    
    def process_files(self):
        """Process all files with OCR"""
        start_time = time.time()
        
        folder_path = Path(self.folder)
        files = list(folder_path.rglob("*.jpg")) + \
                list(folder_path.rglob("*.png")) + \
                list(folder_path.rglob("*.jpeg")) + \
                list(folder_path.rglob("*.pdf")) + \
                list(folder_path.rglob("*.tiff")) + \
                list(folder_path.rglob("*.JPG")) + \
                list(folder_path.rglob("*.PNG")) + \
                list(folder_path.rglob("*.JPEG")) + \
                list(folder_path.rglob("*.PDF"))
        
        total_files = len(files)
        output_folder = folder_path / "ocr_results"
        output_folder.mkdir(exist_ok=True)
        
        count = 0
        total_processing_time = 0
        
        skipped = 0
        
        for idx, file in enumerate(files, 1):
            # Check if stopped
            if self.stop_requested:
                self.add_to_file_list(f"⏹ Processing stopped by user at {count}/{total_files} files")
                break
            
            # Wait if paused
            while self.paused and not self.stop_requested:
                time.sleep(0.1)
            
            if self.stop_requested:
                break
            
            try:
                # Check if already processed
                output_file = output_folder / f"{file.stem}.txt"
                if output_file.exists():
                    skipped += 1
                    self.add_to_file_list(f"⏭️  [{idx}/{total_files}] {file.name} (already processed, skipped)")
                    
                    # Update stats (count as processed for progress)
                    count += 1
                    self.processed_label.config(text=str(count))
                    self.remaining_label.config(text=str(total_files - count))
                    
                    # Update progress bar
                    progress_pct = (count / total_files) * 100
                    self.progress_bar['value'] = progress_pct
                    self.progress_percentage.config(text=f"{progress_pct:.1f}%")
                    
                    self.window.update()
                    continue
                
                file_start = time.time()
                
                # Update current file
                self.current_file_label.config(text=f"Processing: {file.name}")
                self.window.update()
                
                # Do OCR
                if file.suffix.lower() == '.pdf':
                    images = convert_from_path(file)
                    text = ""
                    for i, img in enumerate(images):
                        text += f"\n--- Page {i+1} ---\n"
                        text += pytesseract.image_to_string(img)
                else:
                    img = Image.open(file)
                    text = pytesseract.image_to_string(img)
                
                # Save result
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                file_time = time.time() - file_start
                total_processing_time += file_time
                count += 1
                
                # Update stats
                self.processed_label.config(text=str(count))
                self.remaining_label.config(text=str(total_files - count))
                
                # Update progress bar
                progress_pct = (count / total_files) * 100
                self.progress_bar['value'] = progress_pct
                self.progress_percentage.config(text=f"{progress_pct:.1f}%")
                
                # Update elapsed time
                elapsed = time.time() - start_time
                self.elapsed_label.config(text=self.format_time(elapsed))
                
                # Calculate remaining time
                if count > 0:
                    avg_time = total_processing_time / count
                    est_remaining_secs = avg_time * (total_files - count)
                    self.est_remaining_label.config(text=self.format_time(est_remaining_secs))
                
                # Add to file list
                self.add_to_file_list(f"✅ [{count}/{total_files}] {file.name} ({file_time:.1f}s)")
                
                self.window.update()
                
            except Exception as e:
                self.add_to_file_list(f"❌ Error: {file.name} - {str(e)}")
        
        # Done
        total_time = time.time() - start_time
        
        actually_processed = count - skipped
        
        self.current_file_label.config(text=f"✅ Complete! Processed {actually_processed} new files, {skipped} already done")
        self.progress_bar['value'] = 100
        self.progress_percentage.config(text="100%")
        self.est_remaining_label.config(text="0:00:00")
        
        # Reset buttons
        self.start_button.config(state=NORMAL)
        self.pause_button.config(state=DISABLED)
        self.stop_button.config(state=DISABLED)
        self.processing = False
        
        messagebox.showinfo("Complete!",
                           f"OCR Processing Complete!\n\n"
                           f"Total files: {total_files}\n"
                           f"Newly processed: {actually_processed}\n"
                           f"Already completed (skipped): {skipped}\n"
                           f"Total time: {self.format_time(total_time)}\n"
                           f"Results saved to:\n{output_folder}")

# Run the app
if __name__ == '__main__':
    EnhancedOCR()
