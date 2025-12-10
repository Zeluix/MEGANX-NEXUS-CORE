"""
MEGANX FILE EXTRACTOR v1.0
Copia as ferramentas de unlock encontradas pra pasta MEGANX_V9 pra analise.
"""

import os
import shutil
import glob

def banner():
    print("=" * 60)
    print(" MEGANX FILE EXTRACTOR - Copiando Ferramentas de Unlock")
    print("=" * 60)
    print()

def main():
    banner()
    
    # Pastas de origem
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Pasta de destino (nosso territorio)
    destino = r"C:\Users\LOGAN\Desktop\MEGANX_V9\UNLOCK_TOOLS"
    
    # Cria pasta de destino se nao existir
    os.makedirs(destino, exist_ok=True)
    print(f"[INFO] Pasta de destino: {destino}")
    
    # Arquivos a procurar
    arquivos_alvo = [
        "UnlockTool*.exe",
        "Moneyfrp*.exe",
        "*unlock*.exe",
        "*bypass*.exe",
        "*icloud*.exe",
        "*frp*.exe"
    ]
    
    copiados = []
    
    # Busca em Downloads
    print("\n[1/2] Buscando em Downloads...")
    for pattern in arquivos_alvo:
        matches = glob.glob(os.path.join(downloads, pattern))
        for match in matches:
            try:
                filename = os.path.basename(match)
                dest_path = os.path.join(destino, filename)
                shutil.copy2(match, dest_path)
                print(f"  [OK] Copiado: {filename}")
                copiados.append(filename)
            except Exception as e:
                print(f"  [ERRO] {match}: {e}")
    
    # Busca em Desktop
    print("\n[2/2] Buscando em Desktop...")
    for pattern in arquivos_alvo:
        matches = glob.glob(os.path.join(desktop, pattern))
        for match in matches:
            try:
                filename = os.path.basename(match)
                dest_path = os.path.join(destino, filename)
                shutil.copy2(match, dest_path)
                print(f"  [OK] Copiado: {filename}")
                copiados.append(filename)
            except Exception as e:
                print(f"  [ERRO] {match}: {e}")
    
    # Resumo
    print("\n" + "=" * 60)
    print(" RESUMO")
    print("=" * 60)
    
    if copiados:
        print(f"\n[SUCESSO] {len(copiados)} arquivo(s) copiado(s):")
        for c in copiados:
            print(f"  -> {c}")
        print(f"\nArquivos estao em: {destino}")
        print("\nAgora a MEGANX pode analisar!")
    else:
        print("\n[AVISO] Nenhum arquivo .exe encontrado com os padroes.")
        print("Verifique se os arquivos ainda estao no Downloads/Desktop.")
    
    input("\nPressione ENTER para fechar...")

if __name__ == "__main__":
    main()
