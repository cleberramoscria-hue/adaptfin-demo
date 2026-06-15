import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import uuid
from utils.theme_utils import aplicar_tema_global

# Aplicar tema
aplicar_tema_global()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.format_utils import format_currency
from src.database import DatabaseManager

st.set_page_config(page_title="Metas - AdaptFin", page_icon="🎯", layout="wide")

def formatar_moeda(valor):
    return format_currency(valor)

def formatar_data_br(data):
    """Formata data para padrão brasileiro DD/MM/YYYY"""
    if data is None or pd.isna(data):
        return "N/A"
    try:
        if isinstance(data, str):
            data = pd.to_datetime(data, errors='coerce')
        if pd.isna(data):
            return "N/A"
        return data.strftime("%d/%m/%Y")
    except:
        return "N/A"

def converter_para_date(data):
    """Converte datetime para date se necessário"""
    if data is None:
        return None
    if isinstance(data, datetime):
        return data.date()
    return data

st.title("🎯 Metas Financeiras")
st.markdown("---")

# Inicializar banco de dados
db = DatabaseManager()

# Inicializar session state
if "metas" not in st.session_state:
    st.session_state.metas = []

# Metas pré-programadas
METAS_PRE_PROGRAMADAS = [
    {
        "nome": "🏖️ Viagem Internacional",
        "valor": 15000,
        "prazo_meses": 12,
        "aporte": 1250,
        "icone": "✈️",
        "descricao": "Realize o sonho de conhecer outro país"
    },
    {
        "nome": "🏠 Entrada da Casa Própria",
        "valor": 50000,
        "prazo_meses": 24,
        "aporte": 2083,
        "icone": "🏠",
        "descricao": "Dê o primeiro passo para sair do aluguel"
    },
    {
        "nome": "💰 Reserva de Emergência",
        "valor": 12000,
        "prazo_meses": 6,
        "aporte": 2000,
        "icone": "🛡️",
        "descricao": "Crie uma reserva para imprevistos"
    },
    {
        "nome": "🚗 Carro Novo",
        "valor": 35000,
        "prazo_meses": 18,
        "aporte": 1944,
        "icone": "🚗",
        "descricao": "Troque de carro ou compre o primeiro"
    },
    {
        "nome": "📚 Curso/MBA",
        "valor": 8000,
        "prazo_meses": 10,
        "aporte": 800,
        "icone": "📚",
        "descricao": "Invista na sua educação e carreira"
    },
    {
        "nome": "💍 Casamento",
        "valor": 20000,
        "prazo_meses": 12,
        "aporte": 1667,
        "icone": "💍",
        "descricao": "Realize o sonho do casamento"
    },
    {
        "nome": "🏦 Aposentadoria",
        "valor": 100000,
        "prazo_meses": 60,
        "aporte": 1667,
        "icone": "🏦",
        "descricao": "Garanta seu futuro com tranquilidade"
    },
    {
        "nome": "💻 Computador Novo",
        "valor": 5000,
        "prazo_meses": 6,
        "aporte": 833,
        "icone": "💻",
        "descricao": "Upgrade no seu equipamento"
    }
]

def carregar_metas_do_banco():
    """Carrega metas do banco de dados"""
    try:
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, valor_alvo, valor_atual, prazo, aporte_mensal, status FROM metas")
        rows = cursor.fetchall()
        conn.close()
        
        metas = []
        for row in rows:
            prazo = None
            if row[4]:
                try:
                    prazo = datetime.fromisoformat(row[4]).date()
                except:
                    prazo = datetime.strptime(row[4], '%Y-%m-%d').date()
            
            metas.append({
                "id": row[0],
                "nome": row[1],
                "valor": row[2],
                "economizado": row[3],
                "prazo": prazo,
                "aporte": row[5],
                "status": row[6]
            })
        return metas
    except Exception as e:
        print(f"Erro ao carregar metas: {e}")
        return []

def salvar_meta_no_banco(meta):
    """Salva meta no banco de dados"""
    try:
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        prazo_str = meta['prazo'].isoformat() if meta['prazo'] else None
        cursor.execute("""
            INSERT OR REPLACE INTO metas (id, nome, valor_alvo, valor_atual, prazo, aporte_mensal, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (meta.get('id', str(uuid.uuid4())[:8]), 
              meta['nome'], meta['valor'], meta['economizado'], 
              prazo_str,
              meta.get('aporte', 0), meta.get('status', 'Ativa')))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar meta: {e}")

def excluir_meta_do_banco(meta_id):
    """Exclui meta do banco de dados"""
    try:
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metas WHERE id = ?", (meta_id,))
        conn.commit()
        conn.close()
    except:
        pass

# Carregar metas do banco ao iniciar
if not st.session_state.metas:
    st.session_state.metas = carregar_metas_do_banco()

# ====================== METAS PRÉ-PROGRAMADAS ======================
st.subheader("📋 Metas Pré-Programadas")
st.caption("Clique em uma meta abaixo para adicionar rapidamente")

# Exibir metas pré-programadas em grid
for i in range(0, len(METAS_PRE_PROGRAMADAS), 4):
    cols = st.columns(4)
    for j in range(4):
        idx = i + j
        if idx < len(METAS_PRE_PROGRAMADAS):
            meta_pre = METAS_PRE_PROGRAMADAS[idx]
            with cols[j]:
                with st.container():
                    st.markdown(f"""
                    <div style="
                        background-color: #f0f2f6;
                        padding: 15px;
                        border-radius: 10px;
                        margin: 5px;
                        text-align: center;
                    ">
                        <span style="font-size: 2rem;">{meta_pre['icone']}</span>
                        <p style="font-weight: bold; margin: 5px 0;">{meta_pre['nome']}</p>
                        <p style="font-size: 0.8rem; color: #666;">{meta_pre['descricao']}</p>
                        <p style="font-weight: bold; color: #2ecc71;">{formatar_moeda(meta_pre['valor'])}</p>
                        <p style="font-size: 0.7rem;">em {meta_pre['prazo_meses']} meses</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"➕ Usar esta meta", key=f"pre_{idx}", use_container_width=True):
                        existe = any(m['nome'] == meta_pre['nome'] for m in st.session_state.metas)
                        if existe:
                            st.warning(f"⚠️ Você já possui uma meta com este nome!")
                        else:
                            nova_meta = {
                                "id": str(uuid.uuid4())[:8],
                                "nome": f"{meta_pre['icone']} {meta_pre['nome']}",
                                "valor": meta_pre['valor'],
                                "economizado": 0,
                                "prazo": (datetime.now() + timedelta(days=meta_pre['prazo_meses'] * 30)).date(),
                                "aporte": meta_pre['aporte'],
                                "status": "Ativa"
                            }
                            st.session_state.metas.append(nova_meta)
                            salvar_meta_no_banco(nova_meta)
                            st.success(f"✅ Meta '{meta_pre['nome']}' adicionada!")
                            st.rerun()

st.markdown("---")

# ====================== CRIAR META PERSONALIZADA ======================
st.subheader("➕ Criar Meta Personalizada")

with st.expander("Clique para criar sua própria meta", expanded=False):
    with st.form("add_meta"):
        col1, col2 = st.columns(2)
        with col1:
            nome_meta = st.text_input("Nome da Meta", placeholder="Ex: Viagem dos sonhos, Casa própria...")
            st.caption("💡 Escolha um nome que te motive!")
        
        with col2:
            valor_meta = st.number_input("Valor Alvo (R$)", min_value=0.0, step=500.0, format="%.2f", value=10000.0)
            st.caption("💰 Quanto você precisa juntar?")
        
        col3, col4 = st.columns(2)
        with col3:
            prazo_meta = st.date_input("Prazo", value=datetime.now().date() + timedelta(days=365), format="DD/MM/YYYY")
            st.caption(f"📅 Data: {prazo_meta.strftime('%d/%m/%Y')}")
        
        with col4:
            aporte_mensal = st.number_input("Aporte Mensal (R$)", min_value=0.0, step=100.0, format="%.2f", value=500.0)
            st.caption("📊 Quanto você pode guardar por mês?")
        
        if st.form_submit_button("✅ Criar Meta Personalizada", use_container_width=True):
            if nome_meta and valor_meta > 0:
                nova_meta = {
                    "id": str(uuid.uuid4())[:8],
                    "nome": nome_meta,
                    "valor": valor_meta,
                    "economizado": 0,
                    "prazo": prazo_meta,
                    "aporte": aporte_mensal,
                    "status": "Ativa"
                }
                st.session_state.metas.append(nova_meta)
                salvar_meta_no_banco(nova_meta)
                st.success(f"✅ Meta '{nome_meta}' criada com sucesso!")
                st.rerun()
            else:
                st.error("❌ Preencha todos os campos")

st.markdown("---")

# ====================== LISTA DE METAS ======================
if st.session_state.metas:
    st.subheader("📋 Minhas Metas")
    
    # Resumo geral
    metas_ativas = [m for m in st.session_state.metas if m.get('status') != 'Concluída']
    total_alvo = sum(m['valor'] for m in metas_ativas)
    total_economizado = sum(m['economizado'] for m in metas_ativas)
    progresso_geral = (total_economizado / total_alvo * 100) if total_alvo > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 Metas Ativas", len(metas_ativas))
    with col2:
        st.metric("💰 Total Economizado", formatar_moeda(total_economizado))
    with col3:
        st.metric("📊 Progresso Geral", f"{progresso_geral:.1f}%")
    with col4:
        st.metric("🎯 Total em Metas", formatar_moeda(total_alvo))
    
    if progresso_geral > 0:
        st.progress(progresso_geral / 100)
    
    st.markdown("---")
    
    # Exibir cada meta
    for i, meta in enumerate(st.session_state.metas):
        with st.container():
            # Converter prazo para date se necessário
            prazo_meta = converter_para_date(meta.get('prazo'))
            hoje = datetime.now().date()
            
            # Status da meta
            if meta['economizado'] >= meta['valor']:
                status_text = "✅ CONCLUÍDA"
                status_cor = "🟢"
                meta['status'] = "Concluída"
            elif prazo_meta and prazo_meta < hoje:
                status_text = "⚠️ ATRASADA"
                status_cor = "🔴"
            else:
                status_text = "🟡 EM ANDAMENTO"
                status_cor = "🟡"
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {meta['nome']}")
            with col2:
                st.markdown(f"**Status:** {status_text}")
            
            # Barra de progresso
            progresso = min(meta['economizado'] / meta['valor'], 1.0) if meta['valor'] > 0 else 0
            st.progress(progresso)
            
            # Métricas da meta
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎯 Valor Alvo", formatar_moeda(meta['valor']))
            with col2:
                st.metric("💰 Economizado", formatar_moeda(meta['economizado']))
            with col3:
                if prazo_meta:
                    dias = (prazo_meta - hoje).days
                    st.metric("⏰ Prazo", f"{max(0, dias)} dias")
                    st.caption(f"📅 Vence em: {formatar_data_br(prazo_meta)}")
                else:
                    st.metric("⏰ Prazo", "Sem prazo")
            with col4:
                restante = meta['valor'] - meta['economizado']
                st.metric("📊 Faltam", formatar_moeda(restante))
            
            # Cálculo de projeção
            if meta.get('aporte', 0) > 0 and meta['economizado'] < meta['valor']:
                restante = meta['valor'] - meta['economizado']
                meses_necessarios = restante / meta['aporte']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📈 **Projeção:** Com aporte de {formatar_moeda(meta['aporte'])}/mês, você atingirá sua meta em {meses_necessarios:.1f} meses")
                with col2:
                    if prazo_meta:
                        meses_disponiveis = max(1, (prazo_meta - hoje).days / 30)
                        if meses_necessarios <= meses_disponiveis:
                            st.success(f"✅ No prazo! Faltam {meses_necessarios:.0f} meses")
                        else:
                            necessario_mensal = restante / meses_disponiveis
                            st.warning(f"⚠️ Aperte o ritmo! Precisa de {formatar_moeda(necessario_mensal)}/mês")
            
            # Adicionar economia
            st.markdown("**Adicionar economia a esta meta:**")
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                valor_add = st.number_input(f"Valor", min_value=0.0, step=50.0, format="%.2f", key=f"add_{i}", label_visibility="collapsed")
            with col2:
                if st.button("➕ Adicionar", key=f"btn_{i}"):
                    if valor_add > 0:
                        st.session_state.metas[i]['economizado'] += valor_add
                        salvar_meta_no_banco(st.session_state.metas[i])
                        st.success(f"✅ Adicionado {formatar_moeda(valor_add)} à meta '{meta['nome']}'!")
                        st.rerun()
            with col3:
                if st.button("🗑️ Remover", key=f"del_{i}"):
                    excluir_meta_do_banco(meta['id'])
                    st.session_state.metas.pop(i)
                    st.rerun()
            
            st.markdown("---")

else:
    st.info("🎯 Nenhuma meta cadastrada. Escolha uma meta pré-programada acima ou crie a sua!")
    
    with st.expander("💡 Dicas para definir metas eficazes"):
        st.markdown("""
        **Metas SMART - Critérios para metas eficazes:**
        
        - **S** (Específica): Defina exatamente o que você quer
        - **M** (Mensurável): Coloque um valor claro (R$)
        - **A** (Alcançável): Seja realista com sua renda
        - **R** (Relevante): Algo que realmente te motive
        - **T** (Temporal): Defina um prazo realista
        
        **Exemplo de meta SMART:**
        "Quero juntar R$ 15.000 em 12 meses para viajar para a Europa, guardando R$ 1.250 por mês"
        """)

st.markdown("---")
st.caption("🎯 Defina metas e acompanhe seu progresso rumo à liberdade financeira!")