'''
Autore: Francesco Totaro 
Data: 18/07/2025
Titolo: Progetto Esame Finale 
'''

##
## Funzioni e classi:
##

from fpdf import FPDF                         # Libreria per creare file PDF
from datetime import datetime                 # Per ottenere data e ora attuali
from .system_snapshot import (                # Importazione delle funzioni di snapshot del sistema
    get_active_services, 
    get_logged_users, 
    get_open_ports, 
    get_recent_etc_modifications
)
import os                                     # Libreria per operazioni su file e percorsi


class PDFReport(FPDF):
    '''
    Classe: PDFReport
    Estende la classe FPDF per generare un report PDF automatizzato
    '''

    def __init__(self, filename=None):
        '''
        Metodo: __init__
        Inizializza il report, imposta font, margini, logo e header
        Parametri:
        str filename (opzionale) -> nome file PDF da generare. Se non fornito, viene generato automaticamente.
        '''
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)  # Imposta il margine di fine pagina
        self.set_font("Helvetica", size=12)             # Font di default
        self.add_page()                                 # Aggiunge la prima pagina

        self.filename = filename or f"reports/report__{self._timestamp()}.pdf"  # Nome file con timestamp
        self._add_logo()                                # Aggiunge il logo in alto
        self._add_header()                              # Aggiunge l’intestazione

    def _timestamp(self):
        '''
        Funzione: _timestamp
        Ritorna una stringa contenente data e ora correnti formattate per l'inserimento nel nome file
        Valore di ritorno:
        str -> timestamp formattato (es. 18-07-2025__15:30:00)
        '''
        return datetime.now().strftime("%d-%m-%Y__%H:%M:%S")

    def _add_logo(self):
        '''
        Funzione: _add_logo
        Inserisce un logo nell’intestazione del PDF se presente nella directory assets
        '''
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            self.image(logo_path, x=10, y=8, w=30)
            self.ln(20)

    def _add_header(self):
        '''
        Funzione: _add_header
        Aggiunge il titolo principale del report PDF
        '''
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(0, 70, 130)
        self.cell(0, 10, "SnapAudit Report", 0, 1, 'C')
        self.ln(10)

    def add_section(self, title, content):
        '''
        Funzione: add_section
        Aggiunge una sezione al report PDF, formattata come tabella o testo a seconda del contenuto

        Parametri formali:
        str title   -> Titolo della sezione
        list|str content -> Contenuto testuale o tabellare della sezione
        '''
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(52, 58, 64)
        self.cell(0, 10, title, 0, 1)

        self.set_font("Helvetica", size=12)
        self.set_text_color(0, 0, 0)

        # Se content è una lista di dizionari => stampa tabella
        if isinstance(content, list) and content and isinstance(content[0], dict):
            headers = list(content[0].keys())                          # Ottiene intestazioni
            col_width = (self.w - 30) / len(headers)                   # Calcola larghezza colonne

            self.set_fill_color(200, 230, 255)                         # Colore intestazione tabella
            self.set_font("Helvetica", "B", 12)
            for h in headers:
                self.cell(col_width, 10, h, 1, 0, 'C', True)           # Stampa intestazioni
            self.ln()

            self.set_font("Helvetica", size=10)
            self.set_fill_color(245, 245, 245)

            for row in content:
                cell_texts = [str(v) for v in row.values()]
                n_lines = [max(1, int(self.get_string_width(text) / (col_width - 2))) for text in cell_texts]
                max_lines = max(n_lines)
                row_height = 6 * max_lines

                x_start = self.get_x()
                y_start = self.get_y()

                for i, text in enumerate(cell_texts):
                    x = self.get_x()
                    y = self.get_y()
                    self.multi_cell(col_width, 6, text, 1, 'L')       # Stampa ogni cella su più righe se necessario
                    self.set_xy(x + col_width, y)

                self.ln(row_height)
        else:
            # Se content è lista semplice o stringa => stampa testo multilinea
            if isinstance(content, list):
                content = "\n".join(str(item) for item in content)
            self.multi_cell(0, 8, content)

        self.ln()

    def generate_full_report(self):
        '''
        Funzione: generate_full_report
        Genera tutte le sezioni del report richiamando le funzioni del modulo system_snapshot
        '''
        self.add_section("Active Services", get_active_services())
        self.add_section("Logged In Users", get_logged_users())
        self.add_section("Open Ports", get_open_ports())
        self.add_section("Recent /etc Modifications", get_recent_etc_modifications())
        self.output(self.filename)  # Salva il file PDF nel percorso definito
