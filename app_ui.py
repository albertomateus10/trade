import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from data_processor import DataProcessor
import pandas as pd

class AppUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Plate Search Pro • High Performance")
        self.geometry("1100x700")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.processor = DataProcessor()
        self.setup_ui()

    def setup_ui(self):
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Plate Search Pro", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20)

        self.btn_load = ctk.CTkButton(self.sidebar, text="Carregar Base Excel", command=self.load_file)
        self.btn_load.pack(pady=10, padx=20, fill="x")

        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Buscar placa...")
        self.search_entry.pack(pady=10, padx=20, fill="x")
        self.search_entry.bind("<KeyRelease>", self.on_search)

        self.stats_label = ctk.CTkLabel(self.sidebar, text="Status: Aguardando arquivo", font=ctk.CTkFont(size=12))
        self.stats_label.pack(side="bottom", pady=20)

        self.progress_bar = ctk.CTkProgressBar(self.sidebar)
        self.progress_bar.pack(side="bottom", pady=10, padx=20, fill="x")
        self.progress_bar.set(0)

        # Results List (Scrollable Frame)
        self.results_frame = ctk.CTkScrollableFrame(self, label_text="Resultados da Busca")
        self.results_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Details Panel (Initially hidden or as a secondary view)
        # We'll use a simple approach: clicking a result shows details in a popup or a dedicated area

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not path:
            return

        self.btn_load.configure(state="disabled")
        self.stats_label.configure(text="Carregando...")
        self.progress_bar.set(0)

        def thread_task():
            try:
                count = self.processor.load_excel(path, self.update_progress)
                self.after(0, lambda: self.on_load_success(count, path))
            except Exception as e:
                self.after(0, lambda: self.on_load_error(str(e)))

        threading.Thread(target=thread_task, daemon=True).start()

    def update_progress(self, val, text):
        self.after(0, lambda: self.progress_bar.set(val))
        self.after(0, lambda: self.stats_label.configure(text=text))

    def on_load_success(self, count, path):
        self.btn_load.configure(state="normal")
        filename = path.split("/")[-1]
        self.stats_label.configure(text=f"Pronto: {count} registros em {filename}")
        self.on_search()

    def on_load_error(self, err):
        self.btn_load.configure(state="normal")
        print(f"ERRO CRÍTICO NO CARREGAMENTO: {err}")
        messagebox.showerror("Erro", f"Falha ao carregar excel:\n{err}\n\nVerifique o terminal para detalhes.")
        self.stats_label.configure(text="Erro ao carregar")

    def on_search(self, event=None):
        query = self.search_entry.get()
        results = self.processor.search(query)
        self.display_results(results)

    def display_results(self, df):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if df.empty:
            lbl = ctk.CTkLabel(self.results_frame, text="Nenhum resultado encontrado")
            lbl.pack(pady=20)
            return

        for _, row in df.head(100).iterrows():
            frame = ctk.CTkFrame(self.results_frame)
            frame.pack(fill="x", pady=5, padx=5)
            
            plate = str(row['plate_raw'])
            sheet = str(row['sheet_name'])
            
            # Simple list item
            ctk.CTkLabel(frame, text=plate, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            ctk.CTkLabel(frame, text=f"({sheet})").pack(side="left", padx=5)
            
            btn = ctk.CTkButton(frame, text="Ver Detalhes", width=80, command=lambda r=row: self.show_details(r))
            btn.pack(side="right", padx=10)

    def show_details(self, row):
        details_win = ctk.CTkToplevel(self)
        details_win.title(f"Detalhes: {row['plate_raw']}")
        details_win.geometry("500x600")
        
        # Lift and focus
        details_win.attributes('-topmost', True)

        scroll = ctk.CTkScrollableFrame(details_win)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        for col, val in row.items():
            if col in ['plate_norm', 'plate_raw', 'sheet_name', 'row_index']:
                continue
            if pd.notna(val):
                f = ctk.CTkFrame(scroll)
                f.pack(fill="x", pady=2)
                ctk.CTkLabel(f, text=f"{col}:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
                ctk.CTkLabel(f, text=str(val)).pack(side="left", padx=5)

if __name__ == "__main__":
    app = AppUI()
    app.mainloop()
