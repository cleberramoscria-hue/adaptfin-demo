import pandas as pd

def process_data(df_transacoes, df_despesas_fixas):
    df = df_transacoes.copy()
    if 'Data' not in df.columns:
        df['Data'] = pd.Timestamp.now().date()
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    df = df.dropna(subset=['Valor'])
    if not df_despesas_fixas.empty:
        df_despesas_fixas['Valor'] = pd.to_numeric(df_despesas_fixas['Valor'], errors='coerce')
        df_despesas_fixas = df_despesas_fixas.dropna(subset=['Valor'])
        if 'Data' not in df_despesas_fixas.columns:
            df_despesas_fixas['Data'] = pd.Timestamp.now().date()
        df = pd.concat([df, df_despesas_fixas], ignore_index=True)
    return df

def categorize_transactions(df):
    df = df.copy()
    if 'Categoria' not in df.columns:
        df['Categoria'] = 'Outros'
    
    categorias = {
        'Alimentação': ['supermercado', 'mercado', 'ifood', 'restaurante', 'padaria', 'feira', 'comida'],
        'Transporte': ['uber', 'taxi', '99', 'combustivel', 'gasolina', 'estacionamento'],
        'Moradia': ['aluguel', 'condominio', 'energia', 'agua', 'gas', 'iptu', 'internet', 'telefone'],
        'Saúde': ['farmacia', 'medico', 'dentista', 'hospital'],
        'Educação': ['faculdade', 'curso', 'escola', 'livro', 'material'],
        'Lazer': ['cinema', 'teatro', 'show', 'parque', 'bar', 'viagem'],
        'Serviços': ['netflix', 'spotify', 'streaming', 'assinatura'],
    }
    
    for idx, row in df.iterrows():
        descricao = str(row['Descrição']).lower()
        if row['Categoria'] != 'Outros':
            continue
        for categoria, palavras in categorias.items():
            if any(palavra in descricao for palavra in palavras):
                df.at[idx, 'Categoria'] = categoria
                break
        if row['Valor'] > 0 and df.at[idx, 'Categoria'] == 'Outros':
            df.at[idx, 'Categoria'] = 'Renda'
    return df