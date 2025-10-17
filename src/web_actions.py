# ============================================
# web_actions.py (AGORA INCLUI tirar_screenshot)
# Funções de baixo nível para interação com o Selenium
# ============================================

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as ec 
import os
import time

# --- Variável Global para o Diretório de Evidências ---
# Cria um diretório de screenshots único por execução
EVIDENCE_DIR = os.path.join(os.getcwd(), 'evidencias', time.strftime("%Y%m%d_%H%M%S"))
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# 🟢 NOVA FUNÇÃO ADICIONADA: tirar_screenshot
def tirar_screenshot(driver, nome_arquivo: str):
    """
    Captura uma screenshot e salva no diretório de evidências.
    """
    try:
        caminho_completo = os.path.join(EVIDENCE_DIR, f"{nome_arquivo}.png")
        driver.save_screenshot(caminho_completo)
        print(f"📸 Screenshot salva em: {caminho_completo}")
    except Exception as e:
        print(f"❌ Erro ao tirar screenshot: {e}")

# ... (MANTENHA TODAS AS OUTRAS FUNÇÕES ABAIXO INALTERADAS) ...

def abrir_site(driver, url: str):
    """Abre um site na URL fornecida."""
    print(f"🌐 Acessando: {url}")
    driver.get(url)

def preencher_campo(driver, seletor: tuple, texto: str):
    # ... (código inalterado) ...
    """
    Preenche um campo de texto, usando Espera Híbrida/Agressiva (SendKeys + JS Fallback).
    """
    seletor_tipo = seletor[0]
    seletor_valor = seletor[1]
    elemento = None
    
    try:
        wait = WebDriverWait(driver, 10)
        
        # 1. Espera que o elemento esteja PRESENTE
        elemento = wait.until(
            ec.presence_of_element_located(seletor)
        )
        
        # 2. Tenta preencher (Ação normal)
        elemento.clear()
        elemento.send_keys(texto)
        print(f"✍️ Campo ('{seletor_tipo}', '{seletor_valor}') preenchido com: {texto}")
        
    except Exception:
        # Se falhou, tenta preencher forçado via JavaScript
        if elemento:
            try:
                driver.execute_script(f"arguments[0].value='{texto}';", elemento)
                print(f"⚠️ Campo ('{seletor_tipo}', '{seletor_valor}') falhou. Preenchimento JS forçado com: {texto}")
            except:
                print(f"⚠️ Campo ('{seletor_tipo}', '{seletor_valor}') falhou no preenchimento JS.")
        else:
            print(f"⚠️ Campo ('{seletor_tipo}', '{seletor_valor}') não encontrado.")

def clicar_elemento(driver, seletor: tuple):
    # ... (código inalterado) ...
    """
    Clica em um elemento usando Espera Híbrida/Agressiva (Normal Click + JS Fallback).
    """
    seletor_tipo = seletor[0]
    seletor_valor = seletor[1]
    elemento = None 

    try:
        wait = WebDriverWait(driver, 10) 
        
        # 1. Espera que o elemento esteja PRESENTE
        elemento = wait.until(ec.presence_of_element_located(seletor))
        
        # 2. Tenta o clique normal
        wait.until(ec.element_to_be_clickable(seletor))
        elemento.click()
        print(f"🖱️ Clique realizado em: {seletor}")
        
    except Exception:
        # 3. Se o clique normal falhou, tenta o clique forçado via JavaScript
        if elemento:
            try:
                driver.execute_script("arguments[0].click();", elemento)
                print(f"⚠️ Elemento {seletor} falhou. Tentando JS... 🖱️ Clique JS realizado.")
            except:
                print(f"⚠️ Elemento ('{seletor_tipo}', '{seletor_valor}') falhou no clique JS.")
        else:
            print(f"⚠️ Elemento ('{seletor_tipo}', '{seletor_valor}') não encontrado após 10s.")


def validar_texto_esperado(driver, seletor: tuple, texto_esperado: str):
    # ... (código inalterado) ...
    """Valida se um texto esperado está presente no elemento, usando Espera Explícita."""
    seletor_tipo = seletor[0]
    seletor_valor = seletor[1]
    
    try:
        wait = WebDriverWait(driver, 10)
        
        # Espera até que o elemento esteja VISÍVEL e CAPTURA seu texto
        elemento = wait.until(
            ec.visibility_of_element_located(seletor)
        )
        
        texto_capturado = elemento.text.strip()
        print(f"🔍 Texto capturado: {texto_capturado}")

        if texto_esperado in texto_capturado:
            print(f"✅ Validação OK: '{texto_esperado}' encontrado.")
        else:
            print(f"❌ Validação FALHOU: '{texto_esperado}' não encontrado.")
            
    except Exception:
        print(f"⚠️ Não foi possível capturar texto de {seletor}.")
        print(f"❌ Validação FALHOU: '{texto_esperado}' não encontrado.")

def esperar_por_alerta(driver, texto_esperado: str = "Product added"):
    # ... (código inalterado) ...
    """
    Aguarda por um alerta do navegador (modal do DemoBlaze) e o aceita.
    """
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(ec.alert_is_present())
        alert = driver.switch_to.alert
        
        # Captura e valida o texto
        texto_alerta = alert.text
        if texto_esperado in texto_alerta:
            print(f"✅ Alerta capturado com sucesso: '{texto_alerta}'")
            alert.accept()
        else:
            print(f"❌ Alerta encontrado, mas texto esperado ('{texto_esperado}') não corresponde. Texto: '{texto_alerta}'")
            alert.accept() # Aceita mesmo assim para continuar
            
    except Exception as e:
        print(f"⚠️ Alerta não apareceu dentro do tempo limite. Erro: {e}")
        
def esperar_por_visibilidade(driver, seletor: tuple):
    # ... (código inalterado) ...
    """
    Aguarda até que um elemento se torne visível no DOM.
    Útil para modais ou elementos que demoram a aparecer.
    """
    seletor_tipo = seletor[0]
    seletor_valor = seletor[1]

    try:
        wait = WebDriverWait(driver, 10)
        wait.until(
            ec.visibility_of_element_located(seletor)
        )
        print(f"⌛ Espera concluída: Elemento {seletor} está visível.")
    except Exception:
        print(f"❌ Espera FALHOU: Elemento {seletor} não se tornou visível em 10s.")
        
def esperar_por_invisibilidade(driver, seletor: tuple):
    # ... (código inalterado) ...
    """
    Aguarda até que um elemento se torne INVISÍVEL no DOM.
    Útil para modais ou overlays que devem desaparecer.
    """
    seletor_tipo = seletor[0]
    seletor_valor = seletor[1]

    try:
        wait = WebDriverWait(driver, 10)
        # CRÍTICO: Espera a condição de INVISIBILIDADE
        wait.until(
            ec.invisibility_of_element_located(seletor)
        )
        print(f"⌛ Espera concluída: Elemento {seletor} está INVISÍVEL.")
    except Exception:
        print(f"❌ Espera FALHOU: Elemento {seletor} NÃO desapareceu em 10s.")