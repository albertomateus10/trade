import streamlit as st
import pandas as pd
import os
import re

# Tenta carregar o processador com tratamento de erro
try:
    from data_processor import DataProcessor
except Exception as e:
    st.error(f"❌ Erro ao carregar o motor de dados (data_processor.py): {e}")
    st.info("Verifique se o arquivo 'data_processor.py' foi enviado para o GitHub corretamente.")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="Plate Search Pro • Online", 
    page_icon="🔍", 
    layout="wide"
)

# Estilização Premium (Dark Mode)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .result-card {
        padding: 1.2rem;
        border-radius: 8px;
        background-color: #1e293b;
        border-left: 5px solid #3b82f6;
        margin-bottom: 10px;
    }
    .plate-text {
        font-family: 'Courier New', monospace;
        font-size: 1.4rem;
        font-weight: bold;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_processor():
    return DataProcessor()

processor = get_processor()

# Interface Principal
st.title("🔍 Plate Search Pro • Buscador Online")

with st.sidebar:
    st.header("Base de Dados")
    uploaded_file = st.file_uploader("Suba sua planilha (XLSX, XLS, XLSB)", type=["xlsx", "xls", "xlsb"])
    
    if uploaded_file:
        # Salva o arquivo temporariamente para processamento
        temp_name = f"temp_{uploaded_file.name}"
        with open(temp_name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            with st.spinner("Indexando milhares de linhas..."):
                count = processor.load_excel(temp_name)
                st.success(f"✅ {count} registros indexados!")
                st.session_state['data_ready'] = True
        except Exception as e:
            st.error(f"Falha ao processar: {e}")
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)

if st.session_state.get('data_ready'):
    q = st.text_input("Digite a placa para buscar:", placeholder="Ex: ABC1234")
    
    if q:
        results = processor.search(q)
        if not results.empty:
            st.write(f"Exibindo {min(len(results), 50)} de {len(results)} resultados:")
            for _, row in results.head(50).iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="result-card">
                            <span class="plate-text">{row['plate_raw']}</span> | 
                            <span style="color:#94a3b8">Aba: {row['sheet_name']} (Linha {row['row_index']})</span>
                        </div>
                    """, unsafe_allow_html=True)
                    with st.expander("Ver detalhes"):
                        st.dataframe(pd.DataFrame([row]).drop(['plate_norm', 'plate_raw', 'sheet_name', 'row_index'], axis=1).dropna(axis=1))
        else:
            st.warning("Nenhum resultado encontrado.")
    else:
        st.info("Digite algo acima para começar a busca.")
else:
    st.info("👋 Bem-vindo! Comece carregando uma planilha pelo menu lateral.")
