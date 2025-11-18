import customtkinter as ctk
import tkinter as tk
import colorsys


ctk.set_appearance_mode("system")  # Modes: "system" (standard), "dark", "light"
ctk.set_default_color_theme("green")


def fmt(x):
    """Wandelt Zahl in deutsche Schreibweise mit Komma um."""
    return f"{x:.2f}".replace(".", ",")


def berechne_teilstuecke(gesamtlänge, teilstücklänge, abstand, offset):
    nutzbare_länge = gesamtlänge - 2 * offset
    if nutzbare_länge < teilstücklänge:
        return [], 0, offset, offset, 0

    anzahl = int((nutzbare_länge + abstand) // (teilstücklänge + abstand))
    belegte_länge = anzahl * teilstücklänge + (anzahl - 1) * abstand
    rest_links = (gesamtlänge - belegte_länge) / 2
    rest_rechts = rest_links

    teile = []
    for i in range(anzahl):
        start = rest_links + i * (teilstücklänge + abstand)
        mitte = start + teilstücklänge / 2
        ende = start + teilstücklänge
        teile.append((start, mitte, ende))

    empfohlene_gesamtlänge = (anzahl * teilstücklänge) + ((anzahl - 1) * abstand) + 2 * offset
    return teile, anzahl, rest_links, rest_rechts, empfohlene_gesamtlänge


class Visualisierung(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Längen-Aufteilung")
        self.geometry("1000x600")

        # Eingabe-Bereich
        eingabe_frame = ctk.CTkFrame(self)
        eingabe_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.gesamt = ctk.CTkEntry(eingabe_frame, placeholder_text="Gesamtlänge (mm)")
        self.gesamt.pack(pady=5)
        self.teil = ctk.CTkEntry(eingabe_frame, placeholder_text="Teilstück (mm)")
        self.teil.pack(pady=5)
        self.abstand = ctk.CTkEntry(eingabe_frame, placeholder_text="Abstand (mm)")
        self.abstand.pack(pady=5)
        self.offset = ctk.CTkEntry(eingabe_frame, placeholder_text="Offset (mm)")
        self.offset.pack(pady=5)
        self.anzahl = ctk.CTkEntry(eingabe_frame, placeholder_text="Anzahl")
        self.anzahl.pack(pady=5)

        # Enter-Taste aktivieren
        for entry in (self.gesamt, self.teil, self.abstand, self.offset, self.anzahl):
            entry.bind("<Return>", lambda event: self.zeichnen())

        self.form_var = ctk.StringVar(value="kreis")
        ctk.CTkLabel(eingabe_frame, text="Form:").pack(pady=(10, 0))
        ctk.CTkRadioButton(eingabe_frame, text="Kreis", variable=self.form_var, value="kreis").pack()
        ctk.CTkRadioButton(eingabe_frame, text="Quadrat", variable=self.form_var, value="quadrat").pack()

        self.button = ctk.CTkButton(eingabe_frame, text="Zeichnen", command=self.zeichnen)
        self.button.pack(pady=10)

        self.info = ctk.CTkLabel(eingabe_frame, text="", justify="left")
        self.info.pack(pady=10)

        # appearance_mode
        if ctk.get_appearance_mode() == "Dark":
            print("Dark mode aktiv")
            self.canvas_bg = "#1e1e1e"
            self.canvas_outline = "#FFFFFF"
        else:
            print("Light mode aktiv")
            self.canvas_bg = "#e6e6e6"
            self.canvas_outline = "#000000"

        # Zeichenfläche
        self.canvas = tk.Canvas(self, bg= self.canvas_bg, highlightthickness=0)
        self.canvas.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def zeichnen(self):
        self.canvas.delete("all")

        eingaben = {
            "gesamtlänge": self.gesamt.get().replace(",", "."),
            "teilstück": self.teil.get().replace(",", "."),
            "abstand": self.abstand.get().replace(",", "."),
            "offset": self.offset.get().replace(",", "."),
            "anzahl": self.anzahl.get().replace(",", "."),
        }

        leere_felder = [k for k, v in eingaben.items() if v.strip() == ""]

        if len(leere_felder) == 0:
            try:
                gesamtlänge = float(eingaben["gesamtlänge"])
                teilstücklänge = float(eingaben["teilstück"])
                abstand = float(eingaben["abstand"])
                offset = float(eingaben["offset"])
                anzahl = int(float(eingaben["anzahl"]))
            except ValueError:
                self.info.configure(text="Bitte gültige Zahlen eingeben.")
                return

        elif len(leere_felder) == 1:
            feld = leere_felder[0]
            try:
                gesamtlänge = float(eingaben["gesamtlänge"]) if eingaben["gesamtlänge"] else None
                teilstücklänge = float(eingaben["teilstück"]) if eingaben["teilstück"] else None
                abstand = float(eingaben["abstand"]) if eingaben["abstand"] else None
                offset = float(eingaben["offset"]) if eingaben["offset"] else None
                anzahl = int(float(eingaben["anzahl"])) if eingaben["anzahl"] else None
            except ValueError:
                self.info.configure(text="Ungültige Eingabe.")
                return

            if feld == "gesamtlänge" and None not in (teilstücklänge, abstand, offset, anzahl):
                gesamtlänge = (teilstücklänge * anzahl) + ((anzahl - 1) * abstand) + 2 * offset
                self.gesamt.delete(0, "end")
                self.gesamt.insert(0, fmt(gesamtlänge))
            elif feld == "teilstück" and None not in (gesamtlänge, abstand, offset, anzahl):
                teilstücklänge = (gesamtlänge - ((anzahl - 1) * abstand) - 2 * offset) / anzahl
                self.teil.delete(0, "end")
                self.teil.insert(0, fmt(teilstücklänge))
            elif feld == "abstand" and None not in (gesamtlänge, teilstücklänge, offset, anzahl):
                if anzahl > 1:
                    abstand = (gesamtlänge - (anzahl * teilstücklänge) - 2 * offset) / (anzahl - 1)
                else:
                    abstand = 0
                self.abstand.delete(0, "end")
                self.abstand.insert(0, fmt(abstand))
            elif feld == "offset" and None not in (gesamtlänge, teilstücklänge, abstand, anzahl):
                offset = (gesamtlänge - ((anzahl * teilstücklänge) + ((anzahl - 1) * abstand))) / 2
                self.offset.delete(0, "end")
                self.offset.insert(0, fmt(offset))
            elif feld == "anzahl" and None not in (gesamtlänge, teilstücklänge, abstand, offset):
                anzahl = int((gesamtlänge - 2 * offset + abstand) // (teilstücklänge + abstand))
                self.anzahl.delete(0, "end")
                self.anzahl.insert(0, str(anzahl))
            else:
                self.info.configure(text="Zu wenige Daten zum Berechnen.")
                return

        else:
            self.info.configure(text="Bitte nur ein Feld frei lassen.")
            return

        teile, anzahl, rest_links, rest_rechts, empfohlene = berechne_teilstuecke(
            gesamtlänge, teilstücklänge, abstand, offset
        )

        breite = self.canvas.winfo_width()
        höhe = self.canvas.winfo_height()
        if breite < 10 or höhe < 10:
            breite, höhe = 900, 500

        skala = (breite * 0.8) / gesamtlänge
        kasten_höhe = teilstücklänge * skala + 2 * offset * skala
        y0 = höhe * 0.25
        y1 = y0 + kasten_höhe
        text_y = y1 + 50

        self.canvas.create_rectangle(breite * 0.1, y0, breite * 0.9, y1, outline=self.canvas_outline, width=2)

        farben = []
        for i in range(anzahl):
            rgb = colorsys.hsv_to_rgb(i / max(1, anzahl), 0.9, 1.0)
            farben.append('#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)))

        for i, (start, mitte, ende) in enumerate(teile):
            mitte_x = breite * 0.1 + mitte * skala
            w = teilstücklänge * skala / 2
            farbe = farben[i]

            if self.form_var.get() == "quadrat":
                self.canvas.create_rectangle(mitte_x - w, y0 + offset * skala, mitte_x + w,
                                             y1 - offset * skala, fill=farbe, outline="")
            else:
                self.canvas.create_oval(mitte_x - w, y0 + offset * skala, mitte_x + w,
                                        y1 - offset * skala, fill=farbe, outline="")

            text = f"Start: {fmt(start)} mm | Mitte: {fmt(mitte)} mm | Ende: {fmt(ende)} mm"
            self.canvas.create_text(breite * 0.1 + mitte * skala, text_y + i * 20,
                                    text=text, fill=farbe, font=("Consolas", 10, "bold"), anchor="center")

        # Anzeige links (exakt: Rest == Offset)
        if rest_links == offset:
            self.info.configure(text="Perfekte Aufteilung")
        else:
            self.info.configure(
                text=f"Rest links/rechts: {fmt(rest_links)} mm\nEmpfohlene Länge: {fmt(empfohlene)} mm"
            )


if __name__ == "__main__":
    app = Visualisierung()
    app.mainloop()
