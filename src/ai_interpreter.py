# ============================================
# ai_interpreter.py (FINAL: AGORA GERA EVIDÊNCIAS)
# ============================================
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from web_actions import esperar_por_alerta # Garante que o módulo está importado

# Carregar variáveis do arquivo .env
load_dotenv()

# Cria o client da OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. DEFINIÇÃO DA FUNÇÃO (Ferramenta)
def get_automation_tools():
    """Retorna a definição das ações de automação para a IA."""
    return [
        {
            "type": "function",
            "function": {
                "name": "executar_script_automacao",
                "description": "Cria um script completo de automação web em formato de lista de ações, com base no comando do usuário. Esta é a única ferramenta que deve ser utilizada.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "script_acoes": {
                            "type": "array",
                            "description": "A lista sequencial de ações de automação web a serem executadas.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    # Incluída a nova ação de screenshot
                                    "acao": {"type": "string", "enum": ["abrir_site", "preencher_campo", "clicar_elemento", "validar_texto_esperado", "esperar_por_alerta", "esperar_por_visibilidade", "esperar_por_invisibilidade", "tirar_screenshot"]}, 
                                    "parametros": {
                                        "type": "array",
                                        "description": "Lista de parâmetros necessários. O primeiro é sempre o seletor (ID, class, ou xpath) ou a URL. Para 'tirar_screenshot', o parâmetro é apenas o nome do arquivo.",
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": ["acao", "parametros"]
                            }
                        }
                    },
                    "required": ["script_acoes"]
                }
            }
        }
    ]

# 2. Função Principal
def interpretar_comando(comando: str) -> str:
    """
    Usa a IA (Function Calling) para gerar o JSON estruturado de ações.
    """
    
    # Contexto de sistema (DemoBlaze)
    system_prompt = f"""
    Você é um assistente de automação web. Sua única tarefa é traduzir o pedido do usuário para uma chamada da função `executar_script_automacao`.
    O site de teste é 'https://www.demoblaze.com/'.
    
    **NOVA INSTRUÇÃO:** Você deve incluir a ação `tirar_screenshot` nos seguintes pontos do fluxo:
    1. Após abrir o site (nome: '01_Home').
    2. Após o Login bem-sucedido (nome: '02_Logado').
    3. Após adicionar o item ao carrinho (nome: '03_Item_Adicionado').
    4. Após a validação final de sucesso da compra (nome: '04_Compra_Sucesso').

    ### Seletores e Fluxo de Compra no Demoblaze:
    - URL Principal: 'https://www.demoblaze.com/'
    
    #### Login/Navegação:
    - Link Login: 'login2' (ID)
    - Campo Usuário: 'loginusername' (ID)
    - Campo Senha: 'loginpassword' (ID)
    - Botão Login: XPath: //*[@id="logInModal"]/div/div/div[3]/button[2] 
    - AÇÃO CRÍTICA (LOGIN): Após o clique no botão de Login, use a ação **'esperar_por_invisibilidade'** com o seletor **'logInModal'** (o container do modal de login).
    - Validação Login: Valide a presença do ID 'nameofuser' com o texto esperado 'Welcome michaelparaizo'.
    
    #### Adicionar ao Carrinho (Comprar Laptop):
    - Categoria Laptops: //a[text()='Laptops'] (XPath)
    - Link do Produto (Dell i7): //a[text()='Dell i7 8gb'] (XPath)
    - Botão 'Add to Cart': //a[text()='Add to cart'] (XPath)
    - Ação Crítica: Após clicar em 'Add to cart', use a ação **'esperar_por_alerta'** com o texto esperado 'Product added'.
    
    #### Checkout:
    - Link Carrinho: 'cartur' (ID)
    - Botão Place Order: Use a classe 'btn-success' na página do carrinho.
    - Modal de Compra (Formulário IDs): 'name', 'country', 'city', 'card', 'month', 'year'.
    - Botão Purchase: Use XPath //button[text()='Purchase'] para o botão final do modal.
    - Validação de Sucesso: Valide a presença do texto **'Thank you for your purchase!'** no seletor XPath: **//h2[text()='Thank you for your purchase!']**.
    - AÇÃO CRÍTICA (FECHAR MODAL): Clique no botão "OK" do modal final. Seletor: **class name: confirm**
    
    **Dados de Teste:**
    - Login: 'michaelparaizo' e '12345'
    - Dados de Compra: Nome: 'Michael Paraizo', País: 'Brazil', Cidade: 'Sao Paulo', Cartão: '123456789', Mês: '10', Ano: '2027'.
    
    Você DEVE gerar a chamada de função completa, encadeando todas as ações, validações e preenchimentos de forma lógica, incluindo os 4 pontos de screenshots.
    """

    try:
        # 3. Chamada à API com Tools
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": comando}
            ],
            tools=get_automation_tools(),
            tool_choice={"type": "function", "function": {"name": "executar_script_automacao"}} 
        )
        
        # 4. Processamento da Resposta
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            if tool_call.function.name == "executar_script_automacao":
                return tool_call.function.arguments 

        return json.dumps({"erro": "A IA não conseguiu gerar a chamada de função de automação (Function Calling falhou)."})

    except Exception as e:
        erro_json = json.dumps({"erro": f"Erro ao interpretar comando com a IA (Tools): {e}"})
        return erro_json