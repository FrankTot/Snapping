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

        self.filename = filename or f"reports/report_{self._timestamp()}.pdf"  # Nome file con timestamp
        self._add_logo()                                # Aggiunge il logo in alto
        self._add_header()                              # Aggiunge l'intestazione

    def _timestamp(self):
        '''
        Funzione: _timestamp
        Ritorna una stringa contenente data e ora correnti formattate per l'inserimento nel nome file
        Valore di ritorno:
        str -> timestamp formattato (es. 20250718_153000)
        '''
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _add_logo(self):
        '''
        Funzione: _add_logo
        Inserisce un logo nell'intestazione del PDF se presente nella directory assets
        '''
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            try:
                self.image(logo_path, x=10, y=8, w=30)
                self.ln(25)
            except Exception:
                # Se il logo non può essere caricato, continua senza errori
                self.ln(5)
        else:
            self.ln(5)

    def _add_header(self):
        '''
        Funzione: _add_header
        Aggiunge il titolo principale del report PDF
        '''
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(0, 70, 130)
        self.cell(0, 12, "SnapAudit System Report", 0, 1, 'C')
        
        # Aggiunge la data di generazione
        self.set_font("Helvetica", size=10)
        self.set_text_color(100, 100, 100)
        current_time = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        self.cell(0, 8, f"Generato il: {current_time}", 0, 1, 'C')
        
        # Linea separatrice
        self.ln(5)
        self.set_draw_color(0, 70, 130)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def _truncate_text(self, text, max_width):
        '''
        Funzione: _truncate_text
        Tronca il testo se supera la larghezza massima consentita
        
        Parametri:
        str text -> testo da troncare
        float max_width -> larghezza massima in unità PDF
        
        Valore di ritorno:
        str -> testo troncato se necessario
        '''
        if self.get_string_width(text) <= max_width:
            return text
        
        # Tronca il testo e aggiunge "..."
        while len(text) > 3 and self.get_string_width(text + "...") > max_width:
            text = text[:-1]
        
        return text + "..." if len(text) > 0 else "..."

    def _add_table(self, data, headers=None):
        '''
        Funzione: _add_table
        Aggiunge una tabella formattata al PDF
        
        Parametri:
        list data -> lista di dizionari contenenti i dati della tabella
        list headers -> lista delle intestazioni (opzionale)
        '''
        if not data:
            self.set_font("Helvetica", "I", 12)
            self.cell(0, 10, "Nessun dato disponibile", 0, 1)
            return

        # Determina le intestazioni
        if headers is None:
            headers = list(data[0].keys()) if isinstance(data[0], dict) else ["Dato"]
        
        # Calcola le larghezze delle colonne
        available_width = self.w - 20  # Larghezza disponibile meno margini
        col_width = available_width / len(headers)
        
        # Intestazione della tabella
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(230, 230, 230)
        self.set_text_color(0, 0, 0)
        
        for header in headers:
            truncated_header = self._truncate_text(str(header), col_width - 4)
            self.cell(col_width, 10, truncated_header, 1, 0, 'C', True)
        self.ln()

        # Righe della tabella
        self.set_font("Helvetica", size=10)
        self.set_fill_color(250, 250, 250)
        
        for i, row in enumerate(data):
            # Alterna il colore di sfondo
            fill = (i % 2 == 0)
            
            if isinstance(row, dict):
                values = [str(row.get(header, "")) for header in headers]
            else:
                values = [str(row)]
            
            # Calcola l'altezza necessaria per la riga
            max_lines = 1
            for value in values:
                truncated_value = self._truncate_text(value, col_width - 4)
                lines = max(1, len(truncated_value) // 50 + 1)  # Stima approssimativa
                max_lines = max(max_lines, lines)
            
            row_height = max(8, max_lines * 6)
            
            # Controlla se c'è spazio sufficiente, altrimenti vai a nuova pagina
            if self.get_y() + row_height > self.h - 25:
                self.add_page()
                # Ripeti l'intestazione nella nuova pagina
                self.set_font("Helvetica", "B", 11)
                self.set_fill_color(230, 230, 230)
                for header in headers:
                    truncated_header = self._truncate_text(str(header), col_width - 4)
                    self.cell(col_width, 10, truncated_header, 1, 0, 'C', True)
                self.ln()
                self.set_font("Helvetica", size=10)
                self.set_fill_color(250, 250, 250)
            
            # Stampa la riga
            for value in values:
                truncated_value = self._truncate_text(value, col_width - 4)
                self.cell(col_width, row_height, truncated_value, 1, 0, 'L', fill)
            self.ln()

    def add_section(self, title, content):
        '''
        Funzione: add_section
        Aggiunge una sezione al report PDF, formattata come tabella o testo a seconda del contenuto

        Parametri formali:
        str title   -> Titolo della sezione
        list|str content -> Contenuto testuale o tabellare della sezione
        '''
        # Controlla se c'è spazio sufficiente per il titolo
        if self.get_y() > self.h - 50:
            self.add_page()
        
        # Titolo della sezione
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 70, 130)
        self.cell(0, 12, title, 0, 1, 'L')
        self.ln(3)

        # Contenuto
        self.set_text_color(0, 0, 0)
        
        if isinstance(content, list) and content and isinstance(content[0], dict):
            # Contenuto tabellare
            self._add_table(content)
        else:
            # Contenuto testuale
            self.set_font("Helvetica", size=11)
            if isinstance(content, list):
                content = "\n".join(str(item) for item in content)
            
            if not content.strip():
                content = "Nessun dato disponibile"
            
            # Usa multi_cell per gestire il testo lungo
            self.multi_cell(0, 7, str(content), 0, 'L')

        self.ln(8)

    def generate_full_report(self):
        '''
        Funzione: generate_full_report
        Genera tutte le sezioni del report richiamando le funzioni del modulo system_snapshot
        '''
        try:
            # Assicurati che la cartella reports esista
            os.makedirs("reports", exist_ok=True)
            
            # Genera le sezioni del report
            self.add_section("Servizi Attivi", get_active_services())
            self.add_section("Utenti Connessi", get_logged_users())
            self.add_section("Porte Aperte", get_open_ports())
            self.add_section("Modifiche Recenti in /etc", get_recent_etc_modifications())
            
            # Aggiunge una nota finale
            self.add_page()
            self.set_font("Helvetica", "B", 12)
            self.set_text_color(0, 70, 130)
            self.cell(0, 10, "Note", 0, 1, 'L')
            self.ln(5)
            
            self.set_font("Helvetica", size=10)
            self.set_text_color(0, 0, 0)
            note_text = (
                "Questo report è stato generato automaticamente da SnapAudit.\n"
                "Le informazioni mostrate riflettono lo stato del sistema al momento della generazione.\n"
                "Per informazioni aggiornate, generare un nuovo report."
            )
            self.multi_cell(0, 6, note_text, 0, 'L')
            
            # Salva il file
            self.output(self.filename)
            
        except Exception as e:
            raise Exception(f"Errore durante la generazione del report: {str(e)}")
