import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import uuid
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager
from src.shared import carregar_todas_transacoes, formatar_moeda
from utils.theme_utils import aplicar_tema_global, get_temas_disponiveis, get_icone_tema

st.set_page_config(page_title="Configurações - AdaptFin", page_icon="⚙️", layout="wide")

# ====================== INICIALIZAR TODAS AS VARIÁVEIS ======================
if "configuracoes" not in st.session_state:
    st.session_state.configuracoes = {
        "salario_mensal": 0.0,
        "limite_gastos": 0.0,
        "alertas_ativos": True,
        "ml_ativado": True,
        "tema": "Claro",
        "llm_provider": "groq",
        "groq_api_key": "",
        "gemini_api_key": "",
        "openai_api_key": "",
        "github_api_key": "",
        "cerebras_api_key": ""
    }

if "dados_treinamento_carregados" not in st.session_state:
    st.session_state.dados_treinamento_carregados = False

if "dados_carregados_banco" not in st.session_state:
    st.session_state.dados_carregados_banco = False

if "receitas" not in st.session_state:
    st.session_state.receitas = pd.DataFrame()

if "despesas_fixas" not in st.session_state:
    st.session_state.despesas_fixas = pd.DataFrame()

if "gastos_variaveis" not in st.session_state:
    st.session_state.gastos_variaveis = pd.DataFrame()

if "metas" not in st.session_state:
    st.session_state.metas = []

# Aplicar tema
aplicar_tema_global()

st.title("⚙️ Configurações do Sistema")
st.markdown("---")

# ====================== BANCO DE DADOS ======================
db = DatabaseManager()

# ====================== FUNÇÕES ======================
def carregar_todas_transacoes_local():
    todas = []
    if not st.session_state.receitas.empty:
        todas.append(st.session_state.receitas)
    if not st.session_state.despesas_fixas.empty:
        todas.append(st.session_state.despesas_fixas)
    if not st.session_state.gastos_variaveis.empty:
        todas.append(st.session_state.gastos_variaveis)
    
    if todas:
        df_total = pd.concat(todas, ignore_index=True)
        if 'Valor' in df_total.columns:
            df_total['Valor'] = pd.to_numeric(df_total['Valor'], errors='coerce')
            df_total = df_total.dropna(subset=['Valor'])
        return df_total
    return pd.DataFrame()

def carregar_dados_treinamento():
    dados_treinamento = pd.DataFrame({
        "Descrição": ["Salário", "Freelance", "Aluguel", "Supermercado", "Ifood", "Netflix", "Uber", "Cinema", "Academia", "Conta Luz", "Internet", "Farmácia"],
        "Valor": [5000, 1200, -1500, -680, -250, -39.90, -120, -60, -99.90, -180, -100, -75],
        "Categoria": ["Renda", "Renda", "Moradia", "Alimentação", "Alimentação", "Lazer", "Transporte", "Lazer", "Saúde", "Moradia", "Serviços", "Saúde"],
        "Data": pd.date_range(start="2024-01-01", periods=12, freq="15D"),
        "id": [str(i) for i in range(12)],
        "Status": ["Pago"] * 12
    })
    
    st.session_state.receitas = pd.DataFrame(columns=["Descrição", "Valor", "Categoria", "Data", "id", "Status"])
    st.session_state.despesas_fixas = pd.DataFrame(columns=["Descrição", "Valor", "Categoria", "Data", "id", "Status"])
    st.session_state.gastos_variaveis = pd.DataFrame(columns=["Descrição", "Valor", "Categoria", "Data", "id", "Status"])
    
    for _, row in dados_treinamento.iterrows():
        if row['Valor'] > 0:
            st.session_state.receitas = pd.concat([st.session_state.receitas, pd.DataFrame([row])], ignore_index=True)
        else:
            if row['Categoria'] in ['Moradia', 'Serviços']:
                st.session_state.despesas_fixas = pd.concat([st.session_state.despesas_fixas, pd.DataFrame([row])], ignore_index=True)
            else:
                st.session_state.gastos_variaveis = pd.concat([st.session_state.gastos_variaveis, pd.DataFrame([row])], ignore_index=True)
    
    st.session_state.dados_treinamento_carregados = True
    st.session_state.dados_carregados_banco = True
    salvar_todas_no_banco()

def salvar_todas_no_banco():
    df_total = carregar_todas_transacoes_local()
    if not df_total.empty:
        for _, row in df_total.iterrows():
            dados = {
                'id': row.get('id', str(uuid.uuid4())[:8]),
                'descricao': row['Descrição'],
                'valor': float(row['Valor']),
                'categoria': row['Categoria'],
                'data': row['Data'].strftime('%Y-%m-%d') if hasattr(row['Data'], 'strftime') else str(row['Data']),
                'status': row.get('Status', 'Pendente'),
                'tipo': 'receita' if row['Valor'] > 0 else 'despesa'
            }
            db.salvar_transacao_local(dados)
        return True
    return False

def remover_dados_treinamento():
    ids_treinamento = [str(i) for i in range(12)]
    if not st.session_state.receitas.empty:
        st.session_state.receitas = st.session_state.receitas[~st.session_state.receitas['id'].isin(ids_treinamento)]
    if not st.session_state.despesas_fixas.empty:
        st.session_state.despesas_fixas = st.session_state.despesas_fixas[~st.session_state.despesas_fixas['id'].isin(ids_treinamento)]
    if not st.session_state.gastos_variaveis.empty:
        st.session_state.gastos_variaveis = st.session_state.gastos_variaveis[~st.session_state.gastos_variaveis['id'].isin(ids_treinamento)]
    st.session_state.dados_treinamento_carregados = False
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        ids_str = ','.join([f"'{i}'" for i in ids_treinamento])
        cursor.execute(f"DELETE FROM transacoes WHERE id IN ({ids_str})")
        conn.commit()
        conn.close()
    except:
        pass

# ====================== SEÇÃO 1: APARÊNCIA ======================
st.subheader("🎨 Aparência e Temas")

temas_disponiveis = get_temas_disponiveis()
tema_atual = st.session_state.configuracoes.get("tema", "Claro")

col1, col2 = st.columns([3, 1])

with col1:
    tema_selecionado = st.selectbox(
        "Escolha um tema:",
        temas_disponiveis,
        index=temas_disponiveis.index(tema_atual) if tema_atual in temas_disponiveis else 0,
        format_func=lambda x: f"{get_icone_tema(x)} {x}"
    )
    
    if tema_selecionado != tema_atual:
        st.session_state.configuracoes["tema"] = tema_selecionado
        st.success(f"✅ Tema alterado para {tema_selecionado}!")
        st.rerun()

with col2:
    st.markdown(f"<div style='text-align: center; font-size: 48px;'>{get_icone_tema(tema_atual)}</div>", unsafe_allow_html=True)
    st.caption(f"Tema atual: **{tema_atual}**")

st.markdown("---")

# ====================== SEÇÃO 2: IA E PROVEDORES ======================
st.subheader("🤖 Inteligência Artificial")

# Seletor de provedor
provedores = {
    "groq": "Groq (Recomendado - Grátis e Rápido)",
    "gemini": "Google Gemini (Grátis - Requer chave)",
    "openai": "OpenAI (Pago - ChatGPT)",
    "github": "GitHub Models (Grátis - Beta)",
    "cerebras": "Cerebras (Grátis - Muito Rápido)"
}

provedor_atual = st.session_state.configuracoes.get("llm_provider", "groq")
provedor_selecionado = st.selectbox(
    "Escolha o provedor de IA:",
    options=list(provedores.keys()),
    format_func=lambda x: provedores.get(x, x),
    index=list(provedores.keys()).index(provedor_atual) if provedor_atual in provedores else 0
)

if provedor_selecionado != provedor_atual:
    st.session_state.configuracoes["llm_provider"] = provedor_selecionado
    st.rerun()

st.markdown("---")

# ====================== CONFIGURAÇÃO DA API POR PROVEDOR ======================
st.subheader("🔑 Configuração da API")

# Dicas para cada provedor
dicas_provedores = {
    "groq": """
    **Groq (Recomendado)** ⚡
    - ✅ Totalmente gratuito
    - ✅ Muito rápido
    - ✅ 30 req/minuto
    - 🔑 Obter chave: [console.groq.com](https://console.groq.com/keys)
    """,
    "gemini": """
    **Google Gemini** 
    - ✅ Gratuito (com limites)
    - ⚠️ Chave expira após algum tempo
    - 🔑 Obter chave: [aistudio.google.com](https://aistudio.google.com/)
    """,
    "openai": """
    **OpenAI** 💰
    - ❌ Pago (créditos necessários)
    - 🔑 Obter chave: [platform.openai.com](https://platform.openai.com/api-keys)
    """,
    "github": """
    **GitHub Models** (Beta)
    - ✅ Gratuito (em beta)
    - 🔑 Obter token: [github.com/settings/tokens](https://github.com/settings/tokens)
    """,
    "cerebras": """
    **Cerebras** 🚀
    - ✅ Gratuito
    - ✅ Extremamente rápido
    - 🔑 Obter chave: [api.cerebras.ai](https://api.cerebras.ai/)
    """
}

with st.expander("ℹ️ Dicas para obter sua chave API"):
    st.markdown(dicas_provedores.get(provedor_selecionado, "Selecione um provedor acima"))

# Campo para chave conforme o provedor
chave_map = {
    "groq": "groq_api_key",
    "gemini": "gemini_api_key",
    "openai": "openai_api_key",
    "github": "github_api_key",
    "cerebras": "cerebras_api_key"
}

chave_nome = chave_map.get(provedor_selecionado, "api_key")

# Valor atual da chave
valor_atual = st.session_state.configuracoes.get(chave_nome, "")

api_key = st.text_input(
    f"🔑 {provedores.get(provedor_selecionado, provedor_selecionado).split(' ')[0]} API Key",
    value=valor_atual,
    type="password",
    placeholder="Cole sua chave aqui..."
)

# Botões de ação
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Salvar Chave", use_container_width=True):
        if api_key:
            st.session_state.configuracoes[chave_nome] = api_key
            from src.data_manager import DataManager
            DataManager().save_config(st.session_state.configuracoes)
            st.success(f"✅ Chave salva com sucesso!")
            st.rerun()
        else:
            st.warning("⚠️ Digite uma chave válida")

with col2:
    if st.button("🧪 Testar Conexão", use_container_width=True):
        chave = st.session_state.configuracoes.get(chave_nome, "")
        if not chave:
            st.warning("⚠️ Primeiro salve sua chave")
        else:
            try:
                if provedor_selecionado == "groq":
                    from openai import OpenAI
                    client = OpenAI(
                        base_url="https://api.groq.com/openai/v1",
                        api_key=chave
                    )
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": "Diga 'API funcionando'"}],
                        max_tokens=10
                    )
                    st.success(f"✅ Conexão OK! {response.choices[0].message.content}")
                    st.balloons()
                elif provedor_selecionado == "gemini":
                    import google.generativeai as genai
                    genai.configure(api_key=chave)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content("Diga 'API funcionando'")
                    st.success(f"✅ Conexão OK! {response.text}")
                    st.balloons()
                else:
                    st.info(f"Teste para {provedores.get(provedor_selecionado)} em desenvolvimento")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)[:150]}")

with col3:
    if st.button("🗑️ Remover Chave", use_container_width=True):
        st.session_state.configuracoes[chave_nome] = ""
        from src.data_manager import DataManager
        DataManager().save_config(st.session_state.configuracoes)
        st.success(f"✅ Chave removida!")
        st.rerun()

# Status da IA
st.markdown("---")

chave_salva = st.session_state.configuracoes.get(chave_nome, "")
if chave_salva:
    st.success(f"✅ **Status:** Chave configurada para {provedores.get(provedor_selecionado, provedor_selecionado)}!")
    st.info("💡 O Chat Financeiro usará IA avançada.")
else:
    st.warning(f"⚠️ **Status:** Nenhuma chave configurada. Clique em 'Salvar Chave' após colar sua chave.")

st.markdown("---")

# ====================== CONFIGURAÇÕES DE IA ======================
st.subheader("⚙️ Configurações de IA")

col1, col2 = st.columns(2)
with col1:
    st.session_state.configuracoes["ml_ativado"] = st.toggle(
        "🧠 Ativar Machine Learning", 
        value=st.session_state.configuracoes.get("ml_ativado", True),
        help="Recomendações personalizadas baseadas em ML"
    )

with col2:
    st.session_state.configuracoes["alertas_ativos"] = st.toggle(
        "🔔 Ativar Alertas", 
        value=st.session_state.configuracoes.get("alertas_ativos", True),
        help="Notificações sobre gastos anormais"
    )

st.markdown("---")

# ====================== LIMITES FINANCEIROS ======================
st.subheader("💰 Limites Financeiros")

col1, col2 = st.columns(2)
with col1:
    st.session_state.configuracoes["limite_gastos"] = st.number_input(
        "🎯 Limite de Gastos Mensal (R$)", 
        value=float(st.session_state.configuracoes.get("limite_gastos", 0.0)), 
        step=500.0, 
        format="%.2f",
        help="Receba alertas quando seus gastos se aproximarem deste limite"
    )

with col2:
    st.session_state.configuracoes["salario_mensal"] = st.number_input(
        "💰 Salário de Referência (R$)", 
        value=float(st.session_state.configuracoes.get("salario_mensal", 0.0)), 
        step=500.0, 
        format="%.2f",
        help="Usado para calcular proporções e recomendações"
    )

st.markdown("---")

# ====================== DADOS DE TREINAMENTO ======================
st.subheader("📊 Dados de Treinamento")

col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Carregar Dados de Exemplo", use_container_width=True, help="Carrega dados fictícios para teste"):
        carregar_dados_treinamento()
        st.success("✅ Dados de exemplo carregados!")
        st.rerun()

with col2:
    if st.session_state.dados_treinamento_carregados:
        if st.button("🗑️ Remover Dados de Exemplo", use_container_width=True):
            remover_dados_treinamento()
            st.success("✅ Dados de exemplo removidos!")
            st.rerun()

st.markdown("---")

# ====================== IMPORTAR CSV ======================
st.subheader("📥 Importar CSV")

uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.info(f"📄 {len(df)} linhas encontradas")
        
        if st.button("✅ Confirmar Importação", use_container_width=True):
            for _, row in df.iterrows():
                desc = row.get('Descrição', row.get('descricao', row.get('Descricao', 'Importado')))
                valor = float(row.get('Valor', row.get('valor', 0)))
                data = row.get('Data', row.get('data', datetime.now()))
                categoria = row.get('Categoria', row.get('categoria', 'Renda' if valor > 0 else 'Outros'))
                
                if valor > 0:
                    nova = pd.DataFrame({
                        "Descrição": [desc],
                        "Valor": [valor],
                        "Categoria": [categoria],
                        "Data": [pd.to_datetime(data)],
                        "id": [str(uuid.uuid4())[:8]],
                        "Status": ["Pago"]
                    })
                    st.session_state.receitas = pd.concat([st.session_state.receitas, nova], ignore_index=True)
                else:
                    nova = pd.DataFrame({
                        "Descrição": [desc],
                        "Valor": [valor],
                        "Categoria": [categoria],
                        "Data": [pd.to_datetime(data)],
                        "id": [str(uuid.uuid4())[:8]],
                        "Status": ["Pago"]
                    })
                    st.session_state.gastos_variaveis = pd.concat([st.session_state.gastos_variaveis, nova], ignore_index=True)
            
            salvar_todas_no_banco()
            st.success("✅ Importação concluída!")
            st.rerun()
    except Exception as e:
        st.error(f"Erro: {e}")

st.markdown("---")

# ====================== GERENCIAMENTO ======================
st.subheader("🗄️ Gerenciamento")

stats = db.estatisticas()
st.caption(f"📊 {stats['total_transacoes']} transações no banco de dados")

col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Fazer Backup", use_container_width=True):
        backup_path = db.fazer_backup()
        st.success(f"✅ Backup criado com sucesso!")

with col2:
    df = carregar_todas_transacoes_local()
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Exportar CSV", 
            csv, 
            f"adaptfin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
            "text/csv",
            use_container_width=True
        )
    else:
        st.button("📥 Exportar CSV", disabled=True, use_container_width=True)

st.markdown("---")

# ====================== RESET DO SISTEMA ======================
st.subheader("⚠️ Resetar Sistema")

with st.expander("🚨 Resetar Banco de Dados (Irreversível)"):
    st.warning("⚠️ Esta ação apaga TODOS os dados permanentemente!")
    st.caption("Isso inclui: transações, metas, configurações e histórico.")
    
    col1, col2 = st.columns(2)
    with col1:
        confirmar = st.text_input("Digite 'RESETAR' para confirmar", type="password")
    with col2:
        if confirmar == "RESETAR":
            if st.button("🗑️ Resetar Banco", type="primary", use_container_width=True):
                try:
                    conn = sqlite3.connect(db.db_path)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM transacoes")
                    cursor.execute("DELETE FROM configuracoes")
                    cursor.execute("DELETE FROM metas")
                    cursor.execute("DELETE FROM log_alteracoes")
                    conn.commit()
                    conn.close()
                    
                    st.session_state.receitas = pd.DataFrame()
                    st.session_state.despesas_fixas = pd.DataFrame()
                    st.session_state.gastos_variaveis = pd.DataFrame()
                    st.session_state.dados_carregados_banco = False
                    st.session_state.dados_treinamento_carregados = False
                    
                    st.success("✅ Banco de dados resetado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao resetar: {e}")
        else:
            st.caption("Digite RESETAR para habilitar")

st.markdown("---")

# ====================== SOBRE ======================
st.subheader("📄 Sobre o AdaptFin")

st.markdown("""
**AdaptFin v2.0** - Assistente Financeiro Adaptativo

**Funcionalidades:**
- 📊 Dashboard interativo
- 💰 Gestão de transações
- 📈 Relatórios financeiros
- 🤖 Machine Learning
- 💬 Chat IA (múltiplos provedores)
- 🎯 Metas financeiras

**Provedores de IA suportados:**
- 🚀 Groq (Recomendado - Grátis)
- 🔵 Google Gemini (Grátis)
- 🟢 OpenAI (Pago)
- ⚫ GitHub Models (Grátis - Beta)
- 🟠 Cerebras (Grátis)

*"Em vez de você se adaptar ao app, o app se adapta a você"*
""")

# ====================== SALVAR CONFIGURAÇÕES ======================
from src.data_manager import DataManager
DataManager().save_config(st.session_state.configuracoes)

st.markdown("---")
st.caption("⚙️ Configurações salvas automaticamente")