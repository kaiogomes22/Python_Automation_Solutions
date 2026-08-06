import subprocess
import json
from PIL import Image, ImageDraw, ImageFont

# Configuring addresses

tarjet_list = ["W2K19-RDCB02.ADM-CESUMAR.LOCAL", # Lyceum Server
              "W2K19-CTA-RODC1.adm-cesumar.local", # Local Dns
              "W2K19-CTA-APP01.adm-cesumar.local", # Print Server
              "", # Lyceum Server
              "", # Studeo
              "", # Intranet
#              "", #  
#              "",
]            

# GLOBAL FUNCTIONS

def enable_scripts():
    print("[*] Disabling Script Policy in the local MACHINE...")
    prompt = "Set-ExecutionPolicy Unrestricted -Force"
    subprocess.run(["powershell", "-Command", prompt], capture_output=True)

def disable_script():
    print("\n[*] Enabling Script Policy in the local Machine...")
    prompt1 = "Set-EcevutionPolicy Restricted- Force"
    subprocess.run(["powershell", "-Command", prompt1], capture_output=True)

# CREATING A JSONFILE 
def exe_tnc(tarjet):
    print(f"\n [>] Tracking tarjet: {tarket} (This may take a while )")

    comando = (
        f"$resultado = Test-NetConnection "{tarjet}"
    )
