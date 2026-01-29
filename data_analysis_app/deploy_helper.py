import os
import subprocess
import sys

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Errore comando '{command}': {e.stderr}")
        return None

def main():
    print("🚀 -- Assistente Deployment GitHub --")
    print("Questo script collegherà la tua app a GitHub automaticamente.\n")
    
    # 1. Verifica git init
    if not os.path.exists(".git"):
        print("Inizializzo Git...")
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "Initial commit"')
    
    # 2. Richiesta URL
    print("Passo 1: Vai su https://github.com/new e crea un repository vuoto.")
    print("Passo 2: Copia il link HTTPS del repository (es. https://github.com/tuo-nome/tuo-repo.git)")
    repo_url = input("\n👉 Incolla qui il link del repository: ").strip()
    
    if not repo_url.startswith("http"):
        print("❌ Errore: Il link deve iniziare con http o https.")
        return

    # 3. Configurazione Remote
    print(f"\nConfiguro il remote origin su: {repo_url}")
    
    # Rimuove origin esistente se c'è
    run_command("git remote remove origin")
    
    # Aggiunge nuovo origin
    res = run_command(f"git remote add origin {repo_url}")
    
    # 4. Push
    print("\n📦 Caricamento file su GitHub in corso...")
    print("Nota: Se ti chiede username/password, inseriscili (per la password usa un Personal Access Token).")
    
    run_command("git branch -M main")
    
    try:
        subprocess.run("git push -u origin main", shell=True, check=True)
        print("\n✅ SUCCESSO! Il codice è su GitHub.")
        print("Ora vai su https://share.streamlit.io e fai il Deploy selezionando questo repository.")
    except subprocess.CalledProcessError:
        print("\n❌ ERRORE nel caricamento. Verifica le tue credenziali o se il repo esiste.")

if __name__ == "__main__":
    main()
