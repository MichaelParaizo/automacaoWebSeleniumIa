# ============================================
# app.py (AJUSTADO: NOVA URL DE TESTE)
# Interface Streamlit para o Mentor de Automação Web com IA
# ============================================

import streamlit as st
import json

# Importar as funções necessárias
from ai_interpreter import interpretar_comando
from automation_engine import executar_automacao 

# --- Configuração da Interface ---
st.set_page_config(page_title="Automação Web Selenium com IA", layout="wide")

# Título Principal (Não alterado)
st.title("Automação Web Selenium com IA 🤖")
# DESCRIÇÃO ALTERADA para o novo site
st.markdown("Descreva a tarefa de automação que você quer executar em linguagem natural (Site de Teste: `https://www.demoblaze.com/`).")

# --- Entrada do Usuário ---
# Rótulo e Placeholder mantidos
comando_usuario = st.text_area(
    "Comando de Automação", 
    value="",
    placeholder="digite o comando aqui...",
    height=150
)

# --- Botão de Execução ---
if st.button("Executar Automação Guiada por IA"):
    if not comando_usuario:
        st.warning("Por favor, digite um comando de automação.")
    else:
        st.info(f"Analisando comando: {comando_usuario}")
        
        st.markdown("---")
        st.subheader("Passo 1/2: Interpretando comando com IA (Gerando o Script JSON)")

        try:
            # 1. Chamar a IA para gerar o JSON de ações
            json_acoes = interpretar_comando(comando_usuario)
            
            # Tenta carregar o JSON para exibição formatada
            acoes_carregadas = json.loads(json_acoes)
            
            # Exibe o JSON completo gerado pela IA
            st.code(json.dumps(acoes_carregadas, indent=2), language='json')
            
            if 'script_acoes' in acoes_carregadas and acoes_carregadas['script_acoes']:
                 st.success("✅ Plano de Ação Completo gerado com sucesso!")
            elif acoes_carregadas.get("erro"):
                 st.error(f"❌ Erro na Geração do Plano de Ação: {acoes_carregadas.get('erro')}")
            else:
                 st.warning("⚠️ A IA gerou o JSON, mas ele está vazio ou incompleto.")

            st.markdown("---")
            
            # 2. Executar a automação (só se não houver erro de IA)
            if 'script_acoes' in acoes_carregadas:
                st.subheader("Passo 2/2: Executando ações no Selenium...")
                
                # Executa o motor de automação e recebe o log completo
                log_completo = executar_automacao(json_acoes) 
                
                # Lógica para verificar o erro no log
                if "❌ Erro" in log_completo or "Validação FALHOU" in log_completo:
                    st.error("❌ Automação Falhou! Verifique o Log de Execução abaixo.")
                else:
                    st.success("✅ Automação de script concluída com sucesso!")
                    
                st.subheader("Log de Execução do Selenium:")
                # Exibe o log completo que contém os detalhes da execução
                st.code(log_completo, language='text') 

        except json.JSONDecodeError:
             st.error("❌ Erro fatal: O retorno da IA não é um JSON válido. Verifique a chave da API.")
             st.code(json_acoes)
        except Exception as e:
             st.error(f"❌ Erro Inesperado: {e}")