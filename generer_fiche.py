import os
import re
import sys

from fpdf import FPDF
from markdown_it import MarkdownIt

BASE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = None


def find_font_dir():
    import matplotlib

    return os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")


def parse_front_matter(text):
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            text = text[end + 4 :]
    return meta, text


def inline_to_md(children):
    out = []
    for tok in children or []:
        t = tok.type
        if t == "text":
            out.append(tok.content)
        elif t == "strong_open":
            out.append("**")
        elif t == "strong_close":
            out.append("**")
        elif t == "em_open":
            out.append("*")
        elif t == "em_close":
            out.append("*")
        elif t == "code_inline":
            out.append(tok.content)
        elif t == "link_open":
            pass
        elif t == "link_close":
            pass
        elif t == "softbreak":
            out.append("\n")
        elif t == "hardbreak":
            out.append("\n")
        else:
            out.append(tok.content if tok.content else "")
    return "".join(out)


class FichePDF(FPDF):
    titre = ""
    sous_titre = ""

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(110, 110, 110)
        self.cell(0, 5, self.titre, align="L")
        self.cell(0, 5, self.sous_titre, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y() + 1, self.w - self.r_margin, self.get_y() + 1)
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(110, 110, 110)
        self.cell(0, 5, f"Page {self.page_no()}/{{nb}}", align="C")


def build_pdf(md_path, out_path):
    with open(md_path, encoding="utf-8") as f:
        raw = f.read()
    meta, body = parse_front_matter(raw)

    font_dir = find_font_dir()
    pdf = FichePDF(format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_font("DejaVu", "", os.path.join(font_dir, "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", os.path.join(font_dir, "DejaVuSans-Bold.ttf"))
    pdf.add_font("DejaVu", "I", os.path.join(font_dir, "DejaVuSans-Oblique.ttf"))
    pdf.add_font("DejaVu", "BI", os.path.join(font_dir, "DejaVuSans-BoldOblique.ttf"))

    titre = meta.get("titre", os.path.basename(md_path))
    semaine = meta.get("semaine", "")
    periode = meta.get("periode", "")
    FichePDF.titre = titre
    FichePDF.sous_titre = f"{semaine} — {periode}" if periode else semaine

    md = MarkdownIt("gfm-like")
    tokens = md.parse(body)

    pdf.add_page()
    pdf.set_text_color(0, 0, 0)

    if meta.get("titre"):
        pdf.set_font("DejaVu", "B", 20)
        pdf.multi_cell(0, 9, meta["titre"], new_x="LMARGIN", new_y="NEXT")
        if semaine or periode:
            pdf.set_font("DejaVu", "", 11)
            pdf.set_text_color(70, 70, 70)
            label = " — ".join(x for x in [semaine, periode] if x)
            pdf.multi_cell(0, 6, label, new_x="LMARGIN", new_y="NEXT")
        if meta.get("auteur"):
            pdf.set_font("DejaVu", "I", 10)
            pdf.multi_cell(0, 6, meta["auteur"], new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
        pdf.set_draw_color(30, 30, 30)
        pdf.set_line_width(0.6)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(4)

    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        t = tok.type
        if t == "heading_open":
            level = int(tok.tag[1])
            content = inline_to_md(tokens[i + 1].children) if i + 1 < n and tokens[i + 1].type == "inline" else ""
            sizes = {1: 15, 2: 12.5, 3: 11}
            pdf.ln(2 if level > 1 else 3)
            pdf.set_font("DejaVu", "B", sizes.get(level, 11))
            if level == 1:
                pdf.set_text_color(20, 40, 80)
            elif level == 2:
                pdf.set_text_color(40, 60, 110)
            else:
                pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 7, content.strip(), markdown=True, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            if level == 1:
                pdf.set_draw_color(150, 160, 190)
                pdf.set_line_width(0.3)
                pdf.line(pdf.l_margin, pdf.get_y() + 0.5, pdf.w - pdf.r_margin, pdf.get_y() + 0.5)
                pdf.ln(1)
            i += 2
            continue
        if t == "paragraph_open":
            content = inline_to_md(tokens[i + 1].children) if i + 1 < n and tokens[i + 1].type == "inline" else ""
            pdf.set_font("DejaVu", "", 10)
            pdf.multi_cell(0, 5.2, content.strip(), markdown=True, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            i += 2
            continue
        if t in ("bullet_list_open", "ordered_list_open"):
            ordered = t == "ordered_list_open"
            i += 1
            idx = 1
            while i < n and tokens[i].type != ("bullet_list_close" if not ordered else "ordered_list_close"):
                if tokens[i].type == "list_item_open":
                    i += 1
                    parts = []
                    while i < n and tokens[i].type != "list_item_close":
                        if tokens[i].type == "paragraph_open" and i + 1 < n and tokens[i + 1].type == "inline":
                            parts.append(inline_to_md(tokens[i + 1].children).strip())
                            i += 2
                        else:
                            i += 1
                    label = f"{idx}." if ordered else "•"
                    pdf.set_font("DejaVu", "", 10)
                    x0 = pdf.l_margin + 4
                    pdf.set_x(x0)
                    pdf.cell(5, 5.2, label)
                    pdf.multi_cell(0, 5.2, " ".join(parts), markdown=True, new_x="LMARGIN", new_y="NEXT")
                    pdf.set_x(pdf.l_margin)
                    if ordered:
                        idx += 1
                else:
                    i += 1
            i += 1
            pdf.ln(1)
            continue
        if t == "blockquote_open":
            i += 1
            pdf.set_font("DejaVu", "I", 10)
            pdf.set_text_color(60, 60, 60)
            x = pdf.l_margin + 3
            pdf.set_x(x)
            pdf.set_draw_color(120, 120, 120)
            y = pdf.get_y()
            while i < n and tokens[i].type != "blockquote_close":
                if tokens[i].type == "paragraph_open" and i + 1 < n and tokens[i + 1].type == "inline":
                    content = inline_to_md(tokens[i + 1].children).strip()
                    pdf.multi_cell(pdf.w - pdf.r_margin - x, 5.2, content, markdown=True, new_x="LMARGIN", new_y="NEXT")
                    i += 2
                else:
                    i += 1
            pdf.set_draw_color(120, 120, 120)
            pdf.line(x - 2, y, x - 2, pdf.get_y())
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1)
            i += 1
            continue
        if t == "hr":
            pdf.ln(2)
            pdf.set_draw_color(180, 180, 180)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(2)
            i += 1
            continue
        if t == "table_open":
            i += 1
            pdf.set_font("DejaVu", "", 9)
            while i < n and tokens[i].type != "table_close":
                if tokens[i].type == "tr_open":
                    i += 1
                    cells = []
                    while i < n and tokens[i].type != "tr_close":
                        if tokens[i].type in ("th_open", "td_open"):
                            i += 1
                            if i < n and tokens[i].type == "inline":
                                cells.append(inline_to_md(tokens[i].children).strip())
                                i += 1
                        else:
                            i += 1
                    if cells:
                        pdf.multi_cell(0, 5, " | ".join(cells), new_x="LMARGIN", new_y="NEXT")
                else:
                    i += 1
            pdf.ln(1)
            i += 1
            continue
        i += 1

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pdf.output(out_path)
    return out_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python generer_fiche.py <fichier.md> [sortie.pdf]")
        sys.exit(1)
    md_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        BASE, "sorties", os.path.splitext(os.path.basename(md_path))[0] + ".pdf"
    )
    print(build_pdf(md_path, out_path))


if __name__ == "__main__":
    main()
