import subprocess
import sys
import ctypes
from xml.dom.minidom import Text

def is_admin():

    try: 
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_powershell(command):
    process = subprocess.run(
        ["powershell", "-Noprofile", "-ExecutionPolicy", "Bypass", "-Command", command],
        capture_output=True,
        text=True
    )
    return process

def main():
    # Trava de segurança
    if not is_admin():
        print("[X] ACESSO NEGADO: Esta ferramenta precisa ser executada como Administrador!")
        input("Pressione Enter para sair...")
        sys.exit(1)

    print("="*55)
    print("   FERRAMENTA DE CONFIGURAÇÃO: HOSTNAME E USUÁRIO")
    print("="*55)

    # Setting Up Hostname
    novo_hostname = input("\n[*] Digite o novo HOSTNAME (ou pressione Enter para pular): ").strip()
    
    if novo_hostname:
        print(f"    Injetando novo Hostname: '{novo_hostname}'...")
        # Comando nativo do PS para trocar o nome da máquina
        cmd_host = f"Rename-Computer -NewName '{novo_hostname}' -Force"
        res_host = run_powershell(cmd_host)
        
        if res_host.returncode == 0:
            print("    [+] Hostname alterado com sucesso!")
        else:
            print(f"    [-] Falha ao alterar Hostname. Erro: {res_host.stderr.strip()}")

    # ---------------------------------------------------------
    # 2. ALTERAÇÃO DO USUÁRIO LOCAL
    # ---------------------------------------------------------
    print("\n" + "-"*55)
    usuario_atual = input("[*] Digite o nome do usuário local ATUAL (ex: Aluno): ").strip()
    novo_usuario = input("[*] Digite o NOVO nome para este usuário: ").strip()

    if usuario_atual and novo_usuario:
        print(f"    Renomeando usuário '{usuario_atual}' para '{novo_usuario}'...")
        # Comando nativo do PS que altera o nome no Gerenciamento de Computador (SAM)
        cmd_user = f"Rename-LocalUser -Name '{usuario_atual}' -NewName '{novo_usuario}'"
        res_user = run_powershell(cmd_user)
        
        if res_user.returncode == 0:
            print("    [+] Usuário alterado com sucesso!")
        else:
            print(f"    [-] Falha ao alterar Usuário. Verifique se o nome atual está correto.")
            if res_user.stderr:
                print(f"        Detalhe: {res_user.stderr.strip()}")

    # ---------------------------------------------------------
    # 3. FINALIZAÇÃO E REBOOT
    # ---------------------------------------------------------
    print("\n=======================================================")
    print("Operações concluídas. As mudanças exigem reinicialização.")
    reboot = input("Deseja reiniciar a máquina AGORA? (S/N): ").strip().upper()

    if reboot == 'S':
        print("Reiniciando o sistema em 5 segundos...")
        subprocess.run(["shutdown", "/r", "/t", "5"])
    else:
        print("Reinício cancelado. As alterações entrarão em vigor no próximo boot.")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()