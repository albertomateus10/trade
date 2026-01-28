import streamlit as st
import pandas as pd
import os

# Tenta carregar o processador
try:
    from data_processor import DataProcessor
except Exception as e:
    st.error(f"❌ Erro ao carregar o motor de dados: {e}")
    st.stop()

# Configuração da página (Tema Claro/Elegante)
st.set_page_config(
    page_title="Plate Search Pro • Dashboard", 
    page_icon="🔍", 
    layout="wide"
)

# Estilização "Elegante e Limpa" (Fundo claro, sombras suaves)
st.markdown("""
<style>
    /* Fundo Principal */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Títulos e Textos */
    h1, h2, h3 {
        color: #1e293b;
        font-family: 'Inter', sans-serif;
    }
    
    /* Cartões de Resultado */
    .result-card {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: transform 0.2s;
    }
    
    .result-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }

    .plate-badge {
        font-family: 'Monaco', 'Consolas', monospace;
        background-color: #eff6ff;
        color: #2563eb;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-weight: 800;
        font-size: 1.3rem;
        border: 1px solid #dbeafe;
    }
    
    .info-text {
        color: #64748b;
        font-size: 0.9rem;
    }

    /* Input de Busca */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        padding: 12px;
        font-size: 1.1rem;
    }
    
    /* Botão na Sidebar */
    .stButton>button {
        border-radius: 8px;
        background-color: #2563eb;
        color: white;
        border: None;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_processor():
    return DataProcessor()

processor = get_processor()

# Título e Logo
st.title("🛡️ Plate Search Pro")
st.markdown("<p style='color: #64748b; font-size: 1.1rem;'>Sistema de busca de placas de alta performance</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&q=80&w=200", width=200)
    st.header("Gerenciar Base")
    uploaded_file = st.file_uploader("Suba sua planilha de dados", type=["xlsx", "xls", "xlsb"])
    
    if uploaded_file:
        temp_name = f"temp_{uploaded_file.name}"
        with open(temp_name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            with st.spinner("Indexando dados..."):
                count = processor.load_excel(temp_name)
                st.success(f"✅ {count} registros encontrados!")
                st.session_state['data_ready'] = True
        except Exception as e:
            st.error(f"Erro: {e}")
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)

# Área de Busca
if st.session_state.get('data_ready'):
    # Campo de busca otimizado
    q = st.text_input("Localizar Placa", placeholder="Digite para filtrar...", label_visibility="collapsed")
    
    # Streamlit executa o rerender automaticamente. 
    # Para o usuário não precisar dar Enter, ele só precisa parar de digitar por meio segundo
    # ou clicar fora, mas em apps modernos de Streamlit isso já é bem fluido.
    
    results = processor.search(q)
    
    if not results.empty:
        st.markdown(f"<p class='info-text'>Mostrando {min(len(results), 50)} resultados de {len(results)}</p>", unsafe_allow_html=True)
        
        for _, row in results.head(50).iterrows():
            with st.container():
                # HTML Customizado para o card elegante
                st.markdown(f"""
                    <div class="result-card">
                        <div>
                            <span class="plate-badge">{row['plate_raw']}</span>
                            <span style="margin-left: 15px; color: #1e293b; font-weight: 500;">{row['sheet_name']}</span>
                        </div>
                        <div class="info-text">
                            Linha {row['row_index']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Ver ficha completa"):
                    # Exibição limpa dos dados extras
                    data_cols = [c for c in row.index if c not in ['plate_norm', 'plate_raw', 'sheet_name', 'row_index']]
                    for i in range(0, len(data_cols), 3):
                        cols = st.columns(3)
                        for j in range(3):
                            if i + j < len(data_cols):
                                col_name = data_cols[i+j]
                                val = row[col_name]
                                if pd.notna(val):
                                    cols[j].metric(label=str(col_name), value=str(val))

    elif q:
        st.warning(f"Nenhum registro encontrado para '{q}'.")
else:
    # Tela de Boas Vindas
    st.markdown("""
        <div style="background-color: #ffffff; padding: 40px; border-radius: 20px; border: 1px solid #e2e8f0; text-align: center; margin-top: 50px;">
            <h2 style="color: #2563eb;">Aguardando Arquivo</h2>
            <p style="color: #64748b;">Por favor, carregue sua planilha Excel no menu lateral para começar as buscas.</p>
        </div>
    """, unsafe_allow_html=True)
