# ============================================
# automation_engine.py (AGORA SUPORTA TIRAR SCREENSHOT)
# Motor de execução que lê o JSON e executa as ações
# ============================================
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 🔑 Importar TODAS as ações
from web_actions import (
    abrir_site, 
    preencher_campo, 
    clicar_elemento, 
    validar_texto_esperado,
    esperar_por_alerta,
    esperar_por_visibilidade, 
    esperar_por_invisibilidade,
    tirar_screenshot # FUNÇÃO IMPORTADA
)

# Mapeamento: NOME DA AÇÃO NO JSON -> FUNÇÃO
ACTION_MAP = {
    "abrir_site": abrir_site,
    "preencher_campo": preencher_campo,
    "clicar_elemento": clicar_elemento,
    "validar_texto_esperado": validar_texto_esperado,
    "esperar_por_alerta": esperar_por_alerta, 
    "esperar_por_visibilidade": esperar_por_visibilidade, 
    "esperar_por_invisibilidade": esperar_por_invisibilidade,
    "tirar_screenshot": tirar_screenshot, # MAPEADO
}

def _inicializar_driver():
    """Inicializa o driver do Chrome com opções otimizadas."""
    options = Options()
    
    # Opções para minimizar a interferência do navegador
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_argument("--start-maximized")
    
    # Prefs de idioma e notificações 
    prefs = {
        "profile.default_content_settings.popups": 2, 
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)

    try:
        driver = webdriver.Chrome(options=options)
        print("🚀 Navegador Chrome inicializado.")
        return driver
    except Exception as e:
        print(f"❌ Erro ao inicializar o ChromeDriver: {e}")
        return None

def executar_automacao(json_acoes: str) -> str:
    """Executa o script de automação lendo o JSON de ações."""
    driver = None
    log_execucao = []
    
    try:
        # Tenta carregar o script JSON
        script = json.loads(json_acoes)
        acoes = script.get('script_acoes', [])
        
        driver = _inicializar_driver()
        if not driver:
            log_execucao.append("❌ Falha na inicialização do driver.")
            return "\n".join(log_execucao)

        # Execução do loop de ações
        for item in acoes:
            acao = item.get("acao")
            parametros = item.get("parametros", [])
            
            if acao in ACTION_MAP:
                funcao = ACTION_MAP[acao]
                
                # Tratamento especial para tirar_screenshot (apenas nome do arquivo)
                if acao == "tirar_screenshot":
                    funcao(driver, *parametros)
                    log_execucao.append(f"➡️ Executando: {acao} com nome: {parametros[0]}")
                    
                # Tratamento para ações que usam seletor
                elif acao in ["preencher_campo", "clicar_elemento", "validar_texto_esperado", "esperar_por_visibilidade", "esperar_por_invisibilidade"]:
                    
                    if not parametros:
                        log_execucao.append(f"⚠️ Ação '{acao}' requer um seletor e/ou texto. Ignorando.")
                        continue
                        
                    seletor_id = parametros.pop(0) 
                    
                    # LÓGICA DE SELETOR
                    if seletor_id.startswith('//'):
                        seletor_selenium = (By.XPATH, seletor_id)
                    elif seletor_id == 'body':
                        seletor_selenium = (By.TAG_NAME, seletor_id)
                    elif seletor_id in ['btn-primary', 'btn-success']: # Classes comuns no Demoblaze
                         seletor_selenium = (By.CLASS_NAME, seletor_id)
                    else:
                        seletor_selenium = (By.ID, seletor_id) 
                    
                    funcao(driver, seletor_selenium, *parametros) 
                    log_execucao.append(f"➡️ Executando: {acao} com seletor: {seletor_id}")
                
                # Tratamento para a função de alerta
                elif acao == "esperar_por_alerta": 
                    funcao(driver, *parametros)
                    log_execucao.append(f"➡️ Executando: {acao} com parâmetros: {parametros}")
                
                # Tratamento para abrir_site
                else:
                    funcao(driver, *parametros)
                    log_execucao.append(f"➡️ Executando: {acao} com parâmetros: {parametros}")
                    
                time.sleep(0.5) # Pequena pausa entre ações para estabilidade

        log_execucao.append("\n✅ Automação de script concluída com sucesso!")
        return "\n".join(log_execucao)

    except Exception as e:
        log_execucao.append(f"\n❌ Erro durante a execução da automação: {e}")
        return "\n".join(log_execucao)
        
    finally:
        if driver:
            driver.quit()
            log_execucao.append("✅ Navegador fechado.")