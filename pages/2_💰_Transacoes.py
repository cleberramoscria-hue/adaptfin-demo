import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
from utils.theme_utils import aplicar_tema_global

# Aplicar tema
aplicar_tema_global()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.format_utils import format_currency
from utils.constants import CATEGORIAS_RECEITA, CATEGORIAS_DESPESA

st.set_page_config(page_title="Transações - AdaptFin", page_icon="💰", layout="wide")

def formatar_moeda(valor):
    return format_currency(valor)

def formatar_data_br(data):
    if pd.isna(data):
        return "N/A"
    try:
        if isinstance(data, str):
            data = pd.to_datetime(data, errors='coerce')
        if pd.isna(data):
            return "N/A"
        return data.strftime("%d/%m/%Y")
    except:
        return "N/A"

def gerar_id():
    import uuid
    return str(uuid.uuid4())[:8]

# ====================== INICIALIZAÇÃO DO SESSION STATE ======================
if "receitas" not in st.session_state:
    st.session_state.receitas = pd.DataFrame(columns=["Descrição", "Valor", "Categoria", "Data", "id", "Status"])
if "despesas_fixas" not in st.session_state:
    st.session_state.despesas_fixas = pd.DataFrame(columns=["Descrição", "Valor", "Categoria", "Data", "id", "Status"])
if "gastos_variaveis" not in st.session_state:
    st.session_state.gastos_variaveis = pd.DataFrame(columns=["Descrição", "Valor", "Categoria", "Data", "id", "Status"])
if "contas_recorrentes" not in st.session_state:
    st.session_state.contas_recorrentes = pd.DataFrame(columns=["id", "Tipo", "Descrição", "Valor", "Categoria", "DiaVencimento", "NumMeses", "DataInicio", "GrupoId"])

# ====================== FUNÇÃO PARA VERIFICAR DUPLICIDADE ======================
def verificar_duplicidade(tipo, descricao, valor, data):
    """Verifica se já existe uma transação similar"""
    if tipo == "Receita":
        df = st.session_state.receitas
    elif tipo == "Despesa Fixa":
        df = st.session_state.despesas_fixas
    else:
        df = st.session_state.gastos_variaveis
    
    if df.empty:
        return False, None
    
    # Verificar se existe com mesma descrição e valor (ignorando sinal)
    valor_abs = abs(valor)
    for _, row in df.iterrows():
        if row['Descrição'].lower() == descricao.lower() and abs(row['Valor']) == valor_abs:
            return True, row
    
    return False, None

# ====================== FUNÇÕES ======================
def salvar_dados():
    from src.data_manager import DataManager
    data_manager = DataManager()
    todas = []
    if not st.session_state.receitas.empty:
        todas.append(st.session_state.receitas)
    if not st.session_state.despesas_fixas.empty:
        todas.append(st.session_state.despesas_fixas)
    if not st.session_state.gastos_variaveis.empty:
        todas.append(st.session_state.gastos_variaveis)
    
    if todas:
        df_total = pd.concat(todas, ignore_index=True)
        data_manager.save_transactions(df_total)

def excluir_transacao(tipo, index):
    if tipo == "receitas":
        st.session_state.receitas = st.session_state.receitas.drop(index).reset_index(drop=True)
    elif tipo == "despesas_fixas":
        st.session_state.despesas_fixas = st.session_state.despesas_fixas.drop(index).reset_index(drop=True)
    elif tipo == "gastos_variaveis":
        st.session_state.gastos_variaveis = st.session_state.gastos_variaveis.drop(index).reset_index(drop=True)
    salvar_dados()
    st.rerun()

# ====================== FILTROS ======================
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros")

# Obter anos disponíveis dos dados
def obter_anos_disponiveis():
    anos = set()
    if not st.session_state.receitas.empty and 'Data' in st.session_state.receitas.columns:
        anos.update(pd.to_datetime(st.session_state.receitas['Data']).dt.year.dropna().astype(int))
    if not st.session_state.despesas_fixas.empty and 'Data' in st.session_state.despesas_fixas.columns:
        anos.update(pd.to_datetime(st.session_state.despesas_fixas['Data']).dt.year.dropna().astype(int))
    if not st.session_state.gastos_variaveis.empty and 'Data' in st.session_state.gastos_variaveis.columns:
        anos.update(pd.to_datetime(st.session_state.gastos_variaveis['Data']).dt.year.dropna().astype(int))
    
    if not anos:
        anos.add(datetime.now().year)
    
    return sorted(anos)

anos_disponiveis = obter_anos_disponiveis()
ano_selecionado = st.sidebar.selectbox("Ano", anos_disponiveis, index=len(anos_disponiveis)-1)

meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
               "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
mes_selecionado = st.sidebar.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1,
                                       format_func=lambda x: meses_nomes[x-1])
status_filtro = st.sidebar.multiselect("Status", ["Pago", "Pendente"], default=["Pago", "Pendente"])

def filtrar_por_mes(df, ano, mes):
    if df.empty or 'Data' not in df.columns:
        return df
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data'])
    if df.empty:
        return df
    return df[(df['Data'].dt.year == ano) & (df['Data'].dt.month == mes)]

st.title("💰 Gestão de Transações")
st.markdown("---")

# ====================== RESUMO DO MÊS ======================
st.subheader(f"📊 Resumo de {meses_nomes[mes_selecionado-1]} de {ano_selecionado}")

# Calcular totais
todas = []
if not st.session_state.receitas.empty:
    todas.append(st.session_state.receitas)
if not st.session_state.despesas_fixas.empty:
    todas.append(st.session_state.despesas_fixas)
if not st.session_state.gastos_variaveis.empty:
    todas.append(st.session_state.gastos_variaveis)

if todas:
    df_total = pd.concat(todas, ignore_index=True)
    if 'Data' in df_total.columns:
        df_total['Data'] = pd.to_datetime(df_total['Data'], errors='coerce')
    
    df_mes = filtrar_por_mes(df_total, ano_selecionado, mes_selecionado)
    df_mes = df_mes[df_mes['Status'].isin(status_filtro)]
    
    total_receitas = df_mes[df_mes['Valor'] > 0]['Valor'].sum()
    total_despesas = abs(df_mes[df_mes['Valor'] < 0]['Valor'].sum())
    saldo = total_receitas - total_despesas
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Receitas", formatar_moeda(total_receitas))
    with col2:
        st.metric("📤 Despesas", formatar_moeda(total_despesas))
    with col3:
        st.metric("💵 Saldo", formatar_moeda(saldo), delta_color="inverse" if saldo < 0 else "normal")

st.markdown("---")

# ====================== ABAS ======================
tabs = st.tabs(["➕ Adicionar", "💰 Receitas", "🏠 Despesas Fixas", "🛍️ Gastos Variáveis"])

# ====================== ABA 1: ADICIONAR ======================
with tabs[0]:
    st.subheader("➕ Adicionar Nova Transação")
    
    tipo = st.radio("Tipo", ["Receita", "Despesa Fixa", "Gasto Variável"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        descricao = st.text_input("Descrição", placeholder="Ex: Salário, Aluguel...")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=50.0, format="%.2f", value=0.0)
    
    # Categorias baseadas no tipo
    if tipo == "Receita":
        categorias = CATEGORIAS_RECEITA[:8]
    else:
        categorias = CATEGORIAS_DESPESA[:10]
    
    categoria = st.selectbox("Categoria", categorias)
    
    # Data no formato brasileiro
    data = st.date_input("Data", value=datetime.now().date(), format="DD/MM/YYYY")
    st.caption(f"Data selecionada: {data.strftime('%d/%m/%Y')}")
    
    # Verificar duplicidade antes de adicionar
    if descricao and valor > 0:
        duplicado, item_existente = verificar_duplicidade(tipo, descricao, valor, data)
        if duplicado:
            st.warning(f"⚠️ ATENÇÃO: Já existe uma transação similar!")
            st.info(f"📌 '{item_existente['Descrição']}' - {formatar_moeda(abs(item_existente['Valor']))} em {formatar_data_br(item_existente['Data'])}")
    
    if st.button("✅ Adicionar", use_container_width=True):
        if descricao and valor > 0:
            # Verificar duplicidade novamente (por segurança)
            duplicado, _ = verificar_duplicidade(tipo, descricao, valor, data)
            
            if duplicado:
                st.error("❌ Transação duplicada! Não foi adicionada.")
            else:
                valor_final = valor if tipo == "Receita" else -valor
                status = "Pendente" if data > datetime.now().date() else "Pago"
                
                nova = pd.DataFrame({
                    "Descrição": [descricao],
                    "Valor": [valor_final],
                    "Categoria": [categoria],
                    "Data": [pd.to_datetime(data)],
                    "id": [gerar_id()],
                    "Status": [status]
                })
                
                if tipo == "Receita":
                    st.session_state.receitas = pd.concat([st.session_state.receitas, nova], ignore_index=True)
                elif tipo == "Despesa Fixa":
                    st.session_state.despesas_fixas = pd.concat([st.session_state.despesas_fixas, nova], ignore_index=True)
                else:
                    st.session_state.gastos_variaveis = pd.concat([st.session_state.gastos_variaveis, nova], ignore_index=True)
                
                salvar_dados()
                st.success(f"✅ {tipo} de {formatar_moeda(valor)} adicionada!")
                st.rerun()
        else:
            st.error("❌ Preencha todos os campos")

# ====================== ABA 2: RECEITAS ======================
with tabs[1]:
    st.subheader("💰 Lista de Receitas")
    
    if not st.session_state.receitas.empty:
        df = st.session_state.receitas.copy()
        df_filtrado = filtrar_por_mes(df, ano_selecionado, mes_selecionado)
        df_filtrado = df_filtrado[df_filtrado['Status'].isin(status_filtro)]
        
        if not df_filtrado.empty:
            for idx, row in df_filtrado.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1, 0.8])
                
                with col1:
                    st.write(f"**{row['Descrição']}**")
                with col2:
                    st.write(formatar_moeda(row['Valor']))
                with col3:
                    st.write(formatar_data_br(row['Data']))
                with col4:
                    st.write(f"{'🟢' if row['Status'] == 'Pago' else '🟡'} {row['Status']}")
                with col5:
                    if st.button("🗑️", key=f"del_rec_{idx}"):
                        excluir_transacao("receitas", idx)
                        st.rerun()
                st.divider()
            
            st.metric("💰 Total de Receitas", formatar_moeda(df_filtrado['Valor'].sum()))
        else:
            st.info("Nenhuma receita no período selecionado")
    else:
        st.info("Nenhuma receita cadastrada")

# ====================== ABA 3: DESPESAS FIXAS ======================
with tabs[2]:
    st.subheader("🏠 Lista de Despesas Fixas")
    
    if not st.session_state.despesas_fixas.empty:
        df = st.session_state.despesas_fixas.copy()
        df_filtrado = filtrar_por_mes(df, ano_selecionado, mes_selecionado)
        df_filtrado = df_filtrado[df_filtrado['Status'].isin(status_filtro)]
        
        if not df_filtrado.empty:
            for idx, row in df_filtrado.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1, 0.8])
                
                with col1:
                    st.write(f"**{row['Descrição']}**")
                with col2:
                    st.write(formatar_moeda(abs(row['Valor'])))
                with col3:
                    st.write(formatar_data_br(row['Data']))
                with col4:
                    st.write(f"{'🟢' if row['Status'] == 'Pago' else '🟡'} {row['Status']}")
                with col5:
                    if st.button("🗑️", key=f"del_fix_{idx}"):
                        excluir_transacao("despesas_fixas", idx)
                        st.rerun()
                st.divider()
            
            st.metric("🏠 Total de Despesas Fixas", formatar_moeda(abs(df_filtrado['Valor'].sum())))
        else:
            st.info("Nenhuma despesa fixa no período selecionado")
    else:
        st.info("Nenhuma despesa fixa cadastrada")

# ====================== ABA 4: GASTOS VARIÁVEIS ======================
with tabs[3]:
    st.subheader("🛍️ Lista de Gastos Variáveis")
    
    if not st.session_state.gastos_variaveis.empty:
        df = st.session_state.gastos_variaveis.copy()
        df_filtrado = filtrar_por_mes(df, ano_selecionado, mes_selecionado)
        df_filtrado = df_filtrado[df_filtrado['Status'].isin(status_filtro)]
        
        if not df_filtrado.empty:
            for idx, row in df_filtrado.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1, 0.8])
                
                with col1:
                    st.write(f"**{row['Descrição']}**")
                with col2:
                    st.write(formatar_moeda(abs(row['Valor'])))
                with col3:
                    st.write(formatar_data_br(row['Data']))
                with col4:
                    st.write(f"{'🟢' if row['Status'] == 'Pago' else '🟡'} {row['Status']}")
                with col5:
                    if st.button("🗑️", key=f"del_gas_{idx}"):
                        excluir_transacao("gastos_variaveis", idx)
                        st.rerun()
                st.divider()
            
            st.metric("🛍️ Total de Gastos Variáveis", formatar_moeda(abs(df_filtrado['Valor'].sum())))
        else:
            st.info("Nenhum gasto variável no período selecionado")
    else:
        st.info("Nenhum gasto variável cadastrado")

st.markdown("---")
st.caption("💡 As transações são salvas automaticamente | Data no formato DD/MM/YYYY")