import flet as ft
import sqlite3
from ultralytics import YOLO

# ==========================================
# 1. INICIALIZANDO A IA E O BANCO DE DADOS
# ==========================================
print("Carregando o Cérebro da IA (YOLOv8)...")
modelo_ia = YOLO("yolov8n.pt") 

def iniciar_banco():
    conn = sqlite3.connect("estoque.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS produtos (nome TEXT PRIMARY KEY, quantidade INTEGER)")
    conn.commit()
    return conn

conexao = iniciar_banco()

# ==========================================
# 2. O APLICATIVO (INTERFACE E LÓGICA)
# ==========================================
def main(page: ft.Page):
    page.title = "Inventar.IA - App Nativo"
    page.window.width = 420    
    page.window.height = 750   
    
    # SOLUÇÃO À PROVA DE BALA: Usando Texto Puro (Strings) em vez de Módulos!
    page.theme_mode = "light"
    page.horizontal_alignment = "center"
    page.scroll = "auto"

    estado_app = {"item_detectado": ""}

    texto_estoque = ft.Text("Selecione uma imagem para testar a IA!", size=18, weight="bold")
    
    def atualizar_texto_estoque(nome_item):
        cursor = conexao.cursor()
        cursor.execute("SELECT quantidade FROM produtos WHERE nome=?", (nome_item,))
        resultado = cursor.fetchone()
        qtd = resultado[0] if resultado else 0 
        texto_estoque.value = f"Estoque Atual: {qtd}x '{nome_item}'"
        page.update()

    # Cores passadas como Texto Puro ("blue", "green", "white")
    aviso_ia = ft.Text("🤖 Processando...", color="blue")
    campo_edicao = ft.TextField(
        label="Quantidade Validada", 
        value="", 
        width=200, 
        keyboard_type="number"
    )
    btn_confirmar = ft.ElevatedButton(
        "Salvar no SQLite", 
        bgcolor="green", 
        color="white"
    )
    
    caixa_filtro_humano = ft.Column(
        [aviso_ia, campo_edicao, btn_confirmar], 
        visible=False,
        horizontal_alignment="center"
    )

    # ----------------------------------------------------
    # EVENTO 1: Processamento da Imagem (ASSÍNCRONO)
    # ----------------------------------------------------
    async def acionar_camera(e):
        # Abre o explorador de ficheiros do Windows de forma segura
        arquivos = await ft.FilePicker().pick_files(allow_multiple=False)
        
        if arquivos:
            caminho_da_foto = arquivos[0].path
            
            # A IA lê a imagem do teu computador
            resultados = modelo_ia(caminho_da_foto)
            
            # Contagem dos itens
            contagem = {}
            nomes_das_classes = resultados[0].names 
            
            for caixa in resultados[0].boxes:
                id_classe = int(caixa.cls[0])           
                nome_objeto = nomes_das_classes[id_classe] 
                
                if nome_objeto in contagem:
                    contagem[nome_objeto] += 1
                else:
                    contagem[nome_objeto] = 1
            
            # Atualização da Interface
            if contagem:
                item_principal = max(contagem, key=contagem.get)
                quantidade_da_ia = contagem[item_principal]
                
                estado_app["item_detectado"] = item_principal 
                
                aviso_ia.value = f"🤖 Vi {quantidade_da_ia}x '{item_principal}'. Confirme:"
                campo_edicao.value = str(quantidade_da_ia)
                atualizar_texto_estoque(item_principal)
            else:
                aviso_ia.value = "🤖 Nenhum objeto reconhecido. Digite o valor:"
                campo_edicao.value = "0"
                estado_app["item_detectado"] = "desconhecido"

            caixa_filtro_humano.visible = True
            page.update()

    # ----------------------------------------------------
    # EVENTO 2: Persistência no Banco SQLite
    # ----------------------------------------------------
    def salvar_estoque(e):
        quantidade_nova = int(campo_edicao.value) 
        item_para_salvar = estado_app["item_detectado"]
        
        cursor = conexao.cursor()
        cursor.execute("SELECT quantidade FROM produtos WHERE nome=?", (item_para_salvar,))
        resultado = cursor.fetchone()
        
        if resultado:
            total = resultado[0] + quantidade_nova
            cursor.execute("UPDATE produtos SET quantidade=? WHERE nome=?", (total, item_para_salvar))
        else:
            total = quantidade_nova
            cursor.execute("INSERT INTO produtos (nome, quantidade) VALUES (?, ?)", (item_para_salvar, total))
        
        conexao.commit()

        atualizar_texto_estoque(item_para_salvar)
        caixa_filtro_humano.visible = False
        
        notificacao = ft.SnackBar(content=ft.Text(f"✅ {total}x '{item_para_salvar}' salvos com sucesso!"))
        page.overlay.append(notificacao) 
        notificacao.open = True          
        page.update()

    # Ícone passado como Texto Puro ("camera_alt")
    btn_camera = ft.FloatingActionButton(
        icon="camera_alt", 
        on_click=acionar_camera 
    )
    btn_confirmar.on_click = salvar_estoque

    # Montagem do ecrã
    page.add(
        ft.AppBar(title=ft.Text("Inventar.IA"), bgcolor="blue", color="white", center_title=True),
        ft.Container(height=20),
        texto_estoque,
        ft.Divider(),
        caixa_filtro_humano
    )
    page.floating_action_button = btn_camera 
    page.update() 

# 3. EXECUÇÃO LOCAL (PROGRAMA DE WINDOWS)
ft.app(target=main)