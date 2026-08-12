import flet as ft
import cv2
import base64
import sqlite3
from ultralytics import YOLO

# ==========================================
# 1. CARREGAMENTO DA IA E BANCO DE DADOS
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
# 2. APLICATIVO (SIMULADOR MOBILE)
# ==========================================
def main(page: ft.Page):
    page.title = "App Inventário"
    page.window.width = 400
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    estado_app = {"itens_na_tela": {}}

    # ================= NOTIFICAÇÕES =================
    barra_notificacao = ft.SnackBar(content=ft.Text(""))
    page.overlay.append(barra_notificacao)

    def notificar(mensagem: str, cor: str):
        barra_notificacao.content = ft.Text(mensagem, weight="bold")
        barra_notificacao.bgcolor = cor
        barra_notificacao.open = True
        page.update()

    # ================= PROCESSAMENTO DE FOTO =================
    def on_foto_selecionada(e):
        if e.files:
            caminho_foto = e.files[0].path
            
            texto_feedback.value = "🤖 IA Analisando..."
            texto_feedback.color = "orange"
            page.update()

            frame = cv2.imread(caminho_foto)
            resultados = modelo_ia(frame, conf=0.30, verbose=False)[0]
            frame_anotado = resultados.plot()

            contagem = {}
            for caixa in resultados.boxes:
                nome_objeto = resultados.names[int(caixa.cls[0])]
                contagem[nome_objeto] = contagem.get(nome_objeto, 0) + 1
            
            estado_app["itens_na_tela"] = contagem

            _, buffer = cv2.imencode('.jpg', frame_anotado)
            img_base64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
            img_preview.src = f"data:image/jpeg;base64,{img_base64}"

            lista_mira.controls.clear()
            if not contagem:
                texto_feedback.value = "⚠️ Nenhum objeto encontrado."
                texto_feedback.color = "red"
            else:
                texto_feedback.value = "✅ Objetos detectados!"
                texto_feedback.color = "green"
                for item, qtd in contagem.items():
                    lista_mira.controls.append(ft.Text(f"• {qtd}x {item.upper()}", size=18, weight="bold"))

            page.update()

    seletor_arquivos = ft.FilePicker()
    seletor_arquivos.on_result = on_foto_selecionada
    page.overlay.append(seletor_arquivos)

    # ================= BANCO DE DADOS =================
    def salvar_estoque(e):
        if not estado_app["itens_na_tela"]:
            notificar("❌ Tire uma foto com objetos primeiro!", "red")
            return

        cursor = conexao.cursor()
        for item, quantidade_nova in estado_app["itens_na_tela"].items():
            cursor.execute(
                """
                INSERT INTO produtos (nome, quantidade) VALUES (?, ?)
                ON CONFLICT(nome) DO UPDATE SET quantidade = quantidade + excluded.quantidade
                """,
                (item, quantidade_nova),
            )
        conexao.commit()
        notificar("✅ Salvo no banco de dados!", "green")
        
        estado_app["itens_na_tela"] = {}
        pixel_inicial = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        img_preview.src = pixel_inicial
        lista_mira.controls.clear()
        texto_feedback.value = "Toque em 'Câmera / Galeria' abaixo"
        texto_feedback.color = "grey"
        page.update()

    def carregar_dados_inventario():
        cursor = conexao.cursor()
        cursor.execute("SELECT nome, quantidade FROM produtos ORDER BY quantidade DESC")
        registros = cursor.fetchall()

        lista_banco.controls.clear()
        if not registros:
            lista_banco.controls.append(ft.Text("O banco está vazio.", size=16))
        else:
            for nome, qtd in registros:
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Text(nome.upper(), weight="bold", size=18),
                            ft.Text(f"{qtd} un.", color="blue", weight="bold", size=18)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=15
                    )
                )
                lista_banco.controls.append(card)
        page.update()

    def limpar_banco(e):
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM produtos")
        conexao.commit()
        carregar_dados_inventario()
        notificar("🗑️ Banco apagado!", "red")

    # ================= TELAS =================
    pixel_inicial = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    
    texto_feedback = ft.Text("Toque em 'Câmera / Galeria' abaixo", size=16, color="grey", weight="bold")
    img_preview = ft.Image(src=pixel_inicial, width=350, height=300)
    lista_mira = ft.ListView(expand=True, spacing=5)

    btn_camera = ft.Container(
        content=ft.Text("📷 Câmera / Galeria", color="white", weight="bold", size=16),
        bgcolor="blue", padding=15, border_radius=8, alignment=ft.Alignment(0, 0),
        on_click=lambda _: seletor_arquivos.pick_files()
    )
    btn_salvar = ft.Container(
        content=ft.Text("💾 Salvar no Banco", color="white", weight="bold", size=16),
        bgcolor="green", padding=15, border_radius=8, alignment=ft.Alignment(0, 0),
        on_click=salvar_estoque
    )

    tela_scanner = ft.Column([
        ft.Text("Nova Leitura", size=24, weight="bold"),
        img_preview,
        texto_feedback,
        ft.Divider(),
        lista_mira,
        ft.Row([btn_camera, btn_salvar], alignment=ft.MainAxisAlignment.CENTER)
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=True)

    lista_banco = ft.ListView(expand=True, spacing=10)
    btn_apagar = ft.Container(
        content=ft.Text("🗑️ Apagar Tudo", color="white", weight="bold"),
        bgcolor="red", padding=15, border_radius=8, alignment=ft.Alignment(0, 0),
        on_click=limpar_banco
    )

    tela_banco = ft.Column([
        ft.Text("Estoque Salvo", size=24, weight="bold"),
        lista_banco,
        btn_apagar
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, visible=False)

    # ================= NAVEGAÇÃO INFERIOR =================
    def mudar_aba(e):
        if e.control.selected_index == 0:
            tela_scanner.visible = True
            tela_banco.visible = False
        else:
            tela_scanner.visible = False
            tela_banco.visible = True
            carregar_dados_inventario()
        page.update()

    barra_inferior = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.CAMERA_ALT, label="Leitor"),
            ft.NavigationBarDestination(icon=ft.Icons.STORAGE, label="Estoque"),
        ],
        on_change=mudar_aba
    )

    page.navigation_bar = barra_inferior
    page.add(tela_scanner, tela_banco)

ft.run(main)