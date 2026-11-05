import glob
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from generer_fiche import build_pdf


def main():
    fichiers = sorted(glob.glob(os.path.join(BASE, "contenus", "*.md")))
    if not fichiers:
        print("Aucun contenu dans contenus/")
        return
    for f in fichiers:
        out = os.path.join(BASE, "sorties", os.path.splitext(os.path.basename(f))[0] + ".pdf")
        print(build_pdf(f, out))


if __name__ == "__main__":
    main()
