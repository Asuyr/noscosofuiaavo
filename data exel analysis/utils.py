import pandas as pd
import io
import csv


def detect_separator(file_buffer):
    """
    Tenta di rilevare il separatore di un file CSV.
    """
    try:
        sample = file_buffer.read(4096).decode('utf-8', errors='ignore')
        file_buffer.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=[',', ';', '\t', '|'])
        return dialect.delimiter
    except Exception:
        file_buffer.seek(0)
        return None

def find_header_row(file, separator, encoding):
    """
    Cerca la riga di intestazione corretta nelle prime 20 righe.
    La riga corretta è quella con il maggior numero di colonne valide (stringhe, non vuote).
    """
    try:
        # Legge le prime righe senza header
        file.seek(0)
        preview_df = pd.read_csv(file, sep=separator, encoding=encoding, header=None, nrows=20, engine='python')
        
        best_header_row = 0
        max_valid_cols = 0
        
        for i, row in preview_df.iterrows():
            # Conta quanti valori nella riga sono stringhe non vuote e non numeri puri
            # Un header tipico ha stringhe descrittive
            valid_cols = row.apply(lambda x: isinstance(x, str) and len(str(x).strip()) > 0 and not str(x).replace('.','').isdigit()).sum()
            
            # Penalizza righe con molti NaN
            na_count = row.isna().sum()
            score = valid_cols - (na_count * 0.5)
            
            if score > max_valid_cols:
                max_valid_cols = score
                best_header_row = i
                
        return best_header_row
    except Exception:
        return 0 # Fallback alla prima riga

def clean_dataframe(df):
    """
    Pulisce il DataFrame rimuovendo colonne e righe spazzatura.
    """
    # 1. Rimuove righe e colonne completamente vuote
    df = df.dropna(how='all', axis=0)
    df = df.dropna(how='all', axis=1)
    
    # 2. Pulisce i nomi delle colonne
    # Rimuove spazi extra dai nomi
    df.columns = df.columns.astype(str).str.strip()
    
    # 3. Gestione colonne "Unnamed"
    # Se una colonna si chiama "Unnamed" e contiene dati, proviamo a rinominarla o tenerla
    # Se è quasi vuota, la buttiamo
    cols_to_drop = []
    for col in df.columns:
        if "Unnamed" in col or col == "nan":
            # Conta valori non nulli
            non_null_count = df[col].count()
            if non_null_count < (len(df) * 0.1): # Se meno del 10% è pieno, maiali
                cols_to_drop.append(col)
            else:
                # Se ha dati, rinominiamola in modo generico ma utile
                new_name = f"Colonna_{df.columns.get_loc(col)}"
                df.rename(columns={col: new_name}, inplace=True)
        elif len(col) == 0: # Nome vuoto
             new_name = f"Colonna_{df.columns.get_loc(col)}"
             df.rename(columns={col: new_name}, inplace=True)
             
    df.drop(columns=cols_to_drop, inplace=True)
    
    # 4. Pulisce dati numerici (valute, percentuali)
    df = clean_numeric_columns(df)
    
    return df

def clean_numeric_columns(df):
    """
    Converte colonne sporche (es. '1.000 €') in numeri.
    """
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                # Campione per testare conversione
                sample = df[col].dropna().astype(str).head(10)
                if sample.empty: continue
                
                # Check se sembra un numero con testo
                if sample.str.contains(r'\d').any():
                     # Rimuove simboli valuta e spazi
                    cleaned = df[col].astype(str).str.replace(r'[€$£%]', '', regex=True).str.replace(r'\s+', '', regex=True)
                    # Gestione del punto migliaia e virgola decimale (stile europeo)
                    # Se ci sono virgole e punti, assumiamo 1.000,00 -> togli punto, sostituisci virgola
                    if cleaned.str.contains(',').any() and cleaned.str.contains(r'\.').any():
                         cleaned = cleaned.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                    elif cleaned.str.contains(',').any(): # Solo virgola (es 10,5) -> diventa punto
                         cleaned = cleaned.str.replace(',', '.', regex=False)
                    
                    numeric_col = pd.to_numeric(cleaned, errors='coerce')
                    
                    # Se almeno il 70% dei dati è diventato numero valido, sostituiamo
                    if numeric_col.notna().sum() > (len(df) * 0.7):
                        df[col] = numeric_col
            except Exception:
                pass
    return df

def load_data(file, separator_manual=None, encoding_manual=None):
    """
    Carica dati con rilevamento automatico di header e struttura.
    """
    filename = file.name
    try:
        if filename.endswith('.csv'):
            file_content = io.BytesIO(file.getvalue()) # Copia per seek multipli
            
            encodings = [encoding_manual] if encoding_manual else ['utf-8', 'latin1', 'cp1252', 'ISO-8859-1']
            
            for encoding in encodings:
                try:
                    file_content.seek(0)
                    sep = separator_manual if separator_manual else detect_separator(file_content)
                    if not sep and not separator_manual: sep = ',' # Default
                    
                    # Trova la riga di header corretta
                    file_content.seek(0)
                    header_row = find_header_row(file_content, sep, encoding)
                    
                    # Carica
                    file_content.seek(0)
                    df = pd.read_csv(file_content, sep=sep, encoding=encoding, header=header_row)
                    
                    if df is not None and not df.empty:
                        return clean_dataframe(df)
                        
                except Exception:
                    continue # Prova prossimo encoding
            return None # Fallito

        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(file)
            return clean_dataframe(df)
        
        return None
    except Exception as e:
        print(f"Loading error: {e}")
        return None

def get_dataset_info(df):
    buffer = io.StringIO()
    df.info(buf=buffer)
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_values": df.isnull().sum().sum(),
        "info_string": buffer.getvalue()
    }

