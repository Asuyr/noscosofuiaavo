import streamlit as st

import plotly.express as px
from utils import load_data, get_dataset_info

# Configurazione Pagina
st.set_page_config(page_title="Analisi Dati Pro", page_icon="📊", layout="wide")

# CSS Personalizzato
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4B4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">📊 Strumento Analisi Dati</h1>', unsafe_allow_html=True)

    # Sidebar per caricamento file
    with st.sidebar:
        st.header("Upload Dati")
        uploaded_file = st.file_uploader("Carica il tuo file (CSV, Excel)", type=["csv", "xlsx", "xls"])
        
        st.info("Formati supportati: .csv, .xlsx")
        
        with st.expander("🔧 Opzioni Caricamento Avanzate"):
            st.markdown("Se il file non viene letto correttamente, prova a modificare queste opzioni.")
            sep_option = st.selectbox("Separatore CSV", ["Auto", "Virgola (,)", "Punto e virgola (;)", "Tab (\\t)", "Pipe (|)"])
            enc_option = st.selectbox("Encoding", ["Auto", "utf-8", "latin1", "ISO-8859-1"])
            
            # Mappa selezioni ai valori reali
            sep_map = {"Auto": None, "Virgola (,)": ",", "Punto e virgola (;)": ";", "Tab (\\t)": "\t", "Pipe (|)": "|"}
            enc_map = {"Auto": None, "utf-8": "utf-8", "latin1": "latin1", "ISO-8859-1": "ISO-8859-1"}
            
            selected_sep = sep_map[sep_option]
            selected_enc = enc_map[enc_option]

    if uploaded_file is not None:
        # Caricamento Dati
        with st.spinner('Caricamento ed elaborazione dati in corso...'):
            df = load_data(uploaded_file, separator_manual=selected_sep, encoding_manual=selected_enc)
        
        if df is not None:
            st.success("File caricato con successo!")
            
            # --- Sidebar: Filtri Rapidi ---
            st.sidebar.subheader("Filtri Rapidi")
            if st.sidebar.checkbox("Abilita Filtri"):
                filter_col = st.sidebar.selectbox("Filtra per colonna", df.columns)
                unique_values = df[filter_col].unique()
                selected_val = st.sidebar.multiselect(f"Valori per {filter_col}", unique_values, default=unique_values)
                df = df[df[filter_col].isin(selected_val)]
                st.sidebar.info(f"Righe filtrate: {len(df)}")

            # Layout a Tabs Aggiornato
            tab1, tab2, tab3, tab4 = st.tabs(["📄 Anteprima & Dati", "🔍 Analisi Avanzata", "📈 Visualizzazioni", "🧮 Aggregazioni"])
            
            with tab1:
                st.subheader("Anteprima del Dataset")
                st.dataframe(df.head())
                
                info = get_dataset_info(df)
                c1, c2, c3 = st.columns(3)
                c1.metric("Righe", info["rows"])
                c2.metric("Colonne", info["columns"])
                c3.metric("Valori Mancanti", info["missing_values"])
                
                with st.expander("Dettagli Tecnici (Info)"):
                    st.text(info["info_string"])

            with tab2:
                st.subheader("Analisi Statistica Avanzata")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 🌡️ Heatmap Correlazioni")
                    numerical_df = df.select_dtypes(include=['float64', 'int64'])
                    if not numerical_df.empty:
                        corr_matrix = numerical_df.corr()
                        fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', title="Matrice di Correlazione")
                        st.plotly_chart(fig_corr, use_container_width=True)
                    else:
                        st.warning("Nessuna colonna numerica per le correlazioni.")

                with col2:
                    st.markdown("### 📊 Analisi Distribuzione")
                    dist_col = st.selectbox("Seleziona Colonna Numerica", numerical_df.columns if not numerical_df.empty else [])
                    if dist_col:
                        # Statistiche rapide
                        desc = numerical_df[dist_col].describe()
                        st.write(f"**Media**: {desc['mean']:.2f} | **Mediana**: {desc['50%']:.2f} | **Std**: {desc['std']:.2f}")
                        
                        # Grafico combinato
                        fig_dist = px.histogram(df, x=dist_col, marginal="box", title=f"Distribuzione di {dist_col}")
                        st.plotly_chart(fig_dist, use_container_width=True)

            with tab3:
                st.subheader("Visualizzazione Personalizzata")
                
                chart_type = st.selectbox("Seleziona Tipo di Grafico", ["Scatter Plot", "Bar Chart", "Line Chart", "Histogram"])
                columns = df.columns.tolist()
                
                col_ctrl1, col_ctrl2 = st.columns(2)

                if chart_type == "Scatter Plot":
                    with col_ctrl1: x_col = st.selectbox("Asse X", columns, index=0)
                    with col_ctrl2: y_col = st.selectbox("Asse Y", columns, index=1 if len(columns) > 1 else 0)
                    color_col = st.selectbox("Colore (Opzionale)", [None] + columns)
                    
                    if x_col and y_col:
                        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=f"{x_col} vs {y_col}")
                        st.plotly_chart(fig, use_container_width=True)
                        
                elif chart_type == "Histogram":
                    with col_ctrl1: x_col = st.selectbox("Colonna da analizzare", columns)
                    with col_ctrl2: bins = st.slider("Numero di Bin", 5, 100, 20)
                    
                    if x_col:
                        fig = px.histogram(df, x=x_col, nbins=bins, title=f"Distribuzione di {x_col}")
                        st.plotly_chart(fig, use_container_width=True)
                        
                elif chart_type == "Bar Chart":
                    with col_ctrl1: x_col = st.selectbox("Categoria (X)", columns)
                    with col_ctrl2: y_col = st.selectbox("Valore (Y)", columns)
                    
                    if x_col and y_col:
                        fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} per {x_col}")
                        st.plotly_chart(fig, use_container_width=True)
                        
                elif chart_type == "Line Chart":
                    with col_ctrl1: x_col = st.selectbox("Asse X (Tempo/Seq)", columns)
                    with col_ctrl2: y_col = st.selectbox("Asse Y (Valore)", columns)
                    
                    if x_col and y_col:
                        fig = px.line(df, x=x_col, y=y_col, title=f"Trend di {y_col}")
                        st.plotly_chart(fig, use_container_width=True)

            with tab4:
                st.subheader("Raggruppamento e Aggregazione")
                
                cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                
                if cat_cols and num_cols:
                    group_col = st.selectbox("Raggruppa per", cat_cols)
                    target_col = st.selectbox("Calcola statistiche su", num_cols)
                    agg_func = st.selectbox("Funzione", ["mean", "sum", "count", "min", "max"])
                    
                    if st.button("Calcola Aggregazione"):
                        grouped = df.groupby(group_col)[target_col].agg(agg_func).reset_index()
                        grouped = grouped.sort_values(by=target_col, ascending=False)
                        
                        col_res1, col_res2 = st.columns(2)
                        with col_res1:
                            st.dataframe(grouped)
                        with col_res2:
                            fig_agg = px.bar(grouped, x=group_col, y=target_col, title=f"{agg_func} di {target_col} per {group_col}")
                            st.plotly_chart(fig_agg, use_container_width=True)
                else:
                    st.info("Sono necessarie almeno una colonna categorica e una numerica per usare questa funzione.")

        else:
            st.error("Errore nel caricamento del file. Verifica il formato.")
    else:
        st.info("👈 Carica un file dalla barra laterale per iniziare l'analisi.")

if __name__ == "__main__":
    main()
