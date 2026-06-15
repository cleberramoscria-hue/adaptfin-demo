def generate_recommendation(df_transacoes):
    entradas = df_transacoes[df_transacoes['Valor'] > 0]['Valor'].sum()
    saidas = abs(df_transacoes[df_transacoes['Valor'] < 0]['Valor'].sum())
    saldo = entradas - saidas
    
    recomendacao = {"status": "success", "mensagem": "", "total_divida": 0}
    
    if saldo < 0:
        recomendacao["status"] = "danger"
        recomendacao["total_divida"] = abs(saldo)
        recomendacao["mensagem"] = f"⚠️ Déficit de R$ {abs(saldo):,.2f}. Reduza gastos!"
    elif entradas > 0 and saldo < entradas * 0.1:
        recomendacao["status"] = "warning"
        recomendacao["mensagem"] = f"⚡ Economize mais! Saldo é {saldo/entradas*100:.1f}% das entradas"
    elif entradas > 0 and saidas > entradas * 0.7:
        recomendacao["mensagem"] = f"📊 Você gasta {saidas/entradas*100:.1f}% do que ganha"
    elif saldo > 0 and entradas > 0:
        recomendacao["mensagem"] = f"✅ Ótimo! Sobrou R$ {saldo:,.2f} ({saldo/entradas*100:.1f}%)"
    else:
        recomendacao["mensagem"] = "✅ Suas finanças estão equilibradas!"
    
    return recomendacao