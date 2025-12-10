"""
MEGANX PC SCANNER v1.0
Escaneia o PC em busca de apps instalados e arquivos no Desktop.
Foco: Encontrar ferramentas de unlock de iPhone.
"""

import os
import subprocess
import winreg

def banner():
    print("=" * 60)
    print(" MEGANX PC SCANNER v1.0 - Hunting for Unlock Tools")
    print("=" * 60)
    print()

def get_installed_programs():
    """Lista programas instalados via Registro do Windows."""
    programs = []
    paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    for path in paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    try:
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        programs.append(name)
                    except:
                        pass
                except:
                    pass
        except:
            pass
    
    return sorted(set(programs))

def scan_desktop():
    """Lista todos os arquivos e pastas no Desktop."""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    items = []
    
    try:
        for item in os.listdir(desktop):
            full_path = os.path.join(desktop, item)
            item_type = "[PASTA]" if os.path.isdir(full_path) else "[ARQUIVO]"
            items.append(f"{item_type} {item}")
    except Exception as e:
        items.append(f"Erro ao ler Desktop: {e}")
    
    return items

def scan_downloads():
    """Lista arquivos recentes na pasta Downloads."""
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    items = []
    
    try:
        for item in os.listdir(downloads):
            full_path = os.path.join(downloads, item)
            item_type = "[PASTA]" if os.path.isdir(full_path) else "[ARQUIVO]"
            items.append(f"{item_type} {item}")
    except Exception as e:
        items.append(f"Erro ao ler Downloads: {e}")
    
    return items

def find_unlock_tools(programs, desktop_items, download_items):
    """Procura por ferramentas conhecidas de unlock de iPhone."""
    keywords = [
        "3utools", "icloud", "unlock", "bypass", "iremove", 
        "tenorshare", "4ukey", "reiboot", "checkra1n", "flexihub",
        "iphone", "itunes", "apple", "imyfone", "dr.fone", "fone",
        "passcode", "activation", "frp", "samsung", "android"
    ]
    
    matches = []
    
    all_items = programs + desktop_items + download_items
    
    for item in all_items:
        item_lower = item.lower()
        for kw in keywords:
            if kw in item_lower:
                matches.append(item)
                break
    
    return matches

def main():
    banner()
    
    print("[1/4] Escaneando programas instalados...")
    programs = get_installed_programs()
    
    print("[2/4] Escaneando Desktop...")
    desktop = scan_desktop()
    
    print("[3/4] Escaneando Downloads...")
    downloads = scan_downloads()
    
    print("[4/4] Procurando ferramentas de unlock...")
    matches = find_unlock_tools(programs, desktop, downloads)
    
    print("\n" + "=" * 60)
    print(" RESULTADOS")
    print("=" * 60)
    
    # Desktop
    print("\n--- DESKTOP ---")
    for item in desktop[:30]:  # Limita a 30
        print(f"  {item}")
    if len(desktop) > 30:
        print(f"  ... e mais {len(desktop) - 30} itens")
    
    # Downloads (recentes)
    print("\n--- DOWNLOADS (primeiros 20) ---")
    for item in downloads[:20]:
        print(f"  {item}")
    
    # Matches
    print("\n--- FERRAMENTAS DE UNLOCK ENCONTRADAS ---")
    if matches:
        for m in matches:
            print(f"  [!!!] {m}")
    else:
        print("  Nenhuma ferramenta conhecida encontrada automaticamente.")
        print("  Verifique a lista do Desktop manualmente.")
    
    # Salva resultado em arquivo
    output_file = os.path.join(os.path.dirname(__file__), "scan_result.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== PROGRAMAS INSTALADOS ===\n")
        for p in programs:
            f.write(f"{p}\n")
        f.write("\n=== DESKTOP ===\n")
        for d in desktop:
            f.write(f"{d}\n")
        f.write("\n=== DOWNLOADS ===\n")
        for d in downloads:
            f.write(f"{d}\n")
        f.write("\n=== MATCHES ===\n")
        for m in matches:
            f.write(f"{m}\n")
    
    print(f"\n[OK] Resultado completo salvo em: {output_file}")
    print("\nCopia o conteudo de scan_result.txt e cola pra MEGANX!")
    input("\nPressione ENTER para fechar...")

if __name__ == "__main__":
    main()
