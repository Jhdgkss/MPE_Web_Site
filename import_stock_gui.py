"""
GUI Application for importing stock data from Excel into the shop database.

Features:
- File browser to select Excel file
- Sheet selection
- Column mapping
- Stock type filtering based on stock code
- Data preview
- Database backup before import
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

try:
    import django
    import pandas as pd
    django.setup()
except ImportError as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Missing Libraries", f"Could not load Django environment.\n\nError: {e}\n\nPlease install requirements:\npip install django pandas openpyxl requests dj-database-url whitenoise cloudinary django-cloudinary-storage django-import-export")
    messagebox.showerror("Missing Libraries", f"Could not load required libraries (Django, Pandas).\n\nError: {e}\n\nPlease install requirements:\npip install django pandas openpyxl requests")
    sys.exit(1)

from django.conf import settings
from django.db import transaction
from core.models import ShopProduct


class StockImportGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MPE Stock Import Tool")
        self.root.geometry("900x700")
        
        self.excel_file = None
        self.sheet_name = None
        self.df = None
        self.available_sheets = []
        
        # Column mappings
        self.column_mappings = {
            'Stock_Ref': None,
            'Description': None,
            'cost price': None,
            'Stock Code': None  # For filtering
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the GUI interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="MPE Stock Import Tool", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # File Selection Section
        file_frame = ttk.LabelFrame(main_frame, text="1. Select Excel File", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=60, state='readonly').grid(row=0, column=0, padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).grid(row=0, column=1, padx=5)
        
        # Sheet Selection Section
        sheet_frame = ttk.LabelFrame(main_frame, text="2. Select Sheet", padding="10")
        sheet_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.sheet_var = tk.StringVar()
        self.sheet_combo = ttk.Combobox(sheet_frame, textvariable=self.sheet_var, 
                                       state='readonly', width=50)
        self.sheet_combo.grid(row=0, column=0, padx=5)
        self.sheet_combo.bind('<<ComboboxSelected>>', self.on_sheet_selected)
        ttk.Button(sheet_frame, text="Load Sheet", command=self.load_sheet).grid(row=0, column=1, padx=5)
        
        # Header row selection
        ttk.Label(sheet_frame, text="Header row (0 = first row):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.header_row_var = tk.StringVar(value="0")
        header_row_spin = ttk.Spinbox(sheet_frame, from_=0, to=10, textvariable=self.header_row_var, width=10)
        header_row_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Column Mapping Section
        mapping_frame = ttk.LabelFrame(main_frame, text="3. Map Columns", padding="10")
        mapping_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Stock Reference
        ttk.Label(mapping_frame, text="Stock Reference:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.stock_ref_var = tk.StringVar()
        self.stock_ref_combo = ttk.Combobox(mapping_frame, textvariable=self.stock_ref_var, 
                                           state='readonly', width=30)
        self.stock_ref_combo.grid(row=0, column=1, padx=5, pady=2)
        self.stock_ref_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        # Description
        ttk.Label(mapping_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.description_var = tk.StringVar()
        self.description_combo = ttk.Combobox(mapping_frame, textvariable=self.description_var, 
                                              state='readonly', width=30)
        self.description_combo.grid(row=1, column=1, padx=5, pady=2)
        self.description_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        # Sales Price
        ttk.Label(mapping_frame, text="Sales Price:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.price_var = tk.StringVar()
        self.price_combo = ttk.Combobox(mapping_frame, textvariable=self.price_var, 
                                       state='readonly', width=30)
        self.price_combo.grid(row=2, column=1, padx=5, pady=2)
        self.price_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        # Stock Code (for filtering)
        ttk.Label(mapping_frame, text="Stock Code (for filtering):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.stock_code_var = tk.StringVar()
        self.stock_code_combo = ttk.Combobox(mapping_frame, textvariable=self.stock_code_var, 
                                            state='readonly', width=30)
        self.stock_code_combo.grid(row=3, column=1, padx=5, pady=2)
        self.stock_code_combo.bind('<<ComboboxSelected>>', lambda e: [self.load_stock_types(), self.update_preview()])
        
        # Stock Type Filter Section
        filter_frame = ttk.LabelFrame(main_frame, text="4. Filter by Stock Type", padding="10")
        filter_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(filter_frame, text="Select stock types to import:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.stock_types_var = tk.StringVar(value="All")
        self.stock_types_listbox = tk.Listbox(filter_frame, selectmode=tk.MULTIPLE, height=6, width=40)
        self.stock_types_listbox.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.stock_types_listbox.bind('<<ListboxSelect>>', lambda e: self.update_preview())
        
        scrollbar = ttk.Scrollbar(filter_frame, orient=tk.VERTICAL, command=self.stock_types_listbox.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.stock_types_listbox.config(yscrollcommand=scrollbar.set)
        
        ttk.Button(filter_frame, text="Select All", command=self.select_all_types).grid(row=2, column=0, pady=5)
        ttk.Button(filter_frame, text="Deselect All", command=self.deselect_all_types).grid(row=2, column=1, pady=5)
        
        # Preview Section
        preview_frame = ttk.LabelFrame(main_frame, text="5. Preview Data", padding="10")
        preview_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(5, weight=1)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=10, width=80)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        # 6. Import Destination Section
        dest_frame = ttk.LabelFrame(main_frame, text="6. Import Destination", padding="10")
        dest_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.import_mode = tk.StringVar(value="local")
        
        # Mode Selection
        ttk.Radiobutton(dest_frame, text="Local Database (Development)", variable=self.import_mode, value="local", command=self.toggle_inputs).grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Radiobutton(dest_frame, text="Live Website (via API)", variable=self.import_mode, value="api", command=self.toggle_inputs).grid(row=0, column=1, padx=5, sticky=tk.W)

        # API Fields
        self.api_frame = ttk.Frame(dest_frame)
        self.api_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.api_frame, text="URL:").grid(row=0, column=0, padx=5)
        self.url_var = tk.StringVar(value="https://mpewebsite-production.up.railway.app/api/import-stock/")
        self.url_entry = ttk.Entry(self.api_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=3, sticky=tk.W, padx=5)
        
        ttk.Label(self.api_frame, text="User:").grid(row=1, column=0, padx=5)
        self.user_var = tk.StringVar()
        ttk.Entry(self.api_frame, textvariable=self.user_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(self.api_frame, text="Pass:").grid(row=1, column=2, padx=5)
        self.pass_var = tk.StringVar()
        ttk.Entry(self.api_frame, textvariable=self.pass_var, show="*", width=15).grid(row=1, column=3, sticky=tk.W, padx=5)

        # Local Options
        self.local_opts_frame = ttk.Frame(dest_frame)
        self.local_opts_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.local_opts_frame, text="Backup local DB first", variable=self.backup_var).grid(row=0, column=0, padx=5)
        self.update_existing_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.local_opts_frame, text="Update existing products", variable=self.update_existing_var).grid(row=0, column=1, padx=5)

        # Import Button
        ttk.Button(main_frame, text="Start Import", command=self.import_stock, style='Accent.TButton').grid(row=7, column=0, columnspan=2, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Please select an Excel file")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.toggle_inputs()

    def toggle_inputs(self):
        """Enable/Disable fields based on mode"""
        if self.import_mode.get() == "api":
            for child in self.api_frame.winfo_children(): child.configure(state='normal')
            for child in self.local_opts_frame.winfo_children(): child.configure(state='disabled')
        else:
            for child in self.api_frame.winfo_children(): child.configure(state='disabled')
            for child in self.local_opts_frame.winfo_children(): child.configure(state='normal')
        
    def browse_file(self):
        """Open file dialog to select Excel file"""
        filename = filedialog.askopenfilename(
            title='Select Excel File',
            filetypes=[
                ('Excel files', '*.xlsx *.xls'),
                ('All files', '*.*')
            ]
        )
        
        if filename:
            self.excel_file = filename
            self.file_path_var.set(filename)
            self.load_sheets()
            self.status_var.set(f"File loaded: {os.path.basename(filename)}")
    
    def load_sheets(self):
        """Load available sheets from Excel file"""
        if not self.excel_file:
            return
        
        try:
            import pandas as pd
            xl_file = pd.ExcelFile(self.excel_file)
            self.available_sheets = xl_file.sheet_names
            self.sheet_combo['values'] = self.available_sheets
            
            # Try to find "MPE STOCK LIST" sheet and select it
            mpe_sheet_found = False
            for i, sheet in enumerate(self.available_sheets):
                if 'MPE STOCK LIST' in sheet.upper() or 'MPE STOCK' in sheet.upper():
                    self.sheet_combo.current(i)
                    self.sheet_var.set(sheet)
                    mpe_sheet_found = True
                    break
            
            if not mpe_sheet_found and self.available_sheets:
                self.sheet_combo.current(0)
            
            if mpe_sheet_found:
                self.status_var.set(f"Found {len(self.available_sheets)} sheet(s) - Selected: MPE STOCK LIST")
            else:
                self.status_var.set(f"Found {len(self.available_sheets)} sheet(s) - Please select 'MPE STOCK LIST'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read Excel file:\n{e}")
            self.status_var.set("Error loading file")
    
    def on_sheet_selected(self, event=None):
        """Handle sheet selection"""
        self.sheet_name = self.sheet_var.get()
    
    def load_sheet(self):
        """Load the selected sheet and populate column mappings"""
        if not self.excel_file:
            messagebox.showwarning("Warning", "Please select an Excel file first")
            return
        
        self.sheet_name = self.sheet_var.get()
        if not self.sheet_name:
            messagebox.showwarning("Warning", "Please select a sheet")
            return
        
        try:
            import pandas as pd
            
            # Get header row number
            try:
                header_row = int(self.header_row_var.get())
            except:
                header_row = 0
            
            # Try to read with header row
            self.df = pd.read_excel(self.excel_file, sheet_name=self.sheet_name, header=header_row)
            
            # Check if we have "Unnamed" columns - this means headers weren't found
            columns = list(self.df.columns)
            has_unnamed = any('Unnamed' in str(col) for col in columns)
            
            if has_unnamed:
                # Try to find the actual header row by checking first few rows
                temp_df = pd.read_excel(self.excel_file, sheet_name=self.sheet_name, header=None, nrows=5)
                
                # Look for row with "Stock Reference" or "Description" or "Sales Price"
                header_row_found = None
                for idx in range(min(5, len(temp_df))):
                    row_values = [str(val).lower().strip() for val in temp_df.iloc[idx].values]
                    if any('stock reference' in val or 'stock_ref' in val for val in row_values):
                        if any('description' in val for val in row_values):
                            if any('sales' in val and 'price_gbp' in val for val in row_values):
                                header_row_found = idx
                                break
                
                if header_row_found is not None:
                    # Re-read with correct header row
                    self.df = pd.read_excel(self.excel_file, sheet_name=self.sheet_name, header=header_row_found)
                    self.header_row_var.set(str(header_row_found))
                    columns = list(self.df.columns)
                    self.status_var.set(f"✓ Auto-detected header row: {header_row_found + 1}")
                else:
                    # Still have unnamed columns - try to use first row as headers manually
                    temp_df = pd.read_excel(self.excel_file, sheet_name=self.sheet_name, header=None, nrows=1)
                    if len(temp_df.columns) > 0:
                        # Use first row as column names
                        new_columns = [str(val).strip() if pd.notna(val) else f'Column_{i}' 
                                      for i, val in enumerate(temp_df.iloc[0].values)]
                        self.df = pd.read_excel(self.excel_file, sheet_name=self.sheet_name, header=0)
                        self.df.columns = new_columns[:len(self.df.columns)]
                        columns = list(self.df.columns)
                        self.status_var.set("✓ Used first row as headers")
            
            # Get available columns
            columns = list(self.df.columns)
            
            # Populate column combo boxes
            self.stock_ref_combo['values'] = columns
            self.description_combo['values'] = columns
            self.price_combo['values'] = columns
            self.stock_code_combo['values'] = ['None'] + columns
            
            # Try to auto-detect columns (more aggressive matching)
            for col in columns:
                col_lower = str(col).lower().strip()
                col_exact = str(col).strip()
                
                # Stock Reference - try exact match first, then partial
                if not self.stock_ref_var.get():
                    if 'stock reference' in col_lower or col_exact == 'Stock Reference' or 'stock_ref' in col_lower:
                        self.stock_ref_var.set(col)
                
                # Description - try exact match first
                if not self.description_var.get():
                    if col_lower == 'description' or col_exact == 'Description':
                        self.description_var.set(col)
                
                # Sales Price - try exact match first
                if not self.price_var.get():
                    if col_lower == 'sales price' or col_exact == 'Sales Price' or ('sales' in col_lower and 'price_gbp' in col_lower):
                        self.price_var.set(col)
                
                # Stock Code - for filtering
                if not self.stock_code_var.get() or self.stock_code_var.get() == 'None':
                    if col_lower == 'stock code' or col_exact == 'Stock Code' or ('stock' in col_lower and 'code' in col_lower):
                        self.stock_code_var.set(col)
            
            # If still not found, try more flexible matching
            if not self.stock_ref_var.get():
                for col in columns:
                    col_lower = str(col).lower()
                    if ('stock' in col_lower and 'ref' in col_lower) or ('reference' in col_lower):
                        self.stock_ref_var.set(col)
                        break
            
            if not self.description_var.get():
                for col in columns:
                    col_lower = str(col).lower()
                    if 'desc' in col_lower or 'detail' in col_lower:
                        self.description_var.set(col)
                        break
            
            if not self.price_var.get():
                for col in columns:
                    col_lower = str(col).lower()
                    if 'sales' in col_lower and 'price_gbp' in col_lower:
                        self.price_var.set(col)
                        break
                # Fallback to any price column if sales price not found
                if not self.price_var.get():
                    for col in columns:
                        col_lower = str(col).lower()
                        if 'price_gbp' in col_lower:
                            self.price_var.set(col)
                            break
            
            # Load stock types if stock code column is available
            self.load_stock_types()
            
            # Show preview
            self.update_preview()
            
            # Check if all required columns are mapped
            if self.stock_ref_var.get() and self.description_var.get() and self.price_var.get():
                self.status_var.set(f"✓ Loaded {len(self.df)} rows - All columns auto-mapped! Ready to import.")
            else:
                missing = []
                if not self.stock_ref_var.get():
                    missing.append("Stock Reference")
                if not self.description_var.get():
                    missing.append("Description")
                if not self.price_var.get():
                    missing.append("Sales Price")
                self.status_var.set(f"⚠ Loaded {len(self.df)} rows - Please map: {', '.join(missing)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sheet:\n{e}")
            self.status_var.set("Error loading sheet")
    
    def load_stock_types(self):
        """Load unique stock types from stock code column"""
        if self.df is None:
            return
        
        stock_code_col = self.stock_code_var.get()
        if not stock_code_col or stock_code_col == 'None':
            self.stock_types_listbox.delete(0, tk.END)
            self.stock_types_listbox.insert(0, "All (no filter)")
            return
        
        try:
            # Get unique values from stock code column
            unique_codes = self.df[stock_code_col].dropna().unique()
            unique_codes = sorted([str(code).strip() for code in unique_codes if str(code).strip()])
            
            self.stock_types_listbox.delete(0, tk.END)
            for code in unique_codes:
                self.stock_types_listbox.insert(tk.END, code)
            
            # Select all by default
            for i in range(len(unique_codes)):
                self.stock_types_listbox.selection_set(i)
            
            self.status_var.set(f"Found {len(unique_codes)} unique stock types")
            
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not load stock types:\n{e}")
    
    def select_all_types(self):
        """Select all stock types"""
        self.stock_types_listbox.selection_set(0, tk.END)
    
    def deselect_all_types(self):
        """Deselect all stock types"""
        self.stock_types_listbox.selection_clear(0, tk.END)
    
    def update_preview(self):
        """Update the preview text with sample data"""
        if self.df is None:
            self.preview_text.delete(1.0, tk.END)
            return
        
        # Get selected stock types
        selected_types = [self.stock_types_listbox.get(i) for i in self.stock_types_listbox.curselection()]
        
        # Filter data
        filtered_df = self.df.copy()
        
        stock_code_col = self.stock_code_var.get()
        if stock_code_col and stock_code_col != 'None' and selected_types:
            if "All (no filter)" not in selected_types:
                filtered_df = filtered_df[filtered_df[stock_code_col].astype(str).isin(selected_types)]
        
        # Get column mappings
        stock_ref_col = self.stock_ref_var.get()
        desc_col = self.description_var.get()
        price_col = self.price_var.get()
        
        # Show preview
        preview_text = f"Preview: {len(filtered_df)} rows will be imported\n"
        preview_text += "=" * 80 + "\n\n"
        
        if stock_ref_col and desc_col and price_col:
            # Show first 10 rows
            for idx, row in filtered_df.head(10).iterrows():
                stock_ref = str(row.get(stock_ref_col, '')).strip()
                desc = str(row.get(desc_col, '')).strip()[:50]  # Truncate description
                price = row.get(price_col, 0)
                try:
                    price = f"£{float(price):.2f}"
                except:
                    price = "N/A"
                
                preview_text += f"{stock_ref:20} | {desc:50} | {price:10}\n"
            
            if len(filtered_df) > 10:
                preview_text += f"\n... and {len(filtered_df) - 10} more rows\n"
        else:
            preview_text += "Please map all required columns to see preview\n"
        
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview_text)
    
    def backup_database(self):
        """Create a timestamped backup of the database"""
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            return None
        
        backups_dir = Path(settings.BASE_DIR) / 'backups'
        backups_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'db_backup_{timestamp}.sqlite3'
        backup_path = backups_dir / backup_filename
        
        try:
            shutil.copy2(db_path, backup_path)
            return str(backup_path)
        except Exception as e:
            raise Exception(f'Failed to backup database: {e}')
    
    def import_stock(self):
        """Import stock data into database"""
        # Validate inputs
        if not self.excel_file or self.df is None:
            messagebox.showwarning("Warning", "Please load an Excel file and sheet first")
            return
        
        stock_ref_col = self.stock_ref_var.get()
        desc_col = self.description_var.get()
        price_col = self.price_var.get()
        
        if not all([stock_ref_col, desc_col, price_col]):
            messagebox.showwarning("Warning", "Please map all required columns (Stock Reference, Description, Sales Price)")
            return
        
        # Get selected stock types
        selected_types = [self.stock_types_listbox.get(i) for i in self.stock_types_listbox.curselection()]
        stock_code_col = self.stock_code_var.get()
        
        # Filter data
        filtered_df = self.df.copy()
        
        if stock_code_col and stock_code_col != 'None' and selected_types:
            if "All (no filter)" not in selected_types:
                filtered_df = filtered_df[filtered_df[stock_code_col].astype(str).isin(selected_types)]
        
        if len(filtered_df) == 0:
            messagebox.showwarning("Warning", "No rows match the selected filters")
            return
            
        # --- API IMPORT PATH ---
        if self.import_mode.get() == "api":
            self.run_api_import(filtered_df, stock_ref_col, desc_col, price_col)
            return
        
        # Confirm import
        result = messagebox.askyesno(
            "Confirm Import",
            f"Import {len(filtered_df)} products into the database?\n\n"
            f"Stock Reference: {stock_ref_col}\n"
            f"Description: {desc_col}\n"
            f"Sales Price: {price_col}\n"
            f"Update existing: {'Yes' if self.update_existing_var.get() else 'No'}"
        )
        
        if not result:
            return
        
        # Backup database
        if self.backup_var.get():
            try:
                backup_path = self.backup_database()
                self.status_var.set(f"Backed up database to: {os.path.basename(backup_path)}")
                self.root.update()
            except Exception as e:
                if not messagebox.askyesno("Backup Failed", 
                    f"Failed to backup database:\n{e}\n\nContinue anyway?"):
                    return
        
        # Import data
        try:
            import pandas as pd
            
            created_count = 0
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            self.status_var.set("Importing...")
            self.root.update()
            
            with transaction.atomic():
                for index, row in filtered_df.iterrows():
                    try:
                        stock_ref = str(row[stock_ref_col]).strip()
                        description = str(row[desc_col]).strip() if pd.notna(row[desc_col]) else ''
                        cost_price = row[price_col]
                        
                        # Skip if Stock_Ref is empty
                        if not stock_ref or stock_ref == 'nan':
                            skipped_count += 1
                            continue
                        
                        # Validate and convert price
                        try:
                            if pd.isna(cost_price):
                                price = 0.00
                            else:
                                price = float(cost_price)
                                if price < 0:
                                    price = 0.00
                        except (ValueError, TypeError):
                            price = 0.00
                        
                        # Create or update product
                        if self.update_existing_var.get():
                            product, created = ShopProduct.objects.update_or_create(
                                name=stock_ref,
                                defaults={
                                    'description': description,
                                    'price_gbp': price,
                                    'stock_status': 'In Stock',
                                }
                            )
                            if created:
                                created_count += 1
                            else:
                                updated_count += 1
                        else:
                            product, created = ShopProduct.objects.get_or_create(
                                name=stock_ref,
                                defaults={
                                    'description': description,
                                    'price_gbp': price,
                                    'stock_status': 'In Stock',
                                }
                            )
                            if created:
                                created_count += 1
                            else:
                                skipped_count += 1
                    
                    except Exception as e:
                        error_count += 1
                        print(f"Error processing row {index}: {e}")
            
            # Show summary
            summary = (
                f"Import Complete!\n\n"
                f"Created: {created_count}\n"
                f"{'Updated: ' + str(updated_count) if self.update_existing_var.get() else ''}\n"
                f"Skipped: {skipped_count}\n"
                f"{'Errors: ' + str(error_count) if error_count > 0 else ''}"
            )
            
            messagebox.showinfo("Import Complete", summary)
            self.status_var.set(f"Import complete: {created_count} created, {skipped_count} skipped")
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import data:\n{e}")
            self.status_var.set("Import failed")
            import traceback
            traceback.print_exc()

    def run_api_import(self, df, ref_col, desc_col, price_col):
        """Send data to the live website API using the requests library."""
        url = self.url_var.get().strip()
        username = self.user_var.get().strip()
        password = self.pass_var.get().strip()

        if not url or not username or not password:
            messagebox.showwarning("Missing Info", "URL, Username, and Password are required for API import.")
            return

        if not messagebox.askyesno("Confirm API Upload", f"Upload {len(df)} items to {url}?"):
            return

        try:
            import pandas as pd
            import requests  # Use requests library
            import json

            products = []
            for _, row in df.iterrows():
                price = row[price_col]
                try:
                    price = float(price) if pd.notna(price) else 0.0
                except (ValueError, TypeError):
                    price = 0.0

                products.append({
                    "name": str(row[ref_col]).strip(),
                    "description": str(row[desc_col]).strip() if pd.notna(row[desc_col]) else "",
                    "price": price,
                })

            payload = {"username": username, "password": password, "products": products}

            self.status_var.set("Uploading to website...")
            self.root.update()

            # Use requests.post for a simpler API call
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

            res_json = response.json()

            if res_json.get("status") == "success":
                msg = f"Success!\nCreated: {res_json.get('created')}\nUpdated: {res_json.get('updated')}"
                messagebox.showinfo("API Import", msg)
                self.status_var.set("API Import Successful")
            else:
                # The API returned a 200 OK but with a logical error
                raise Exception(res_json.get("message", "API returned a success status with an error message."))

        except requests.exceptions.RequestException as e:
            # Catches connection errors, timeouts, etc.
            error_message = str(e)
            # Try to get more specific error from response if available
            if e.response is not None:
                try:
                    error_detail = e.response.json().get("message", e.response.text)
                    error_message = f"Server responded with {e.response.status_code}: {error_detail}"
                except json.JSONDecodeError:
                    error_message = f"Server responded with {e.response.status_code}: {e.response.text}"

            messagebox.showerror("API Error", f"Failed to upload:\n{error_message}")
            self.status_var.set("API Upload Failed")
        except Exception as e:
            # Catches other errors like JSON parsing from a successful response
            messagebox.showerror("API Error", f"An unexpected error occurred:\n{e}")
            self.status_var.set("API Upload Failed")

def main():
    # Import pandas here to avoid issues if not installed
    try:
        import pandas as pd
    except ImportError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", "pandas is required. Please install: pip install pandas openpyxl")
        sys.exit(1)
    
    root = tk.Tk()
    app = StockImportGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
