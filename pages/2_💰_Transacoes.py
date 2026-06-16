import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.theme_utils import aplicar_tema_global

# ====================== INICIALIZAR SESSION STATE ======================
if "configuracoes" not in st.session_state:
    st.session_state.configuracoes = {
        "salario_mensal": 0.0,
        "limite_gastos": 0.0,
        "alertas_ativos": True,
        "ml_ativado": True,
        "tema": "Claro"
    }

# Aplicar tema
aplicar_tema_global()

st.set_page_config(page_title="Transações - AdaptFin", page_icon="💰", layout="wide")

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

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

def obter_nome_descricao(df):
    """Retorna o nome correto da coluna de descrição"""
    if df is None or df.empty:
        return None
    colunas = df.columns.tolist()
    for nome in ['Descricao', 'Descrição', 'descricao', 'descrição']:
        if nome in colunas:
            return nome
    return None

st.title("💰 Gestão de Transações")
st.markdown("---")

# Inicializar session state
if "receitas" not in st.session_state:
    st.session_state.receitas = pd.DataFrame()
if "despesas_fixas" not in st.session_state:
    st.session_state.despesas_fixas = pd.DataFrame()
if "gastos_variaveis" not in st.session_state:
    st.session_state.gastos_variaveis = pd.DataFrame()

# ====================== FILTROS ======================
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros")

def obter_anos_disponiveis():
    anos = set()
    for df in [st.session_state.receitas, st.session_state.despesas_fixas, st.session_state.gastos_variaveis]:
        if not df.empty and 'Data' in df.columns:
            anos.update(pd.to_datetime(df['Data']).dt.year.dropna().astype(int))
    if not anos:
        anos.add(datetime.now().year)
    return sorted(anos)

anos_disponiveis = obter_anos_disponiveis()
ano_selecionado = st.sidebar.selectbox("Ano", anos_disponiveis, index=len(anos_disponiveis)-1)

meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
               "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
mes_selecionado = st.sidebar.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1,
                                       format_func=lambda x: meses_nomes[x-1])

def filtrar_por_mes(df, ano, mes):
    if df.empty or 'Data' not in df.columns:
        return df
    df = df.copy()
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data'])
    if df.empty:
        return df
    return df[(df['Data'].dt.year == ano) & (df['Data'].dt.month == mes)]

# ====================== RESUMO DO MÊS ======================
st.subheader(f"📊 Resumo de {meses_nomes[mes_selecionado-1]} de {ano_selecionado}")

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
    
    total_receitas = df_mes[df_mes['Valor'] > 0]['Valor'].sum() if not df_mes.empty else 0
    total_despesas = abs(df_mes[df_mes['Valor'] < 0]['Valor'].sum()) if not df_mes.empty else 0
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
    
    categorias_receita = ["Renda", "Salário", "Freelance", "Investimentos", "Bônus", "Extra"]
    categorias_despesa = ["Moradia", "Alimentação", "Transporte", "Lazer", "Saúde", "Serviços", "Educação", "Outros"]
    
    if tipo == "Receita":
        categorias = categorias_receita
    else:
        categorias = categorias_despesa
    
    categoria = st.selectbox("Categoria", categorias)
    data = st.date_input("Data", value=datetime.now().date())
    st.caption(f"Data selecionada: {data.strftime('%d/%m/%Y')}")
    
    if st.button("✅ Adicionar", use_container_width=True):
        if descricao and valor > 0:
            valor_final = valor if tipo == "Receita" else -valor
            nova = pd.DataFrame({
                "Descricao": [descricao],
                "Valor": [valor_final],
                "Categoria": [categoria],
                "Data": [pd.to_datetime(data)],
                "id": [str(uuid.uuid4())[:8]]
            })
            
            if tipo == "Receita":
                st.session_state.receitas = pd.concat([st.session_state.receitas, nova], ignore_index=True)
            elif tipo == "Despesa Fixa":
                st.session_state.despesas_fixas = pd.concat([st.session_state.despesas_fixas, nova], ignore_index=True)
            else:
                st.session_state.gastos_variaveis = pd.concat([st.session_state.gastos_variaveis, nova], ignore_index=True)
            
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
        
        if not df_filtrado.empty:
            # Descobrir nome da coluna de descrição
            col_desc = obter_nome_descricao(df_filtrado)
            
            for idx, row in df_filtrado.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 0.8])
                
                with col1:
                    if col_desc:
                        st.write(f"**{row[col_desc]}**")
                    else:
                        st.write(f"**{row.get('Descricao', row.get('Descrição', 'Sem descrição'))}**")
                with col2:
                    st.write(formatar_moeda(row['Valor']))
                with col3:
                    st.write(formatar_data_br(row['Data']))
                with col4:
                    if st.button("🗑️", key=f"del_rec_{idx}"):
                        st.session_state.receitas = st.session_state.receitas.drop(idx).reset_index(drop=True)
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
        
        if not df_filtrado.empty:
            col_desc = obter_nome_descricao(df_filtrado)
            
            for idx, row in df_filtrado.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 0.8])
                
                with col1:
                    if col_desc:
                        st.write(f"**{row[col_desc]}**")
                    else:
                        st.write(f"**{row.get('Descricao', row.get('Descrição', 'Sem descrição'))}**")
                with col2:
                    st.write(formatar_moeda(abs(row['Valor'])))
                with col3:
                    st.write(formatar_data_br(row['Data']))
                with col4:
                    if st.button("🗑️", key=f"del_fix_{idx}"):
                        st.session_state.despesas_fixas = st.session_state.despesas_fixas.drop(idx).reset_index(drop=True)
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
        
        if not df_filtrado.empty:
            col_desc = obter_nome_descricao(df_filtrado)
            
            for idx, row in df_filtrado.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 0.8])
                
                with col1:
                    if col_desc:
                        st.write(f"**{row[col_desc]}**")
                    else:
                        st.write(f"**{row.get('Descricao', row.get('Descrição', 'Sem descrição'))}**")
                with col2:
                    st.write(formatar_moeda(abs(row['Valor'])))
                with col3:
                    st.write(formatar_data_br(row['Data']))
                with col4:
                    if st.button("🗑️", key=f"del_gas_{idx}"):
                        st.session_state.gastos_variaveis = st.session_state.gastos_variaveis.drop(idx).reset_index(drop=True)
                        st.rerun()
                st.divider()
            
            st.metric("🛍️ Total de Gastos Variáveis", formatar_moeda(abs(df_filtrado['Valor'].sum())))
        else:
            st.info("Nenhum gasto variável no período selecionado")
    else:
        st.info("Nenhum gasto variável cadastrado")

st.markdown("---")
st.caption("💡 As transações são salvas automaticamente | Data no formato DD/MM/YYYY")