"""
GUI-Anwendung für MIDI-Analyse
Grafische Benutzeroberfläche für lokale Nutzung
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import threading

# Füge Parent-Directory zum Path hinzu für lokale Entwicklung
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from midi_analyzer import MidiAnalyzer, TextFormatter


class MidiCompareGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MIDI Analyzer - Analyse und Vergleich")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variablen für Dateipfade
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        # Setze Standard-Output-Pfad
        self.output_path.set(os.path.join(os.getcwd(), "vergleich.txt"))
        
        # Analyzer
        self.analyzer = MidiAnalyzer()
        self.formatter = TextFormatter()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Hauptframe mit Padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfiguriere Grid-Gewichtung
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titel
        title_label = ttk.Label(main_frame, text="MIDI Analyzer", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # ===== Erste MIDI-Datei =====
        ttk.Label(main_frame, text="Referenz MIDI-Datei:", 
                 font=('Arial', 10, 'bold')).grid(row=1, column=0, columnspan=3, 
                                                   sticky=tk.W, pady=(10, 5))
        
        ttk.Entry(main_frame, textvariable=self.file1_path, width=60).grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(main_frame, text="Durchsuchen...", 
                  command=self.browse_file1).grid(row=2, column=2)
        
        # ===== Zweite MIDI-Datei =====
        ttk.Label(main_frame, text="Zu vergleichende MIDI-Datei:", 
                 font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=3, 
                                                   sticky=tk.W, pady=(20, 5))
        
        ttk.Entry(main_frame, textvariable=self.file2_path, width=60).grid(
            row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(main_frame, text="Durchsuchen...", 
                  command=self.browse_file2).grid(row=4, column=2)
        
        # ===== Output-Datei =====
        ttk.Label(main_frame, text="Ausgabe-Datei:", 
                 font=('Arial', 10, 'bold')).grid(row=5, column=0, columnspan=3, 
                                                   sticky=tk.W, pady=(20, 5))
        
        ttk.Entry(main_frame, textvariable=self.output_path, width=60).grid(
            row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(main_frame, text="Speichern unter...", 
                  command=self.browse_output).grid(row=6, column=2)
        
        # ===== Vergleichen Button =====
        self.compare_button = ttk.Button(main_frame, text="MIDI-Dateien vergleichen", 
                                        command=self.start_comparison)
        self.compare_button.grid(row=7, column=0, columnspan=3, pady=30)
        
        # ===== Fortschrittsbalken =====
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress.grid(row=8, column=0, columnspan=3, pady=(0, 10))
        
        # ===== Status-Label =====
        self.status_label = ttk.Label(main_frame, text="Bereit zum Vergleichen", 
                                      font=('Arial', 9))
        self.status_label.grid(row=9, column=0, columnspan=3)
        
        # ===== Log-Bereich =====
        ttk.Label(main_frame, text="Status-Log:", 
                 font=('Arial', 10, 'bold')).grid(row=10, column=0, columnspan=3, 
                                                   sticky=tk.W, pady=(20, 5))
        
        # Frame für Log und Scrollbar
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                      pady=(0, 10))
        main_frame.rowconfigure(11, weight=1)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Log-Text-Widget
        self.log_text = tk.Text(log_frame, height=12, width=70, 
                               yscrollcommand=scrollbar.set, 
                               wrap=tk.WORD, state='disabled',
                               font=('Courier', 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # ===== Buttons am Ende =====
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=12, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Ausgabe-Datei öffnen", 
                  command=self.open_output_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Log löschen", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Beenden", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
    def browse_file1(self):
        """Öffnet Dateiauswahl für die erste MIDI-Datei"""
        filename = filedialog.askopenfilename(
            title="Referenz MIDI-Datei auswählen",
            filetypes=[("MIDI-Dateien", "*.mid *.midi"), ("Alle Dateien", "*.*")],
            initialdir=os.getcwd()
        )
        if filename:
            self.file1_path.set(filename)
            self.log(f"Referenz-Datei ausgewählt: {os.path.basename(filename)}")
            
    def browse_file2(self):
        """Öffnet Dateiauswahl für die zweite MIDI-Datei"""
        filename = filedialog.askopenfilename(
            title="Zu vergleichende MIDI-Datei auswählen",
            filetypes=[("MIDI-Dateien", "*.mid *.midi"), ("Alle Dateien", "*.*")],
            initialdir=os.getcwd()
        )
        if filename:
            self.file2_path.set(filename)
            self.log(f"Vergleichs-Datei ausgewählt: {os.path.basename(filename)}")
            
    def browse_output(self):
        """Öffnet Dateiauswahl für die Ausgabe-Datei"""
        filename = filedialog.asksaveasfilename(
            title="Ausgabe-Datei speichern unter",
            defaultextension=".txt",
            filetypes=[("Text-Dateien", "*.txt"), ("Alle Dateien", "*.*")],
            initialdir=os.getcwd(),
            initialfile="vergleich.txt"
        )
        if filename:
            self.output_path.set(filename)
            self.log(f"Ausgabe-Datei: {os.path.basename(filename)}")
            
    def log(self, message):
        """Fügt eine Nachricht zum Log hinzu"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
    def clear_log(self):
        """Löscht das Log"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
    def update_status(self, message):
        """Aktualisiert die Status-Anzeige"""
        self.status_label.config(text=message)
        
    def start_comparison(self):
        """Startet den Vergleich in einem separaten Thread"""
        file1 = self.file1_path.get()
        file2 = self.file2_path.get()
        output = self.output_path.get()
        
        # Validierung
        if not file1:
            messagebox.showerror("Fehler", "Bitte wählen Sie die erste MIDI-Datei aus!")
            return
        if not file2:
            messagebox.showerror("Fehler", "Bitte wählen Sie die zweite MIDI-Datei aus!")
            return
        if not output:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Ausgabe-Dateipfad an!")
            return
            
        if not os.path.exists(file1):
            messagebox.showerror("Fehler", f"Datei nicht gefunden: {file1}")
            return
        if not os.path.exists(file2):
            messagebox.showerror("Fehler", f"Datei nicht gefunden: {file2}")
            return
        
        # Starte Vergleich in separatem Thread
        thread = threading.Thread(target=self.run_comparison, 
                                 args=(file1, file2, output))
        thread.daemon = True
        thread.start()
        
    def run_comparison(self, file1, file2, output):
        """Führt den Vergleich aus"""
        try:
            # UI aktualisieren
            self.compare_button.config(state='disabled')
            self.progress.start(10)
            self.update_status("Vergleiche MIDI-Dateien...")
            self.log("=" * 60)
            self.log("Starte MIDI-Vergleich...")
            self.log(f"  Datei 1: {os.path.basename(file1)}")
            self.log(f"  Datei 2: {os.path.basename(file2)}")
            
            # Führe Vergleich aus
            result = self.analyzer.compare_files(file1, file2)
            formatted_text = self.formatter.format_comparison(result)
            
            # Speichere
            with open(output, 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            
            # Erfolgsmeldung
            self.log(f"✓ Vergleich erfolgreich!")
            self.log(f"  Ausgabe gespeichert: {output}")
            if result.summary:
                self.log(f"  Unterschiede: {result.summary.total_differences}")
                self.log(f"  Ähnlichkeit: {result.summary.similarity_score * 100:.1f}%")
            self.log("=" * 60)
            self.update_status("Vergleich erfolgreich abgeschlossen!")
            
            # Zeige Erfolgs-Dialog
            self.root.after(0, lambda: messagebox.showinfo(
                "Erfolg", 
                f"Der Vergleich wurde erfolgreich erstellt!\n\nAusgabe-Datei:\n{output}"
            ))
            
        except Exception as e:
            error_msg = str(e)
            self.log(f"✗ FEHLER: {error_msg}")
            self.log("=" * 60)
            self.update_status("Fehler beim Vergleich!")
            
            # Zeige Fehler-Dialog
            self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                "Fehler", 
                f"Beim Vergleich ist ein Fehler aufgetreten:\n\n{msg}"
            ))
            
        finally:
            # UI zurücksetzen
            self.progress.stop()
            self.compare_button.config(state='normal')
            
    def open_output_file(self):
        """Öffnet die Ausgabe-Datei im Standard-Editor"""
        output = self.output_path.get()
        if os.path.exists(output):
            try:
                os.startfile(output)  # Windows
                self.log(f"Öffne Datei: {output}")
            except AttributeError:
                # Für macOS und Linux
                import subprocess
                try:
                    subprocess.run(['open', output])  # macOS
                except FileNotFoundError:
                    subprocess.run(['xdg-open', output])  # Linux
        else:
            messagebox.showwarning("Warnung", 
                                 "Die Ausgabe-Datei existiert noch nicht!\n"
                                 "Bitte führen Sie zuerst einen Vergleich durch.")


def main():
    root = tk.Tk()
    app = MidiCompareGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
