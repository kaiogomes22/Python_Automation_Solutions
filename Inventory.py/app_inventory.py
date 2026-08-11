import flet as ft
import cv2
import base64
import threading
import sqlite3
from ultralytics import YOLO

# ==========================================
# 1. BANCO DE DADOS E MODELO IA
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
# 2. APLICATIVO PRINCIPAL PARA WINDOWS (PC)
# ==========================================
def main(page: ft.Page):
    page.title = "System Inventar.IA - Visão Computacional (PC)"
    page.theme_mode = "light"
    page.padding = 20

    estado_app = {"itens_na_tela": {}}

    # ================= FUNÇÕES DE AÇÃO =================
    def carregar_dados_inventario():
        cursor = conexao.cursor()
        cursor.execute("SELECT nome, quantidade FROM produtos ORDER BY quantidade DESC")
        registros = cursor.fetchall()

        tabela_estoque.rows.clear()
        if not registros:
            tabela_estoque.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(content=ft.Text("Nenhum item salvo ainda...")), 
                    ft.DataCell(content=ft.Text("0"))
                ])
            )
        else:
            for nome, qtd in registros:
                tabela_estoque.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(content=ft.Text(nome.upper(), weight="bold")),
                        ft.DataCell(content=ft.Text(f"{qtd} unidades")),
                    ])
                )
        page.update()

    def limpar_banco(e):
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM produtos")
        conexao.commit()
        carregar_dados_inventario()
        notificacao = ft.SnackBar(content=ft.Text("🗑️ Banco de dados zerado com sucesso!"), bgcolor="red")
        page.overlay.append(notificacao)
        notificacao.open = True
        page.update()

    def salvar_estoque(e):
        itens_agora = estado_app["itens_na_tela"]
        if not itens_agora:
            notificacao = ft.SnackBar(content=ft.Text("❌ Não há nada na câmera para salvar!"), bgcolor="red")
            page.overlay.append(notificacao)
            notificacao.open = True
            page.update()
            return
            
        cursor = conexao.cursor()
        for item, quantidade_nova in itens_agora.items():
            cursor.execute("SELECT quantidade FROM produtos WHERE nome=?", (item,))
            resultado = cursor.fetchone()
            
            if resultado:
                total = resultado[0] + quantidade_nova
                cursor.execute("UPDATE produtos SET quantidade=? WHERE nome=?", (total, item))
            else:
                cursor.execute("INSERT INTO produtos (nome, quantidade) VALUES (?, ?)", (item, quantidade_nova))
        
        conexao.commit()
        
        notificacao = ft.SnackBar(content=ft.Text("✅ Todos os itens da tela foram somados ao Banco de Dados!"), bgcolor="green")
        page.overlay.append(notificacao)
        notificacao.open = True
        page.update()

    def alternar_telas(aba):
        if aba == "scanner":
            painel_scanner.visible = True
            painel_inventario.visible = False
        else:
            painel_scanner.visible = False
            painel_inventario.visible = True
            carregar_dados_inventario()
        page.update()

    # ================= BOTÕES CUSTOMIZADOS E BLINDADOS =================
    # Usando cores sólidas nativas ("black", "blue", "green") para garantir o contraste.
    btn_menu_scanner = ft.Container(
        content=ft.Text("🎥 Scanner Ao Vivo", weight="bold", color="white", size=16),
        bgcolor="black", padding=15, border_radius=8, ink=True,
        alignment=ft.Alignment(0, 0),
        on_click=lambda _: alternar_telas("scanner")
    )

    btn_menu_inventario = ft.Container(
        content=ft.Text("📊 Menu do Inventário", weight="bold", color="white", size=16),
        bgcolor="black", padding=15, border_radius=8, ink=True,
        alignment=ft.Alignment(0, 0),
        on_click=lambda _: alternar_telas("inventario")
    )

    menu_superior = ft.Row([btn_menu_scanner, btn_menu_inventario], alignment="center", spacing=20)

    # ================= TELA 1: SCANNER =================
    img_webcam = ft.Image(src="", width=500, height=380, fit="contain")
    texto_feedback = ft.Text("Ligando a câmera...", size=18, weight="bold", color="orange")
    titulo_mira = ft.Text("Itens na Mira da IA:", size=20, weight="bold")
    lista_mira = ft.ListView(expand=True, spacing=5)

    btn_salvar = ft.Container(
        content=ft.Text("💾 Salvar Estoque Atual da Câmera", weight="bold", color="white", size=16),
        bgcolor="green", padding=15, border_radius=8, ink=True,
        alignment=ft.Alignment(0, 0),
        on_click=salvar_estoque
    )

    coluna_esquerda = ft.Column([img_webcam, texto_feedback], alignment="center", horizontal_alignment="center")
    coluna_direita = ft.Column([titulo_mira, lista_mira, btn_salvar], expand=True, alignment="start")

    painel_scanner = ft.Container(
        content=ft.Row([coluna_esquerda, ft.VerticalDivider(width=20), coluna_direita], expand=True),
        visible=True,
        expand=True
    )

    # ================= TELA 2: INVENTÁRIO =================
    titulo_inventario = ft.Text("📊 Relatório Completo do Estoque (SQLite)", size=22, weight="bold")
    
    tabela_estoque = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Produto Identificado", weight="bold")),
            ft.DataColumn(label=ft.Text("Quantidade Total", weight="bold")),
        ],
        rows=[]
    )

    btn_atualizar_menu = ft.Container(
        content=ft.Text("🔄 Atualizar Tabela", weight="bold", color="white"),
        bgcolor="blue", padding=15, border_radius=8, ink=True,
        alignment=ft.Alignment(0, 0),
        on_click=lambda _: carregar_dados_inventario()
    )

    btn_zerar_banco = ft.Container(
        content=ft.Text("🗑️ Zerar Banco de Dados", weight="bold", color="white"),
        bgcolor="red", padding=15, border_radius=8, ink=True,
        alignment=ft.Alignment(0, 0),
        on_click=limpar_banco
    )

    painel_inventario = ft.Container(
        content=ft.Column([
            titulo_inventario,
            ft.Row([btn_atualizar_menu, btn_zerar_banco], spacing=10),
            ft.Divider(),
            ft.Column([tabela_estoque], scroll="auto", expand=True)
        ], expand=True),
        visible=False,
        expand=True
    )

    # ================= MONTAGEM FINAL DA TELA =================
    page.add(
        menu_superior,
        ft.Divider(),
        ft.Column([painel_scanner, painel_inventario], expand=True)
    )

    # ----------------------------------------------------
    # MOTOR DA WEBCAM (THREAD PARALELA)
    # ----------------------------------------------------
    def processar_webcam():
        cap = cv2.VideoCapture(0)
        
        while cap.isOpened():
            sucesso, frame = cap.read()
            if not sucesso:
                continue
            
            resultados = modelo_ia(frame, conf=0.20)[0]
            frame_anotado = resultados.plot()
            
            contagem = {}
            for caixa in resultados.boxes:
                nome_objeto = resultados.names[int(caixa.cls[0])] 
                contagem[nome_objeto] = contagem.get(nome_objeto, 0) + 1
            
            estado_app["itens_na_tela"] = contagem
            
            _, buffer = cv2.imencode('.png', frame_anotado)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            img_webcam.src = None 
            img_webcam.src_base64 = img_base64
            
            if not contagem:
                texto_feedback.value = "⚠️ Não vejo nada claro. Aproxime a câmera!"
                texto_feedback.color = "red"
                lista_mira.controls.clear()
                lista_mira.controls.append(ft.Text("Nada detectado...", size=16, color="grey"))
            else:
                texto_feedback.value = "✅ Objetos travados na mira!"
                texto_feedback.color = "green"
                
                lista_mira.controls.clear()
                for item, qtd in contagem.items():
                    lista_mira.controls.append(ft.Text(f"• {qtd}x '{item}'", size=20))
            
            try:
                page.update()
            except Exception:
                break

        cap.release()

    motor_video = threading.Thread(target=processar_webcam, daemon=True)
    motor_video.start()

ft.run(main)