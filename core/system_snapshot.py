'''
Autore: Francesco Totaro 
Data: 18/07/2025
Titolo: Progetto Esame Finale 
'''

##
## Funzioni:
##

import subprocess                            # Per eseguire comandi di sistema
import os                                    # Per operazioni su file system
from datetime import datetime, timedelta     # Per gestione date e intervalli temporali


def get_active_services():
    '''
    Funzione: get_active_services
    Ottiene la lista dei servizi attivi sul sistema tramite systemctl

    Valore di ritorno:
    list -> Lista di dizionari con nome del servizio e descrizione
    '''
    try:
        output = subprocess.check_output(
            ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager", "--no-legend"],
            text=True
        )
        services = []
        for line in output.strip().split('\n'):
            parts = line.split()
            if parts:
                # Il nome del servizio è il primo elemento, la descrizione parte dal quinto elemento in poi
                services.append({"Service": parts[0], "Description": " ".join(parts[4:])})
        return services
    except Exception as e:
        # In caso di errore, ritorna un dizionario con la descrizione dell'eccezione
        return [{"Service": "Errore", "Description": str(e)}]


def get_logged_users():
    '''
    Funzione: get_logged_users
    Ottiene l'elenco degli utenti attualmente connessi al sistema

    Valore di ritorno:
    list -> Lista di dizionari contenenti utente, terminale e orario di accesso
    '''
    try:
        output = subprocess.check_output(["who"], text=True)
        users = []
        for line in output.strip().split('\n'):
            parts = line.split()
            if parts:
                users.append({"User": parts[0], "TTY": parts[1], "Login Time": parts[2] + " " + parts[3]})
        return users
    except Exception as e:
        return [{"User": "Errore", "TTY": "", "Login Time": str(e)}]


def get_open_ports():
    '''
    Funzione: get_open_ports
    Ottiene l'elenco delle porte TCP/UDP aperte utilizzando il comando 'ss'

    Valore di ritorno:
    list -> Lista di dizionari con protocollo e indirizzo locale
    '''
    try:
        output = subprocess.check_output(["ss", "-tuln"], text=True)
        ports = []
        lines = output.strip().split('\n')
        for line in lines[1:]:  # Salta l’intestazione
            parts = line.split()
            if len(parts) >= 5:
                proto = parts[0]
                local_address = parts[4]
                ports.append({"Proto": proto, "Local Address": local_address})
        return ports
    except Exception as e:
        return [{"Proto": "Errore", "Local Address": str(e)}]


def get_recent_etc_modifications(days=7):
    '''
    Funzione: get_recent_etc_modifications
    Scansiona la directory /etc alla ricerca di file modificati di recente

    Parametri formali:
    int days -> numero di giorni indietro da considerare per la modifica dei file (default 7)

    Valore di ritorno:
    list -> Lista di file modificati di recente con data e ora
    '''
    try:
        cutoff = datetime.now() - timedelta(days=days)  # Calcola la data limite
        files = []
        for root, _, filenames in os.walk("/etc"):
            for f in filenames:
                path = os.path.join(root, f)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(path))
                    if mtime > cutoff:
                        files.append({"File": path, "Last Modified": mtime.strftime("%Y-%m-%d %H:%M:%S")})
                except:
                    continue  # Ignora file non accessibili
        return files if files else [{"File": "Nessuna modifica recente", "Last Modified": ""}]
    except Exception as e:
        return [{"File": "Errore", "Last Modified": str(e)}]


def get_reports_list():
    '''
    Funzione: get_reports_list
    Elenca tutti i file PDF presenti nella cartella "reports"

    Valore di ritorno:
    list -> Lista dei nomi file .pdf presenti nella directory dei report
    '''
    folder = "reports"
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if f.endswith(".pdf")]
