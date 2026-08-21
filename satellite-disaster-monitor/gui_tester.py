import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

class DisasterTesterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Satellite Disaster Model Tester")
        self.root.geometry("750x600")
        self.root.configure(bg="#0f172a")

        # Title Header
        header = tk.Label(
            root,
            text="🛰️ Satellite Disaster AI Model Tester",
            font=("Segoe UI", 16, "bold"),
            bg="#0f172a",
            fg="#f8fafc",
            pady=15
        )
        header.pack()

        sub_header = tk.Label(
            root,
            text="Select a model below to open a image file dialog (.tif, .png, .jpg) & run inference:",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#94a3b8"
        )
        sub_header.pack(pady=(0, 15))

        # Button Frame
        btn_frame = tk.Frame(root, bg="#0f172a")
        btn_frame.pack(pady=10)

        # Wildfire Button
        btn_wildfire = tk.Button(
            btn_frame,
            text="🔥 Test Wildfire Model",
            font=("Segoe UI", 11, "bold"),
            bg="#dc2626",
            fg="white",
            activebackground="#b91c1c",
            activeforeground="white",
            px=15,
            py=8,
            relief="flat",
            command=self.run_wildfire_test
        )
        btn_wildfire.grid(row=0, column=0, padx=8)

        # Landslide Button
        btn_landslide = tk.Button(
            btn_frame,
            text="⛰️ Test Landslide Model",
            font=("Segoe UI", 11, "bold"),
            bg="#d97706",
            fg="white",
            activebackground="#b45309",
            activeforeground="white",
            px=15,
            py=8,
            relief="flat",
            command=self.run_landslide_test
        )
        btn_landslide.grid(row=0, column=1, padx=8)

        # Flood Button
        btn_flood = tk.Button(
            btn_frame,
            text="🌊 Test Flood Model",
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            px=15,
            py=8,
            relief="flat",
            command=self.run_flood_test
        )
        btn_flood.grid(row=0, column=2, padx=8)

        # Console Output Box
        console_frame = tk.Frame(root, bg="#1e293b", bd=1, relief="solid")
        console_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.text_area = tk.Text(
            console_frame,
            wrap="word",
            font=("Consolas", 10),
            bg="#020617",
            fg="#38bdf8",
            insertbackground="white",
            padx=10,
            pady=10
        )
        self.text_area.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(console_frame, command=self.text_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=scrollbar.set)

        self.log("💡 Ready! Click any button above to pick a satellite TIF file and test the AI model.")

    def log(self, text):
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)

    def pick_file(self, title):
        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=[
                ("Satellite Imagery", "*.tif *.tiff *.png *.jpg *.jpeg"),
                ("All Files", "*.*")
            ]
        )
        return file_path

    def run_wildfire_test(self):
        file_path = self.pick_file("Select Wildfire Satellite TIF File")
        if not file_path:
            return
        self.log("\n" + "=" * 60)
        self.log(f"🔥 Running Wildfire Model Test on: {file_path}")
        self.log("=" * 60)

        try:
            from backend.test_wildfire import test_wildfire
            # Redirect stdout to capture logs
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                test_wildfire(file_path)
            self.log(f.getvalue())
        except Exception as e:
            self.log(f"❌ Error during test execution: {e}")

    def run_landslide_test(self):
        file_path = self.pick_file("Select Landslide Satellite TIF File")
        if not file_path:
            return
        self.log("\n" + "=" * 60)
        self.log(f"⛰️ Running Landslide Model Test on: {file_path}")
        self.log("=" * 60)

        try:
            from backend.test_landslide import test_landslide
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                test_landslide(file_path)
            self.log(f.getvalue())
        except Exception as e:
            self.log(f"❌ Error during test execution: {e}")

    def run_flood_test(self):
        file_path = self.pick_file("Select Flood Satellite TIF File")
        if not file_path:
            return
        self.log("\n" + "=" * 60)
        self.log(f"🌊 Running Flood Model Test on: {file_path}")
        self.log("=" * 60)

        try:
            from backend.test_flood import test_flood
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                test_flood(file_path)
            self.log(f.getvalue())
        except Exception as e:
            self.log(f"❌ Error during test execution: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DisasterTesterGUI(root)
    root.mainloop()
