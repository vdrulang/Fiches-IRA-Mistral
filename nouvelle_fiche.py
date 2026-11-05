import os
import sys
from datetime import date, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
MODELE = os.path.join(BASE, "modeles", "modele_fiche.md")
CONTENUS = os.path.join(BASE, "contenus")


def lundi_de_la_semaine(d):
    return d - timedelta(days=d.weekday())


def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "theme"
    slug = slug.lower().replace(" ", "-")
    slug = "".join(c for c in slug if c.isalnum() or c in "-_")
    today = date.today()
    iso_year, iso_week, _ = today.isocalendar()
    lundi = lundi_de_la_semaine(today)
    dimanche = lundi + timedelta(days=6)
    periode = f"du {lundi.strftime('%d/%m/%Y')} au {dimanche.strftime('%d/%m/%Y')}"
    semaine = f"Semaine {iso_week:02d} ({iso_year})"

    with open(MODELE, encoding="utf-8") as f:
        contenu = f.read()
    contenu = contenu.replace("{{SEMAINE}}", f"{iso_year}-S{iso_week:02d}")
    contenu = contenu.replace("{{PERIODE}}", periode)
    contenu = contenu.replace("{{TITRE}}", slug.replace("-", " ").capitalize())

    os.makedirs(CONTENUS, exist_ok=True)
    path = os.path.join(CONTENUS, f"{iso_year}-S{iso_week:02d}_{slug}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(path)


if __name__ == "__main__":
    main()
