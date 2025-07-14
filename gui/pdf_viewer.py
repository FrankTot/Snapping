'''
Autore: Francesco Totaro
Data: 18/07/2025
Titolo: Progetto Esame Finale
'''

import subprocess
import platform
import os

def open_pdf(filepath):
    '''
    Funzione: open_pdf
    Scopo: Apre un file PDF con il visualizzatore predefinito del sistema operativo.
    
    Parametri:
        filepath (str): percorso assoluto o relativo al file PDF da aprire

    Comportamento:
        - Verifica l'esistenza del file
        - Determina il sistema operativo
        - Utilizza il comando appropriato per aprire il PDF
    '''
    if not os.path.exists(filepath):
        print(f"Il file {filepath} non esiste")  # Messaggio di errore se il file non esiste
        return

    system = platform.system()  # Rileva il sistema operativo

    # Apre il file in base al sistema operativo
    if system == "Windows":
        os.startfile(filepath)
    elif system == "Darwin":  # macOS
        subprocess.call(["open", filepath])
    else:  # Linux e altri sistemi Unix-like
        subprocess.call(["xdg-open", filepath])
