import streamlit as st
import os
import sys

# Tenta importar o processador e exibir erro amigável se falhar
try:
    import pandas as pd
    from data_processor import DataProcessor
except ImportError as e:
    st.error(f"❌ Erro de Dependência: {e}")
    st.info("Certifique-se de que o arquivo 'data_processor.py' está na mesma pasta no GitHub e que o 'requirements.txt' está correto.")
    st.stop()
except Exception as e:
    st.error(f"❌ Erro na inicialização: {e}")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="Plate Search Pro • Cloud", 
    page_icon="🔍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Premium via CSS
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #3b82f6;
        color: white;
    }
    .stTextInput>div>div>input {
        color: #f0f2f6;
    }
    .result-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #1e293b;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    .plate-badge {
        font-family: monospace;
        background-color: #3b82f6;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 0.3rem;
        font-weight: bold;
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Instancia o processador (usa cache para não processar toda hora)
@st.cache_resource
def get_processor():
    return DataProcessor()

processor = get_processor()

# Sidebar
with st.sidebar:
    st.title("Plate Search Pro")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Carregar Base Excel", type=["xlsx", "xls", "xlsb"])
    
    if uploaded_file:
        # Salva temporariamente para o pandas ler
        temp_path = os.path.join("temp_" + uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            with st.spinner('Indexando base...'):
                progress_container = st.empty()
                def progress_cb(val, text):
                    progress_container.text(text)
                
                count = processor.load_excel(temp_path, progress_callback=None) # Callback simplificado no web
                st.success(f"Base carregada: {count} registros")
                st.session_state['loaded'] = True
        except Exception as e:
            st.error(f"Erro ao carregar: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    st.markdown("---")
    st.info("💡 Digite a placa ao lado para buscar resultados em tempo real.")

# Área Principal
if st.session_state.get('loaded'):
    q = st.text_input("🔍 Buscar por Placa", placeholder="Ex: ABC1234...")
    
    results = processor.search(q)
    
    if not results.empty:
        st.subheader(f"Resultados Encontrados ({len(results)})")
        
        # Mostra os primeiros 100 resultados para performance
        for i, row in results.head(100).iterrows():
            with st.container():
                st.markdown(f"""
                    <div class="result-card">
                        <span class="plate-badge">{row['plate_raw']}</span>
                        <span style="color: #94a3b8; margin-left:10px;">Aba: {row['sheet_name']}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Ver detalhes completos"):
                    cols = st.columns(3)
                    idx = 0
                    for col_name, val in row.items():
                        if col_name in ['plate_norm', 'plate_raw', 'sheet_name', 'row_index']:
                            continue
                        if pd.notna(val):
                            with cols[idx % 3]:
                                st.markdown(f"**{col_name}**")
                                st.text(str(val))
                            idx += 1
    else:
        if q:
            st.warning("Nenhuma placa encontrada com esse termo.")
        else:
            st.info("Aguardando busca...")
else:
    st.title("Bem-vindo ao Buscador de Placas")
    st.markdown("""
        ### Como usar:
        1. Use o menu lateral para **carregar seu arquivo Excel**.
        2. Aguarde a indexação (é quase instantânea).
        3. Digite a placa no campo de busca que aparecerá aqui.
    """)
    st.image("https://images.unsplash.com/photo-1554224155-6726b3ff858f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", use_column_width=True)
