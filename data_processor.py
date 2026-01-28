import pandas as pd
import re
import os

class DataProcessor:
    def __init__(self):
        self.df = pd.DataFrame()
        self.sheet_meta = {}

    def normalize_plate(self, s):
        if not s or pd.isna(s):
            return ""
        return re.sub(r'[^A-Z0-9]', '', str(s).upper())

    def is_vehicle_plate(self, s):
        p = self.normalize_plate(s)
        if len(p) != 7:
            return False
        return bool(re.match(r'^[A-Z]{3}[A-Z0-9]{4}$', p))

    def load_excel(self, file_path, progress_callback=None):
        try:
            print(f"Iniciando carregamento: {file_path}")
            ext = os.path.splitext(file_path)[-1].lower()
            
            # Seleciona o motor correto baseado na extensão
            engine = 'openpyxl'
            if ext == '.xls':
                engine = 'xlrd'
            elif ext == '.xlsb':
                engine = 'pyxlsb'
            
            xl = pd.ExcelFile(file_path, engine=engine)
            all_rows = []
            sheet_names = xl.sheet_names
            print(f"Motor: {engine} | Abas: {sheet_names}")
            
            for i, sheet_name in enumerate(sheet_names):
                print(f"Processando aba: {sheet_name}")
                if progress_callback:
                    progress_callback(i / len(sheet_names), f"Lendo aba: {sheet_name}")
                
                # Carregar os dados brutos de forma rápida
                df_sheet = pd.read_excel(xl, sheet_name=sheet_name, header=None)
                if df_sheet.empty:
                    print(f"Aba {sheet_name} está vazia.")
                    continue

                print(f"Aba {sheet_name} carregada: {df_sheet.shape[0]} linhas.")

                # Identificar cabeçalho e coluna de placa
                best_col = -1
                header_row = 0
                max_plates = 0
                
                # Scan top 100 rows for plate density
                sample_rows = min(len(df_sheet), 100)
                for c in range(df_sheet.shape[1]):
                    plates_count = df_sheet.iloc[:sample_rows, c].apply(self.is_vehicle_plate).sum()
                    if plates_count > max_plates:
                        max_plates = plates_count
                        best_col = c
                
                # Se não achou na densidade, busca por nomes de coluna comuns
                if best_col == -1:
                    for r in range(min(len(df_sheet), 10)):
                        row_vals = [str(x).lower() for x in df_sheet.iloc[r] if pd.notna(x)]
                        if any("placa" in v for v in row_vals):
                            header_row = r
                            for c, val in enumerate(df_sheet.iloc[r]):
                                if pd.notna(val) and "placa" in str(val).lower():
                                    best_col = c
                                    break
                            break

                # Se ainda não achou, faz varredura global na folha (Otimizada)
                if best_col == -1:
                    print(f"Iniciando varredura global na aba {sheet_name}...")
                    # Otimização: Só verifica células que têm strings e tamanho compatível
                    def check_any_plate(row):
                        for val in row:
                            if self.is_vehicle_plate(val):
                                return True
                        return False
                    
                    # Filtra apenas linhas que podem ter placa (rápido)
                    possible_rows_mask = df_sheet.apply(check_any_plate, axis=1)
                    plate_rows = df_sheet[possible_rows_mask].copy()
                else:
                    # Se achou a coluna, filtra apenas linhas que tenham placa naquela coluna
                    print(f"Coluna de placa detectada: {best_col}")
                    plate_rows_mask = df_sheet[best_col].apply(self.is_vehicle_plate)
                    plate_rows = df_sheet[plate_rows_mask].copy()

                # Processar dados encontrados
                if not plate_rows.empty:
                    print(f"Registros encontrados na aba {sheet_name}: {len(plate_rows)}")
                    
                    def extract_plate_info(row):
                        # Se temos o best_col, tenta ele primeiro
                        if best_col != -1 and self.is_vehicle_plate(row[best_col]):
                            return str(row[best_col]).upper(), self.normalize_plate(row[best_col])
                        # Caso contrário, varre a linha
                        for val in row:
                            if self.is_vehicle_plate(val):
                                return str(val).upper(), self.normalize_plate(val)
                        return None, None

                    plate_info = plate_rows.apply(extract_plate_info, axis=1)
                    plate_rows['plate_raw'] = plate_info.apply(lambda x: x[0])
                    plate_rows['plate_norm'] = plate_info.apply(lambda x: x[1])
                    plate_rows['sheet_name'] = sheet_name
                    plate_rows['row_index'] = plate_rows.index + 1
                    
                    all_rows.append(plate_rows)

            if all_rows:
                self.df = pd.concat(all_rows, ignore_index=True)
                return len(self.df)
            return 0
        except Exception as e:
            print(f"Erro ao carregar: {e}")
            raise e

    def search(self, query):
        if self.df.empty:
            return pd.DataFrame()
        
        q = self.normalize_plate(query)
        if not q:
            return self.df.head(300)
        
        # Busca exata ou que começa com
        results = self.df[
            self.df['plate_norm'].str.startswith(q) | 
            self.df['plate_raw'].str.contains(query.upper(), na=False)
        ]
        return results
