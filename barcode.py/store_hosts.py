import os
import time

def limpar_tela():
    # Comando para limpar o terminal (funciona no Windows e no Linux/Mac)
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    limpar_tela()
    print("="*40)
    print(" COLETOR DE NOMES E PATRIMÔNIOS ")
    print("="*40)
    print("1 - Lab. de Informática 1")
    print("2 - Lab. de Informática 2")
    print("3 - Lab. de Informática 3")
    print("4 - Lab. de Informática 4")
    print("="*40)
    
    escolha_lab = input("\nSelecione o laboratório (1 a 4): ")
    
    # Para deixar a ferramenta flexível, perguntamos quantas máquinas o lab tem
    try:
        qtd_pcs = int(input(f"Quantas máquinas tem o Lab {escolha_lab}? (Ex: 56): "))
    except ValueError:
        print("[!] Valor inválido. Assumindo o padrão de 56 máquinas.")
        qtd_pcs = 56

    # Cria o nome do arquivo baseado no laboratório escolhido
    nome_arquivo = f"Inventario_Lab_{escolha_lab}.txt"
    
    print(f"\n[*] Iniciando coleta. Os dados serão salvos em: {nome_arquivo}")
    input("Pressione ENTER para começar o escaneamento...")

    # Loop principal que vai da máquina 1 até a quantidade informada
    for i in range(1, qtd_pcs + 1):
        
        # A mágica do zfill(3): transforma o número 1 em '001', 15 em '015', etc.
        hostname = f"CWB-LABIF{escolha_lab}-{str(i).zfill(3)}C"
        
        # Esse 'while True' é a trava para permitir você refazer a leitura se der erro
        while True:
            limpar_tela()
            print(f"LABORATÓRIO {escolha_lab} | MÁQUINA {i} DE {qtd_pcs}")
            print("-" * 40)
            print(f"[ ALVO ATUAL ] Hostname: {hostname}")
            print("-" * 40)
            
            # O leitor vai bipar, preencher o input e dar o ENTER sozinho
            patrimonio = input("\n>> Escaneie o patrimônio da máquina: ").strip()
            
            print(f"\n[ DADO LIDO ] {hostname}  ->  {patrimonio}")
            
            # Opção de validação
            acao = input("\n[ENTER] Salvar e ir pro próximo | [R] Escanear de novo: ").strip().upper()
            
            if acao == 'R':
                print("[!] Descartando leitura. Vamos tentar novamente...")
                time.sleep(1)
                # Como não damos o 'break', o while repete e pede a mesma máquina de novo
            else:
                # O modo 'a' (append) anexa a linha no final do TXT sem apagar o que já existe
                with open(nome_arquivo, 'a', encoding='utf-8') as arquivo:
                    arquivo.write(f"{hostname} - {patrimonio}\n")
                
                print("\n[ OK ] Dado gravado no TXT com sucesso!")
                time.sleep(0.5)
                break # Quebra o while da repetição e vai para a próxima máquina do 'for'

    limpar_tela()
    print("="*40)
    print(" COLETA FINALIZADA COM SUCESSO! ")
    print(f" Verifique o arquivo: {nome_arquivo}")
    print("="*40)

if __name__ == "__main__":
    main() 
    