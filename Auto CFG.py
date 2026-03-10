import customtkinter as ctk
from customtkinter import CTk, CTkLabel, CTkEntry, CTkButton, CTkTextbox, CTkFrame, CTkComboBox
from tkinter import filedialog, messagebox, StringVar
import os
import sys
from datetime import datetime

FUCHSIA = "#e91e63"
FUCHSIA_DARK = "#c2185b"
BG_DARK = "#0d1117"
BG_WIDGET = "#161b22"
TEXT_NORMAL = "#c9d1d9"
TEXT_FUCHSIA = FUCHSIA
TEXT_ON_FUCHSIA = "#000000"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class AutoCFG:
    def __init__(self):
        self.root = CTk()

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        icon_path = os.path.join(base_path, "LOGO.ico")
        try:
            self.root.iconbitmap(icon_path)
        except:
            pass

        self.root.title("Auto CFG")
        self.root.geometry("1300x850")
        self.root.minsize(1100, 650)

        self.obj_path = StringVar()
        self.mtl_path = StringVar()

        self.mw_options = ["U", "U2", "MW", "PROSTREET", "CARBON", "WORLD"]
        self.driver_options = sorted([
            "ALUMINUM", "BOTTOM", "BRAKEDISC", "BRAKELIGHT", "BRAKELIGHTGLASS", "BRAKELIGHTGLASSRED",
            "BRAKELIGHTDULLPLASTIC", "BRAKELIGHT_GLASS", "CALIPER", "CALIPERDECAL", "CALLIPER",
            "CARBONFIBER", "CARBONFIBER2", "CARBONFIBRE", "CARBONITE", "CARSKIN", "CHASSIS", "CHROME",
            "CLEARPLASTIC", "COPPAINT", "DAMAGE", "DECAL", "DECALDULL", "DEFAULT", "DIABLOHP",
            "DOORLINE", "DRIVER", "DULLENGINE", "DULLPLASTIC", "DULLPLASTICT", "ENGINE", "EXHAUST_TIP",
            "GOLDROTOR", "GRILL", "GRILLCHROME", "HEADLIGHT", "HEADLIGHTCHROME", "HEADLIGHTGLASS",
            "HEADLIGHTREFLECTOR", "HLCHROME", "HLDULLPLASTIC", "HOSE", "HOSES", "INTERIOR",
            "LICENSEPLATE", "MAGCHROME", "MAGLIP", "MAGMATTE", "MAGGUNMETAL", "MAGSILVER",
            "MAGSILVERGLOSS", "MATTEPLASTIC", "MESH", "MIRROR", "MOLDING", "MOLDINGS", "PLAINNOTHING",
            "PLASTICHUBCAP", "PS_PAINT", "PS_WINDOW_FRONT", "PS_WINDOW_FRONT_LEFT", "PS_WINDOW_FRONT_RIGHT",
            "PS_WINDOW_REAR", "PS_WINDOW_REAR_LEFT", "PS_WINDOW_REAR_RIGHT", "RAD", "REGPAINTBLACK",
            "REGPAINTRED", "RUBBER", "SHINYPLASTIC", "TRAFFIC", "TRAFFICWINDOWS", "U2_PAINT",
            "WINDOWMASK", "WINDSHIELD", "WINDTUNNEL", "WINDTUNNELSHDW"
        ])

        self.materials = []
        self.parts_section = []
        self.markers_section = []

        self.setup_ui()
        self.root.mainloop()

    def setup_ui(self):
        main_frame = CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        file_frame = CTkFrame(main_frame)
        file_frame.pack(fill="x", pady=(0, 20))

        CTkLabel(file_frame, text="Project Files", font=("Arial", 16, "bold"), text_color=TEXT_FUCHSIA).pack(anchor="w", pady=(0, 10))

        row1 = CTkFrame(file_frame, fg_color="transparent")
        row1.pack(fill="x", pady=6)
        CTkLabel(row1, text="OBJ File:", width=140, anchor="e", text_color=TEXT_NORMAL).pack(side="left", padx=(0,10))
        CTkEntry(row1, textvariable=self.obj_path, fg_color=BG_WIDGET, text_color=TEXT_NORMAL).pack(side="left", fill="x", expand=True, padx=5)
        CTkButton(row1, text="Load OBJ", width=120, command=self.browse_obj,
                  fg_color=FUCHSIA, hover_color=FUCHSIA_DARK, text_color=TEXT_ON_FUCHSIA).pack(side="left", padx=5)

        row2 = CTkFrame(file_frame, fg_color="transparent")
        row2.pack(fill="x", pady=6)
        CTkLabel(row2, text="MTL File:", width=140, anchor="e", text_color=TEXT_NORMAL).pack(side="left", padx=(0,10))
        CTkEntry(row2, textvariable=self.mtl_path, fg_color=BG_WIDGET, text_color=TEXT_NORMAL).pack(side="left", fill="x", expand=True, padx=5)
        CTkButton(row2, text="Load MTL", width=120, command=self.browse_mtl,
                  fg_color=FUCHSIA, hover_color=FUCHSIA_DARK, text_color=TEXT_ON_FUCHSIA).pack(side="left", padx=5)

        CTkButton(main_frame, text="GENERATE & LOAD MATERIALS", command=self.generate_cfg,
                  fg_color=FUCHSIA, hover_color=FUCHSIA_DARK, text_color=TEXT_ON_FUCHSIA,
                  font=("Arial", 16, "bold"), height=45, corner_radius=10).pack(pady=20)

        split_frame = CTkFrame(main_frame, fg_color="transparent")
        split_frame.pack(fill="both", expand=True)

        left_frame = CTkFrame(split_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0,10))

        CTkLabel(left_frame, text="Materials (edit MW & Driver)", text_color=TEXT_FUCHSIA, font=("Arial", 14)).pack(anchor="w", pady=(0,8))

        self.materials_scroll = ctk.CTkScrollableFrame(left_frame, fg_color=BG_WIDGET)
        self.materials_scroll.pack(fill="both", expand=True)

        CTkButton(left_frame, text="UPDATE FINAL OUTPUT", command=self.update_output_text,
                  fg_color=FUCHSIA, hover_color=FUCHSIA_DARK, text_color=TEXT_ON_FUCHSIA,
                  font=("Arial", 14, "bold"), height=40).pack(pady=15, fill="x")

        right_frame = CTkFrame(split_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10,0))

        CTkLabel(right_frame, text="Final Output", text_color=TEXT_FUCHSIA, font=("Arial", 14)).pack(anchor="w", pady=(0,8))

        self.output_text = CTkTextbox(right_frame, font=("Consolas", 11), fg_color=BG_DARK, text_color=TEXT_NORMAL, state="disabled")
        self.output_text.pack(fill="both", expand=True)

        CTkButton(main_frame, text="Save .txt", command=self.save_output,
                  fg_color=FUCHSIA, hover_color=FUCHSIA_DARK, text_color=TEXT_ON_FUCHSIA,
                  width=180, height=40).pack(pady=15)

    def generate_cfg(self):
        if not self.obj_path.get() or not self.mtl_path.get():
            messagebox.showerror("Error", "Please select both OBJ and MTL files")
            return

        materials_temp = {}
        try:
            with open(self.mtl_path.get(), 'r', encoding='utf-8') as f:
                current_mat = None
                for line in f:
                    line = line.strip()
                    if line.startswith('newmtl '):
                        current_mat = line.split(' ', 1)[1].strip()
                    elif line.startswith('map_Kd ') and current_mat:
                        tex = os.path.splitext(os.path.basename(line.split(' ', 1)[1].strip()))[0]
                        materials_temp[current_mat] = tex
        except Exception as e:
            messagebox.showerror("Error", f"Error reading MTL:\n{e}")
            return

        parts = []
        markers = []
        try:
            with open(self.obj_path.get(), 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('o '):
                        obj_name = line.split(' ', 1)[1].strip()
                        if obj_name.startswith('_'):
                            markers.append(obj_name)
                        else:
                            parts.append(obj_name)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading OBJ:\n{e}")
            return

        self.materials = []
        for mat, tex in materials_temp.items():
            mw_var = ctk.StringVar(value="U")
            driver_var = ctk.StringVar(value="DEFAULT")
            self.materials.append({
                "mat": mat,
                "tex": tex,
                "mw_var": mw_var,
                "driver_var": driver_var
            })

        for widget in self.materials_scroll.winfo_children():
            widget.destroy()

        for i, item in enumerate(self.materials):
            row = CTkFrame(self.materials_scroll, fg_color="transparent")
            row.pack(fill="x", pady=4, padx=5)

            CTkLabel(row, text=item["mat"], width=180, anchor="w", text_color=TEXT_NORMAL).pack(side="left", padx=5)
            CTkLabel(row, text=item["tex"], width=180, anchor="w", text_color="#88ff88").pack(side="left", padx=5)

            mw_combo = CTkComboBox(row, values=self.mw_options, variable=item["mw_var"], width=110,
                                   fg_color=BG_DARK, text_color=TEXT_NORMAL)
            mw_combo.pack(side="left", padx=5)

            driver_combo = CTkComboBox(row, values=self.driver_options, variable=item["driver_var"], width=220,
                                       fg_color=BG_DARK, text_color=TEXT_NORMAL)
            driver_combo.pack(side="left", padx=5)

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.parts_section = [f"# Generated on {date}\n#\n# Parts\n#"]
        for p in parts:
            self.parts_section.append(f"PART MW {p} {p}")

        self.markers_section = ["#\n# Position markers\n#"]
        for m in markers:
            self.markers_section.append(f"MARKER MW {m} {m} BASE_A")

        self.update_output_text()

    def update_output_text(self):
        self.output_text.configure(state="normal")
        self.output_text.delete("0.0", "end")

        for line in self.parts_section:
            self.output_text.insert("end", line + "\n")

        self.output_text.insert("end", "#\n# Materials\n#\n")
        for item in self.materials:
            mw = item["mw_var"].get()
            driver = item["driver_var"].get()
            line = f"MATERIAL {mw} {item['mat']} {driver} {item['tex']}"
            self.output_text.insert("end", line + "\n")

        for line in self.markers_section:
            self.output_text.insert("end", line + "\n")

        self.output_text.configure(state="disabled")

    def save_output(self):
        content = self.output_text.get("0.0", "end").strip()
        if not content or len(content) < 50:
            messagebox.showwarning("Warning", "Generate and update first")
            return

        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Saved", "File saved successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def browse_obj(self):
        path = filedialog.askopenfilename(filetypes=[("OBJ files", "*.obj")])
        if path: self.obj_path.set(path)

    def browse_mtl(self):
        path = filedialog.askopenfilename(filetypes=[("MTL files", "*.mtl")])
        if path: self.mtl_path.set(path)


if __name__ == "__main__":
    AutoCFG()