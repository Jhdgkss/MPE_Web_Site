import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import requests
import json
import os
import threading

class RemoteStockImporter:
    def __init__(self, root):
        self.root = root
        self.root.title("MPE Remote Stock Uploader")
        self.root.geometry("900x750")
        
        # Data State
        self.excel_file = None
        self.df = None
        self.sheet_names = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- Styles ---
        style = ttk.Style()
        style.configure("Bold.TLabel", font=('Arial', 10, 'bold'))
        
        # --- Main Container ---
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Title ---
        ttk.Label(main_frame, text="Remote Stock Uploader", font=('Arial', 16, 'bold')).pack(pady=(0, 15))

        # --- 1. Server Configuration ---
        config_frame = ttk.LabelFrame(main_frame, text="1. Server Details (Railway)", padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        
        grid_conf = ttk.Frame(config_frame)
        grid_conf.pack(fill=tk.X)
        
        ttk.Label(grid_conf, text="Website URL:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.url_var = tk.StringVar(value="https://YOUR-APP-NAME.up.railway.app") 
        ttk.Entry(grid_conf, textvariable=self.url_var, width=40).grid(row=0, column=1, padx=5)
        
        ttk.Label(grid_conf, text="Admin Username:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.user_var = tk.StringVar()
        ttk.Entry(grid_conf, textvariable=self.user_var, width=20).grid(row=0, column=3, padx=5)
        
        ttk.Label(grid_conf, text="Admin Password:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.pass_var = tk.StringVar()
        ttk.Entry(grid_conf, textvariable=self.pass_var, show="*", width=20).grid(row=0, column=5, padx=5)

        # --- 2. Excel Selection ---
        file_frame = ttk.LabelFrame(main_frame, text="2. Load Excel File", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        h_frame = ttk.Frame(file_frame)
        h_frame.pack(fill=tk.X)
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(h_frame, textvariable=self.file_path_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(h_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT, padx=5)
        
        # Sheet Selection
        ttk.Label(h_frame, text="Sheet:").pack(side=tk.LEFT, padx=(15, 5))
        self.sheet_combo = ttk.Combobox(h_frame, state="readonly", width=20)
        self.sheet_combo.pack(side=tk.LEFT)
        ttk.Button(h_frame, text="Load Data", command=self.load_sheet).pack(side=tk.LEFT, padx=5)

        # --- 3. Column Mapping ---
        map_frame = ttk.LabelFrame(main_frame, text="3. Map Columns", padding="10")
        map_frame.pack(fill=tk.X, pady=5)
        
        grid_map = ttk.Frame(map_frame)
        grid_map.pack(fill=tk.X)
        
        # Stock Ref
        ttk.Label(grid_map, text="Stock Ref (Name):", style="Bold.TLabel").grid(row=0, column=0, padx=5, pady=5)
        self.col_ref = ttk.Combobox(grid_map, state="readonly", width=25)
        self.col_ref.grid(row=0, column=1, padx=5)
        
        # Description
        ttk.Label(grid_map, text="Description:", style="Bold.TLabel").grid(row=0, column=2, padx=5, pady=5)
        self.col_desc = ttk.Combobox(grid_map, state="readonly", width=25)
        self.col_desc.grid(row=0, column=3, padx=5)
        
        # Price
        ttk.Label(grid_map, text="Price (GBP):", style="Bold.TLabel").grid(row=0, column=4, padx=5, pady=5)
        self.col_price = ttk.Combobox(grid_map, state="readonly", width=25)
        self.col_price.grid(row=0, column=5, padx=5)

        # --- 4. Preview ---
        prev_frame = ttk.LabelFrame(main_frame, text="4. Data Preview (First 50 Rows)", padding="10")
        prev_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.txt_preview = scrolledtext.ScrolledText(prev_frame, height=10, width=80)
        self.txt_preview.pack(fill=tk.BOTH, expand=True)

        # --- 5. Action ---
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X)
        
        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(action_frame, textvariable=self.status_var, foreground="blue").pack(side=tk.LEFT)
        
        self.btn_upload = ttk.Button(action_frame, text="UPLOAD TO WEBSITE", command=self.start_upload_thread)
        self.btn_upload.pack(side=tk.RIGHT)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if filename:
            self.excel_file = filename
            self.file_path_var.set(filename)
            try:
                xl = pd.ExcelFile(filename)
                self.sheet_names = xl.sheet_names
                self.sheet_combo['values'] = self.sheet_names
                if self.sheet_names:
                    self.sheet_combo.current(0)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_sheet(self):
        if not self.excel_file: return
        sheet = self.sheet_combo.get()
        try:
            self.df = pd.read_excel(self.excel_file, sheet_name=sheet)
            cols = list(self.df.columns)
            
            # Update mapping dropdowns
            for combo in [self.col_ref, self.col_desc, self.col_price]:
                combo['values'] = cols
            
            # Auto-guess columns
            self._auto_map_columns(cols)
            self._update_preview()
            self.status_var.set(f"Loaded {len(self.df)} rows.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sheet: {e}")

    def _auto_map_columns(self, cols):
        cols_lower = [str(c).lower() for c in cols]
        
        # Helpers
        def find_col(keywords):
            for i, c in enumerate(cols_lower):
                if any(k in c for k in keywords):
                    return cols[i]
            return ""

        self.col_ref.set(find_col(['stock_ref', 'reference', 'part no']))
        self.col_desc.set(find_col(['desc', 'details']))
        self.col_price.set(find_col(['sales', 'price', 'gbp', 'cost']))

    def _update_preview(self):
        self.txt_preview.delete(1.0, tk.END)
        if self.df is not None:
            self.txt_preview.insert(tk.END, self.df.head(50).to_string())

    def start_upload_thread(self):
        threading.Thread(target=self.upload_data, daemon=True).start()

    def upload_data(self):
        # 1. Validation
        url = self.url_var.get().strip().rstrip("/")
        username = self.user_var.get().strip()
        password = self.pass_var.get().strip()
        
        if not all([url, username, password]):
            messagebox.showwarning("Config Error", "Please fill in URL, Username and Password")
            return

        ref_col = self.col_ref.get()
        price_col = self.col_price.get()
        desc_col = self.col_desc.get()

        if not all([ref_col, price_col]):
            messagebox.showwarning("Mapping Error", "Stock Ref and Price columns are required.")
            return

        self.btn_upload.config(state="disabled")
        self.status_var.set("Preparing data...")

        # 2. Prepare JSON Payload
        products = []
        try:
            count = 0
            for _, row in self.df.iterrows():
                ref = str(row[ref_col]).strip()
                if not ref or ref.lower() == 'nan': continue
                
                # Price clean up
                try:
                    price = float(row[price_col])
                except:
                    price = 0.0
                
                desc = str(row[desc_col]).strip() if desc_col and pd.notna(row[desc_col]) else ""

                products.append({
                    "name": ref,
                    "price": price,
                    "description": desc
                })
                count += 1

            # 3. Send to Server
            self.status_var.set(f"Sending {count} items to {url}...")
            
            endpoint = f"{url}/api/import-stock/"
            payload = {
                "username": username,
                "password": password,
                "products": products
            }

            response = requests.post(endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                res_json = response.json()
                msg = f"Success!\nCreated: {res_json.get('created')}\nUpdated: {res_json.get('updated')}"
                messagebox.showinfo("Upload Complete", msg)
                self.status_var.set("Upload successful.")
            else:
                try:
                    err_msg = response.json().get('message', response.text)
                except:
                    err_msg = response.text
                messagebox.showerror("Server Error", f"Server rejected request:\n{err_msg}")
                self.status_var.set("Upload failed.")

        except Exception as e:
            messagebox.showerror("Error", f"Connection failed:\n{str(e)}")
            self.status_var.set("Connection error.")
        finally:
            self.btn_upload.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteStockImporter(root)
    root.mainloop()