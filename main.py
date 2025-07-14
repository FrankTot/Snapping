'''
Autore: Francesco Totaro
Data: 18/07/2025
Titolo: Progetto Esame Finale
'''

from PyQt6.QtWidgets import QApplication
import sys
import os
from gui.main_gui import MainGUI

##
## Funzioni:
##

def main():
    '''
    Funzione: main
    Scopo: Funzione principale per l'avvio dell'applicazione SnapAudit GUI.
    
    Parametri formali:
    Nessuno

    Valore di ritorno:
    Nessuno (la funzione termina l'esecuzione del programma con `sys.exit`)
    '''
    # Sezione di input Dati
    # Crea la cartella 'reports' se non esiste già
    if not os.path.exists("reports"):
        os.makedirs("reports")

    # Sezione di inizializzazione GUI
    app = QApplication(sys.argv)        # Inizializza l'applicazione Qt
    window = MainGUI()                  # Crea la finestra principale
    window.show()                       # Mostra la finestra principale
    sys.exit(app.exec())                # Avvia il ciclo di eventi Qt (e termina l'app alla chiusura)

'''
Programma principale
Descrizione sintetica funzionalità:
Inizializza e avvia l'interfaccia grafica SnapAudit, assicurandosi che
esista la cartella per i report PDF.
'''

# Avvia il programma solo se eseguito direttamente
if __name__ == "__main__":
    main()
