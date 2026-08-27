import subprocess
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Preformatted, PageBreak
from reportlab.lib.styles import ParagraphStyle

# ==========================================
# PARTE 1: CONFIGURAÇÕES E ALVOS
# ==========================================
PASTA_DESTINO = "Relatorios_Rede"

lista_alvos = [
    "google.com"
    # Your aplication
       
    # SERVIDORES DNS
  
    #PRINT SERVER
   
    
#    "amazon.com"
]
# ==========================================
# PARTE 2: FUNÇÕES DE SEGURANÇA
# ==========================================
def habilitar_scripts():
    print("[*] Abrindo portas: Habilitando execução de scripts no Windows...")
    comando = "Set-ExecutionPolicy Unrestricted -Force"
    subprocess.run(["powershell", "-Command", comando], capture_output=True)

def desabilitar_scripts():
    print("[*] Trancando portas: Restaurando segurança de scripts...")
    comando = "Set-ExecutionPolicy Restricted -Force"
    subprocess.run(["powershell", "-Command", comando], capture_output=True)

# ==========================================
# PARTE 3: GERADOR DE JPG (COM ALTURA DINÂMICA)
# ==========================================
def gerar_imagem_terminal(texto, alvo, pasta):
    try:
        fonte = ImageFont.truetype("consola.ttf", 14)
    except IOError:
        try:
            fonte = ImageFont.truetype("cour.ttf", 14)
        except IOError:
            fonte = ImageFont.load_default()

    img_temp = Image.new('RGB', (1, 1))
    draw_temp = ImageDraw.Draw(img_temp)
    
    caixa_texto = draw_temp.multiline_textbbox((0, 0), texto, font=fonte)
    largura = caixa_texto[2] + 40 
    altura = caixa_texto[3] + 40  
    
    imagem = Image.new('RGB', (largura, altura), color='black')
    desenho = ImageDraw.Draw(imagem)
    
    desenho.multiline_text((20, 20), texto, fill="lime", font=fonte)
    
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"TNC_{alvo.replace('.', '_')}_{agora}.jpg"
    caminho_imagem = os.path.join(pasta, nome_arquivo)
    
    imagem.save(caminho_imagem)
    print(f"  [+] Imagem salva: {nome_arquivo}")

# ==========================================
# PARTE 4: ORQUESTRADOR PRINCIPAL (GERA PDF E JPG)
# ==========================================
def executar_tudo():
    os.makedirs(PASTA_DESTINO, exist_ok=True)
    caminho_pdf = os.path.join(PASTA_DESTINO, "Relatorio_TNC_Completo.pdf")
    
    print(f"\n[!] Iniciando testes... Arquivos serão salvos em: {PASTA_DESTINO}\n")
    
    doc = SimpleDocTemplate(caminho_pdf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elementos_pdf = []
    estilo_terminal = ParagraphStyle('Terminal', fontName='Courier', fontSize=9, leading=11)
    
    for alvo in lista_alvos:
        print(f"[>] Rastreado alvo: {alvo} (Aguarde o TraceRoute...)")
        
        comando = f"Test-NetConnection '{alvo}' -InformationLevel Detailed -TraceRoute"
        processo = subprocess.run(["powershell", "-Command", comando], capture_output=True, text=True)
        
        data_hora_teste = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cabecalho = f"====================================================\nALVO: {alvo.upper()} | DATA/HORA: {data_hora_teste}\n====================================================\n\n"
        
        texto_resultado = processo.stdout.strip() if processo.stdout else "[ERRO] Falha ao testar ou alvo bloqueado."
        texto_final = cabecalho + texto_resultado
        
        elementos_pdf.append(Preformatted(texto_final, estilo_terminal))
        elementos_pdf.append(PageBreak())
        
        gerar_imagem_terminal(texto_final, alvo, PASTA_DESTINO)
        
    doc.build(elementos_pdf)
    print(f"\n[OK] SUCESSO ABSOLUTO! PDF e {len(lista_alvos)} Imagens JPG geradas na pasta '{PASTA_DESTINO}'.")

# ==========================================
# PARTE 5: INÍCIO
# ==========================================
if __name__ == "__main__":
    habilitar_scripts()
    try:
        executar_tudo()
    finally:
        desabilitar_scripts()
