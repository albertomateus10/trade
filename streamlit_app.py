import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# Tenta carregar o processador com tratamento de erro
try:
    from data_processor import DataProcessor
except Exception as e:
    st.error(f"❌ Erro ao carregar o motor de dados (data_processor.py): {e}")
    st.info("Verifique se o arquivo 'data_processor.py' foi enviado para o GitHub corretamente.")
    st.stop()

# =========================
# Configuração da página
# =========================
st.set_page_config(
    page_title="Plate Search Pro • Executive Dashboard",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Estado inicial
# =========================
if "data_ready" not in st.session_state:
    st.session_state.data_ready = False
if "indexed_count" not in st.session_state:
    st.session_state.indexed_count = 0
if "indexed_file" not in st.session_state:
    st.session_state.indexed_file = None
if "indexed_at" not in st.session_state:
    st.session_state.indexed_at = None
if "indexed_secs" not in st.session_state:
    st.session_state.indexed_secs = None
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "selected_row" not in st.session_state:
    st.session_state.selected_row = None

# =========================
# CSS Premium (Dark/Light)
# =========================
DARK_CSS = """
<style>
  :root{
    --bg: #0b1220;
    --panel: rgba(255,255,255,.06);
    --panel2: rgba(255,255,255,.08);
    --stroke: rgba(255,255,255,.10);
    --text: rgba(255,255,255,.92);
    --muted: rgba(255,255,255,.65);
    --brand1: #60a5fa;
    --brand2: #22c55e;
    --warn: #f59e0b;
    --danger: #ef4444;
    --shadow: 0 18px 55px rgba(0,0,0,.45);
    --radius: 18px;
  }

  .stApp{
    background:
      radial-gradient(1200px 700px at 10% 0%, rgba(96,165,250,.20), transparent 60%),
      radial-gradient(900px 600px at 100% 10%, rgba(34,197,94,.18), transparent 55%),
      linear-gradient(180deg, #070b14 0%, var(--bg) 55%, #070b14 100%);
    color: var(--text);
  }

  /* Remove um pouco do “ar de app padrão” */
  [data-testid="stSidebar"]{
    background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
    border-right: 1px solid var(--stroke);
  }

  /* Header premium */
  .topbar{
    position: sticky;
    top: 0;
    z-index: 50;
    padding: 14px 16px;
    border: 1px solid var(--stroke);
    border-radius: var(--radius);
    background: rgba(10,15,25,.58);
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow);
    margin-bottom: 14px;
  }
  .topbar h1{
    margin: 0;
    font-size: 1.35rem;
    letter-spacing: .2px;
  }
  .subline{
    margin-top: 4px;
    color: var(--muted);
    font-size: .92rem;
  }
  .chip{
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding: 6px 10px;
    border-radius: 999px;
    border: 1px solid var(--stroke);
    background: rgba(255,255,255,.06);
    color: var(--muted);
    font-size: .86rem;
    margin-left: 8px;
  }
  .dot{
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: var(--brand2);
    box-shadow: 0 0 0 3px rgba(34,197,94,.18);
  }
  .dot.off{
    background: var(--warn);
    box-shadow: 0 0 0 3px rgba(245,158,11,.18);
  }

  /* KPI cards */
  .kpi{
    border: 1px solid var(--stroke);
    border-radius: var(--radius);
    background: rgba(255,255,255,.06);
    box-shadow: var(--shadow);
    padding: 14px 14px;
  }
  .kpi .label{
    color: var(--muted);
    font-size: .86rem;
  }
  .kpi .value{
    font-size: 1.35rem;
    font-weight: 800;
    margin-top: 6px;
    letter-spacing: .3px;
  }
  .kpi .hint{
    color: rgba(255,255,255,.55);
    font-size: .82rem;
    margin-top: 4px;
  }

  /* Search hero */
  .hero{
    border: 1px solid var(--stroke);
    border-radius: var(--radius);
    background: linear-gradient(90deg, rgba(96,165,250,.14), rgba(34,197,94,.10));
    box-shadow: var(--shadow);
    padding: 14px 14px;
    margin: 10px 0 12px 0;
  }
  .hero-title{
    display:flex;
    align-items:center;
    gap:10px;
    font-weight: 800;
    margin: 0 0 6px 0;
  }
  .hero-sub{
    color: var(--muted);
    margin: 0;
    font-size: .92rem;
  }

  /* Result cards */
  .r-card{
    border: 1px solid var(--stroke);
    border-radius: 16px;
    background: rgba(255,255,255,.06);
    padding: 12px 12px;
    margin-bottom: 10px;
    transition: transform .12s ease, background .12s ease;
  }
  .r-card:hover{
    transform: translateY(-2px);
    background: rgba(255,255,255,.08);
  }
  .plate{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-weight: 900;
    letter-spacing: 1px;
    font-size: 1.15rem;
    color: rgba(255,255,255,.95);
  }
  .meta{
    color: var(--muted);
    font-size: .86rem;
    margin-top: 4px;
  }

  /* Ajuste de inputs */
  .stTextInput > div > div input{
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,.16) !important;
    background: rgba(255,255,255,.06) !important;
  }
  .stTextInput > label{
    font-weight: 700 !important;
  }

  /* Remove excesso de padding nos containers */
  .block-container{
    padding-top: 1.2rem;
    padding-bottom: 2rem;
  }
</style>
"""

LIGHT_CSS = """
<style>
  :root{
    --bg: #f6f8fc;
    --panel: rgba(0,0,0,.04);
    --panel2: rgba(0,0,0,.06);
    --stroke: rgba(0,0,0,.08);
    --text: rgba(10,15,25,.92);
    --muted: rgba(10,15,25,.62);
    --brand1: #2563eb;
    --brand2: #16a34a;
    --warn: #d97706;
    --danger: #dc2626;
    --shadow: 0 18px 55px rgba(10,15,25,.10);
    --radius: 18px;
  }

  .stApp{
    background:
      radial-gradient(1200px 700px at 10% 0%, rgba(37,99,235,.16), transparent 60%),
      radial-gradient(900px 600px at 100% 10%, rgba(22,163,74,.14), transparent 55%),
      linear-gradient(180deg, #ffffff 0%, var(--bg) 55%, #ffffff 100%);
    color: var(--text);
  }

  [data-testid="stSidebar"]{
    background: linear-gradient(180deg, rgba(0,0,0,.03), rgba(0,0,0,.02));
    border-right: 1px solid var(--stroke);
  }

  .topbar{
    position: sticky;
    top: 0;
    z-index: 50;
    padding: 14px 16px;
    border: 1px solid var(--stroke);
    border-radius: var(--radius);
    background: rgba(255,255,255,.72);
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow);
    margin-bottom: 14px;
  }
  .topbar h1{ margin: 0; font-size: 1.35rem; letter-spacing: .2px; }
  .subline{ margin-top: 4px; color: var(--muted); font-size: .92rem; }
  .chip{
    display:inline-flex; align-items:center; gap:8px;
    padding: 6px 10px; border-radius: 999px;
    border: 1px solid var(--stroke);
    background: rgba(0,0,0,.03);
    color: var(--muted);
    font-size: .86rem;
    margin-left: 8px;
  }
  .dot{ width: 8px; height: 8px; border-radius: 999px; background: var(--brand2); box-shadow: 0 0 0 3px rgba(22,163,74,.14); }
  .dot.off{ background: var(--warn); box-shadow: 0 0 0 3px rgba(217,119,6,.14); }

  .kpi{
    border: 1px solid var(--stroke);
    border-radius: var(--radius);
    background: rgba(255,255,255,.70);
    box-shadow: var(--shadow);
    padding: 14px 14px;
  }
  .kpi .label{ color: var(--muted); font-size: .86rem; }
  .kpi .value{ font-size: 1.35rem; font-weight: 800; margin-top: 6px; letter-spacing: .3px; }
  .kpi .hint{ color: rgba(10,15,25,.55); font-size: .82rem; margin-top: 4px; }

  .hero{
    border: 1px solid var(--stroke);
    border-radius: var(--radius);
    background: linear-gradient(90deg, rgba(37,99,235,.12), rgba(22,163,74,.10));
    box-shadow: var(--shadow);
    padding: 14px 14px;
    margin: 10px 0 12px 0;
  }
  .hero-title{ display:flex; align-items:center; gap:10px; font-weight: 800; margin: 0 0 6px 0; }
  .hero-sub{ color: var(--muted); margin: 0; font-size: .92rem; }

  .r-card{
    border: 1px solid var(--stroke);
    border-radius: 16px;
    background: rgba(255,255,255,.75);
    padding: 12px 12px;
    margin-bottom: 10px;
    transition: transform .12s ease, background .12s ease;
  }
  .r-card:hover{ transform: translateY(-2px); background: rgba(255,255,255,.92); }
  .plate{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-weight: 900;
    letter-spacing: 1px;
    font-size: 1.15rem;
    color: rgba(10,15,25,.92);
  }
  .meta{ color: var(--muted); font-size: .86rem; margin-top: 4px; }

  .stTextInput > div > div input{
    border-radius: 14px !important;
    border: 1px solid rgba(10,15,25,.14) !important;
    background: rgba(0,0,0,.02) !important;
  }
  .stTextInput > label{ font-weight: 700 !important; }
  .block-container{ padding-top: 1.2rem; padding-bottom: 2rem; }
</style>
"""

st.markdown(DARK_CSS if st.session_state.theme == "dark" else LIGHT_CSS, unsafe_allow_html=True)

# =========================
# Processor (cache)
# =========================
@st.cache_resource
def get_processor():
    return DataProcessor()

processor = get_processor()

# =========================
# Sidebar (Executive)
# =========================
with st.sidebar:
    st.markdown("### 🔎 Plate Search Pro")
    st.caption("Executive Dashboard • Busca rápida em múltiplas abas")

    st.session_state.theme = st.radio(
        "Tema",
        options=["dark", "light"],
        horizontal=True,
        index=0 if st.session_state.theme == "dark" else 1,
        help="Apenas visual — não muda a lógica do sistema."
    )

    st.divider()
    st.markdown("#### 📥 Base de Dados")

    uploaded_file = st.file_uploader(
        "Arraste e solte sua planilha aqui",
        type=["xlsx", "xls", "xlsb"],
        help="Suporta múltiplas abas. O sistema indexa e permite busca por placa.",
    )

    colA, colB = st.columns(2)
    with colA:
        clear = st.button("🧹 Limpar base", use_container_width=True)
    with colB:
        reset_sel = st.button("🧩 Limpar seleção", use_container_width=True)

    if clear:
        st.session_state.data_ready = False
        st.session_state.indexed_count = 0
        st.session_state.indexed_file = None
        st.session_state.indexed_at = None
        st.session_state.indexed_secs = None
        st.session_state.selected_row = None
        # Zera cache do processor (dataframe interno)
        processor.df = pd.DataFrame()
        st.success("Base limpa.")
        st.rerun()

    if reset_sel:
        st.session_state.selected_row = None
        st.info("Seleção removida.")
        st.rerun()

    st.divider()

    if st.session_state.data_ready:
        st.success("✅ Base pronta para busca")
        if st.session_state.indexed_file:
            st.caption(f"📄 Arquivo: **{st.session_state.indexed_file}**")
        if st.session_state.indexed_at:
            st.caption(f"🕒 Indexado em: **{st.session_state.indexed_at}**")
        if st.session_state.indexed_secs is not None:
            st.caption(f"⚡ Tempo: **{st.session_state.indexed_secs:.2f}s**")
    else:
        st.warning("Aguardando upload da planilha…")

# Reaplica CSS ao mudar tema
st.markdown(DARK_CSS if st.session_state.theme == "dark" else LIGHT_CSS, unsafe_allow_html=True)

# =========================
# Upload + Indexação (com progresso real)
# =========================
if uploaded_file is not None:
    temp_name = f"temp_{uploaded_file.name}"
    with open(temp_name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    progress = st.sidebar.progress(0)
    status = st.sidebar.empty()

    def progress_callback(val, text):
        # val vem como fração (0..1) do DataProcessor
        try:
            v = float(val)
        except Exception:
            v = 0.0
        v = max(0.0, min(1.0, v))
        progress.progress(v)
        status.caption(text)

    t0 = time.perf_counter()
    try:
        with st.spinner("🔧 Indexando e preparando a base para busca…"):
            count = processor.load_excel(temp_name, progress_callback=progress_callback)
        t1 = time.perf_counter()

        st.session_state.data_ready = True
        st.session_state.indexed_count = int(count)
        st.session_state.indexed_file = uploaded_file.name
        st.session_state.indexed_at = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.session_state.indexed_secs = (t1 - t0)

        st.sidebar.success(f"✅ {count} registros indexados!")
    except Exception as e:
        st.sidebar.error(f"Falha ao processar: {e}")
    finally:
        status.empty()
        progress.empty()
        if os.path.exists(temp_name):
            os.remove(temp_name)

# =========================
# Header (Topbar)
# =========================
is_ready = st.session_state.data_ready
dot_class = "dot" if is_ready else "dot off"
status_text = "ONLINE • Base pronta" if is_ready else "OFFLINE • Envie uma planilha"

st.markdown(
    f"""
    <div class="topbar">
      <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px;">
        <div>
          <h1>🔎 Plate Search Pro <span class="chip"><span class="{dot_class}"></span>{status_text}</span></h1>
          <div class="subline">Buscador executivo por placa • múltiplas abas • visão rápida + detalhes</div>
        </div>
        <div style="text-align:right; color: rgba(255,255,255,.65);">
          <div style="font-size:.85rem; opacity:.85;">Sessão</div>
          <div style="font-weight:800;">{datetime.now().strftime("%d/%m/%Y %H:%M")}</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# KPIs (Executive)
# =========================
k1, k2, k3, k4 = st.columns(4)

df_loaded = getattr(processor, "df", pd.DataFrame())
sheet_count = int(df_loaded["sheet_name"].nunique()) if (is_ready and "sheet_name" in df_loaded.columns) else 0
last_file = st.session_state.indexed_file or "—"
last_time = st.session_state.indexed_at or "—"
last_secs = st.session_state.indexed_secs

with k1:
    st.markdown(
        f"""
        <div class="kpi">
          <div class="label">Registros indexados</div>
          <div class="value">{st.session_state.indexed_count if is_ready else 0:,}</div>
          <div class="hint">Linhas com placa detectada</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with k2:
    st.markdown(
        f"""
        <div class="kpi">
          <div class="label">Abas com resultados</div>
          <div class="value">{sheet_count}</div>
          <div class="hint">Consolidado por aba</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with k3:
    secs_txt = f"{last_secs:.2f}s" if (last_secs is not None) else "—"
    st.markdown(
        f"""
        <div class="kpi">
          <div class="label">Tempo de indexação</div>
          <div class="value">{secs_txt}</div>
          <div class="hint">Tempo desta sessão</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with k4:
    st.markdown(
        f"""
        <div class="kpi">
          <div class="label">Último arquivo</div>
          <div class="value" style="font-size:1.05rem; line-height:1.2;">{last_file}</div>
          <div class="hint">Indexado em {last_time}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# Search Hero + Filtros
# =========================
st.markdown(
    """
    <div class="hero">
      <div class="hero-title">✨ Busca inteligente por placa</div>
      <p class="hero-sub">Digite a placa (ou parte dela). A listagem aparece em tempo real e você pode selecionar um item para abrir os detalhes ao lado.</p>
    </div>
    """,
    unsafe_allow_html=True
)

if not is_ready:
    st.info("👋 Envie uma planilha no menu lateral para começar.")
    st.stop()

left, right = st.columns([1.7, 1.0], gap="large")

with left:
    q = st.text_input(
        "Placa (busca por prefixo / parcial)",
        placeholder="Ex: ABC1234 ou ABC",
        help="Pode digitar incompleto. O sistema normaliza e busca por início.",
        key="plate_query",
    )

    with st.expander("⚙️ Filtros avançados", expanded=False):
        max_results = st.slider("Limite de resultados exibidos", 20, 300, 80, step=10)
        only_unique = st.toggle("Mostrar apenas placas únicas", value=True)
        sheet_filter = []
        if "sheet_name" in df_loaded.columns and sheet_count > 0:
            sheet_filter = st.multiselect(
                "Filtrar por aba",
                options=sorted(df_loaded["sheet_name"].dropna().unique().tolist()),
                default=[],
            )
        show_table = st.toggle("Também mostrar tabela (aba adicional)", value=True)

    # Busca
    results = processor.search(q)

    # Filtros
    if not results.empty:
        if sheet_filter:
            results = results[results["sheet_name"].isin(sheet_filter)]
        if only_unique and "plate_norm" in results.columns:
            results = results.drop_duplicates(subset=["plate_norm"], keep="first")

    total = int(len(results)) if isinstance(results, pd.DataFrame) else 0

    # Tabs: Cards / Tabela
    tabs = st.tabs(["🧩 Cards (Executivo)", "📋 Tabela"]) if show_table else [None]

    # ===== Cards =====
    target = tabs[0] if show_table else st
    with (target if target is not None else st):
        if q and total == 0:
            st.warning("Nenhum resultado encontrado.")
        elif not q:
            st.info("Digite uma placa acima para começar a busca.")
        else:
            st.write(f"**{min(total, max_results)}** exibidos de **{total}** resultados.")
            view = results.head(max_results).copy()

            for i, row in view.iterrows():
                plate = str(row.get("plate_raw", "—"))
                sheet = str(row.get("sheet_name", "—"))
                rindex = str(row.get("row_index", "—"))

                c1, c2 = st.columns([0.78, 0.22])
                with c1:
                    st.markdown(
                        f"""
                        <div class="r-card">
                          <div class="plate">{plate}</div>
                          <div class="meta">Aba: <b>{sheet}</b> • Linha: <b>{rindex}</b></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with c2:
                    if st.button("Selecionar", key=f"sel_{i}", use_container_width=True):
                        st.session_state.selected_row = row.to_dict()
                        st.success(f"Selecionado: {plate}")

    # ===== Tabela =====
    if show_table:
        with tabs[1]:
            if q and total > 0:
                cols_to_hide = [c for c in ["plate_norm"] if c in results.columns]
                st.dataframe(results.drop(columns=cols_to_hide, errors="ignore"), use_container_width=True, height=420)
            elif q:
                st.warning("Nenhum resultado para mostrar na tabela.")
            else:
                st.info("Digite uma placa para preencher a tabela.")

with right:
    st.markdown("#### 🧾 Detalhes (Painel Executivo)")

    if st.session_state.selected_row is None:
        st.info("Selecione um resultado à esquerda para ver os detalhes aqui.")
    else:
        row = st.session_state.selected_row
        plate = row.get("plate_raw", "—")
        sheet = row.get("sheet_name", "—")
        rindex = row.get("row_index", "—")

        st.markdown(
            f"""
            <div class="kpi" style="margin-bottom:12px;">
              <div class="label">Placa selecionada</div>
              <div class="value">{plate}</div>
              <div class="hint">Aba: {sheet} • Linha: {rindex}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Monta um dataframe somente com campos relevantes (sem metacampos)
        df_one = pd.DataFrame([row])
        drop_cols = [c for c in ["plate_norm", "plate_raw", "sheet_name", "row_index"] if c in df_one.columns]
        df_one = df_one.drop(columns=drop_cols, errors="ignore")

        # Remove colunas totalmente vazias
        df_one = df_one.dropna(axis=1, how="all")

        # Exibição “executiva”
        if df_one.empty:
            st.warning("Sem detalhes adicionais disponíveis para este registro.")
        else:
            st.dataframe(df_one, use_container_width=True, height=380)

        st.divider()
        st.caption("Dica: use o filtro por **aba** e **placas únicas** para acelerar a análise.")
