import flet as ft
import cv2
import base64
import threading
import time
from ultralytics import YOLO

print("Carregando IA...")
modelo = YOLO("yolov8n.pt")

def main(page: ft.Page):
    page.title = "Câmera em Tempo Real (Pura)"
    page.padding = 20

    # Apenas dois elementos na tela: O vídeo e o texto da contagem
    img_video = ft.Image(width=800, height=600, fit="contain")
    texto_contagem = ft.Text("Iniciando câmera...", size=24, weight="bold", color="blue")

    page.add(
        ft.Row([
            img_video,
            ft.Column([
                ft.Text("O que a IA está vendo AGORA:", size=28, weight="bold"),
                texto_contagem
            ], alignment="start")
        ])
    )

    def atualizar_camera():
        cap = cv2.VideoCapture(0)
        
        # Trava a resolução em 480p para a IA rodar rápida e não travar o vídeo
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        while cap.isOpened():
            sucesso, frame = cap.read()
            if not sucesso:
                time.sleep(0.05)
                continue

            # 1. IA lê o frame (sem travar)
            resultados = modelo(frame, conf=0.4, verbose=False)[0]
            frame_desenhado = resultados.plot()

            # 2. Faz a contagem
            contagem = {}
            for caixa in resultados.boxes:
                nome = resultados.names[int(caixa.cls[0])]
                contagem[nome] = contagem.get(nome, 0) + 1

            # 3. Converte a imagem para o Flet
            _, buffer = cv2.imencode('.jpg', frame_desenhado)
            img_b64 = base64.b64encode(buffer).decode('utf-8')

            # 4. Atualiza os componentes
            img_video.src_base64 = img_b64
            
            if contagem:
                linhas = [f"• {qtd}x {item.upper()}" for item, qtd in contagem.items()]
                texto_contagem.value = "\n".join(linhas)
            else:
                texto_contagem.value = "Nenhum objeto..."

            # Atualiza APENAS a foto e o texto, ignorando o resto do programa
            try:
                img_video.update()
                texto_contagem.update()
            except Exception:
                break
                
            # Um pequeno respiro (30fps) para a imagem fluir como um filme
            time.sleep(0.03)

    # Liga a câmera em segundo plano instantaneamente
    threading.Thread(target=atualizar_camera, daemon=True).start()

ft.run(main)