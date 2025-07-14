'''
Autore: Francesco Totaro 
Data: 18/07/2025
Titolo: Progetto Esame Finale 
'''

##
## Programma principale
## Interfaccia grafica principale del sistema SnapAudit,
## consente la generazione, visualizzazione e cancellazione dei report PDF.
##

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QListWidget, QMessageBox, QHBoxLayout, QCheckBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from core.report_generator import PDFReport                    # Importa la classe per generare PDF
from core.system_snapshot import get_reports_list              # Funzione per ottenere la lista dei report
import subprocess


class MainGUI(QWidget):
    '''
    Classe: MainGUI
    Interfaccia grafica basata su PyQt6 per interagire con SnapAudit
    '''
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SnapAudit - Sistema di Audit")
        self.setGeometry(100, 100, 800, 600)  # Posizione iniziale e dimensioni finestra
        self.is_dark_theme = False            # Tema iniziale: chiaro
        self._setup_ui()                      # Costruzione interfaccia
        self.apply_theme()                    # Applicazione tema

    def _setup_ui(self):
        '''
        Funzione: _setup_ui
        Inizializza e dispone i componenti grafici nella finestra
        '''
        layout = QVBoxLayout()

        # Logo SnapAudit
        logo_label = QLabel()
        pixmap = QPixmap("assets/logo.png")
        if pixmap.isNull():
            logo_label.setText("Logo non trovato")
        else:
            # Ridimensionamento proporzionale del logo
            scaled_pixmap = pixmap.scaled(200, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Checkbox per attivare/disattivare il tema scuro
        self.theme_toggle = QCheckBox("Tema Scuro")
        self.theme_toggle.stateChanged.connect(self.toggle_theme)
        layout.addWidget(self.theme_toggle)

        # Lista dei report disponibili
        self.report_list = QListWidget()
        self._load_report_list()
        layout.addWidget(self.report_list)

        # Sezione bottoni
        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton("📝 Genera Report")
        self.generate_btn.clicked.connect(self.generate_pdf)
        button_layout.addWidget(self.generate_btn)

        self.view_btn = QPushButton("📄 Visualizza Report")
        self.view_btn.clicked.connect(self.view_selected_report)
        button_layout.addWidget(self.view_btn)

        self.delete_btn = QPushButton("🗑️ Elimina Report")
        self.delete_btn.clicked.connect(self.delete_selected_report)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _load_report_list(self):
        '''
        Funzione: _load_report_list
        Carica e aggiorna la lista dei report disponibili nella GUI
        '''
        self.report_list.clear()
        reports = get_reports_list()
        if reports:
            for rpt in sorted(reports, reverse=True):
                self.report_list.addItem(rpt)
        else:
            self.report_list.addItem("Nessun report trovato")

    def apply_theme(self):
        '''
        Funzione: apply_theme
        Applica dinamicamente il tema (chiaro o scuro) all'interfaccia
        '''
        if self.is_dark_theme:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: white;
                    font-family: 'Segoe UI';
                }
                QPushButton {
                    background-color: #444;
                    color: white;
                    border-radius: 5px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
                QListWidget {
                    background-color: #3c3c3c;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f2f5;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QListWidget {
                    background-color: white;
                    border: 1px solid #ccc;
                }
            """)

    def toggle_theme(self):
        '''
        Funzione: toggle_theme
        Inverte lo stato del tema (chiaro ↔ scuro) e applica il nuovo stile
        '''
        self.is_dark_theme = self.theme_toggle.isChecked()
        self.apply_theme()

    def generate_pdf(self):
        '''
        Funzione: generate_pdf
        Genera un nuovo report PDF usando le informazioni di sistema
        '''
        try:
            filename = None
            pdf = PDFReport(filename=filename)
            pdf.generate_full_report()
            self._load_report_list()
            QMessageBox.information(self, "Successo", "✅ Report generato correttamente!")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la generazione del report:\n{str(e)}")

    def view_selected_report(self):
        '''
        Funzione: view_selected_report
        Apre il report PDF selezionato nella lista con il programma predefinito
        '''
        selected = self.report_list.currentItem()
        if not selected or "Nessun report trovato" in selected.text():
            QMessageBox.warning(self, "Attenzione", "Seleziona un report dalla lista.")
            return
        report_path = os.path.join("reports", selected.text())
        if not os.path.exists(report_path):
            QMessageBox.warning(self, "Errore", "File report non trovato.")
            return
        try:
            if sys.platform.startswith('linux'):
                subprocess.run(['xdg-open', report_path], check=False)
            elif sys.platform == 'win32':
                os.startfile(report_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', report_path], check=False)
            else:
                QMessageBox.warning(self, "Errore", "Sistema operativo non supportato.")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'aprire il report:\n{str(e)}")

    def delete_selected_report(self):
        '''
        Funzione: delete_selected_report
        Elimina il report selezionato previa conferma dell’utente
        '''
        selected = self.report_list.currentItem()
        if not selected or "Nessun report trovato" in selected.text():
            QMessageBox.warning(self, "Attenzione", "Seleziona un report dalla lista.")
            return

        report_path = os.path.join("reports", selected.text())
        reply = QMessageBox.question(
            self, 'Conferma', f"Sei sicuro di voler eliminare il report:\n{selected.text()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(report_path)
                self._load_report_list()
                QMessageBox.information(self, "Eliminato", "Report eliminato correttamente.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile eliminare il report:\n{str(e)}")
