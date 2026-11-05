import os
import sys

from fpdf import FPDF
from markdown_it import MarkdownIt

BASE = os.path.dirname(os.path.abspath(__file__))

INK = (25, 35, 55)
BLUE = (24, 55, 110)
BLUE_MED = (52, 88, 150)
GRAY = (105, 105, 115)
LIGHT = (244, 246, 250)
RULE = (205, 212, 228)


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
                    meta[k.strip()] = v.strip().strip('"')
            text = text[end + 4:]
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
        elif t == "softbreak" or t == "hardbreak":
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
        self.set_text_color(*GRAY)
        self.cell(0, 5, self.titre, align="L")
        self.cell(0, 5, self.sous_titre, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*RULE)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y() + 1, self.w - self.r_margin, self.get_y() + 1)
        self.ln(5)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(*RULE)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 5, f"Page {self.page_no()}/{{nb}}", align="C")


def title_block(pdf, meta, semaine, periode):
    pdf.set_fill_color(*BLUE)
    y0 = pdf.get_y()
    pdf.rect(pdf.l_margin, y0, pdf.w - pdf.l_margin - pdf.r_margin, 30, style="F")
    pdf.set_xy(pdf.l_margin + 6, y0 + 6)
    pdf.set_font("DejaVu", "B", 17)
    pdf.set_text_color(255, 255, 255)
    pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 12, 7.5, meta["titre"], new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin + 6)
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(215, 224, 240)
    label = " — ".join(x for x in [semaine, periode] if x)
    if label:
        pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 12, 5.5, label, new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(y0 + 34)
    if meta.get("auteur"):
        pdf.set_font("DejaVu", "I", 9.5)
        pdf.set_text_color(*GRAY)
        pdf.multi_cell(0, 5.5, meta["auteur"], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
    pdf.set_text_color(*INK)


def build_pdf(md_path, out_path):
    with open(md_path, encoding="utf-8") as f:
        raw = f.read()
    meta, body = parse_front_matter(raw)

    font_dir = find_font_dir()
    pdf = FichePDF(format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(18, 16, 18)
    pdf.add_font("DejaVu", "", os.path.join(font_dir, "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", os.path.join(font_dir, "DejaVuSans-Bold.ttf"))
    pdf.add_font("DejaVu", "I", os.path.join(font_dir, "DejaVuSans-Oblique.ttf"))
    pdf.add_font("DejaVu", "BI", os.path.join(font_dir, "DejaVuSans-BoldOblique.ttf"))

    semaine = meta.get("semaine", "")
    periode = meta.get("periode", "")
    FichePDF.titre = meta.get("titre", os.path.basename(md_path))
    FichePDF.sous_titre = f"{semaine} — {periode}" if periode else semaine

    tokens = MarkdownIt("gfm-like").parse(body)

    pdf.add_page()
    pdf.set_text_color(*INK)
    if meta.get("titre"):
        title_block(pdf, meta, semaine, periode)

    i, n = 0, len(tokens)
    while i < n:
        tok = tokens[i]
        t = tok.type
        if t == "heading_open":
            level = int(tok.tag[1])
            content = inline_to_md(tokens[i + 1].children) if i + 1 < n and tokens[i + 1].type == "inline" else ""
            sizes = {1: 14.5, 2: 12, 3: 10.5}
            pdf.ln(3 if level > 1 else 4)
            if level == 1:
                pdf.set_font("DejaVu", "B", sizes[level])
                pdf.set_text_color(*BLUE)
                pdf.multi_cell(0, 7, content.strip(), markdown=True, new_x="LMARGIN", new_y="NEXT")
                pdf.set_draw_color(*BLUE)
                pdf.set_line_width(0.5)
                pdf.line(pdf.l_margin, pdf.get_y() + 0.5, pdf.w - pdf.r_margin, pdf.get_y() + 0.5)
                pdf.ln(2)
            elif level == 2:
                pdf.set_font("DejaVu", "B", sizes[level])
                pdf.set_text_color(*BLUE_MED)
                pdf.multi_cell(0, 6.5, content.strip(), markdown=True, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(0.5)
            else:
                pdf.set_font("DejaVu", "B", sizes[level])
                pdf.set_text_color(*INK)
                pdf.multi_cell(0, 6, content.strip(), markdown=True, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*INK)
            i += 2
            continue
        if t == "paragraph_open":
            content = inline_to_md(tokens[i + 1].children) if i + 1 < n and tokens[i + 1].type == "inline" else ""
            pdf.set_font("DejaVu", "", 10)
            pdf.multi_cell(0, 5.4, content.strip(), markdown=True, align="J", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1.2)
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
                    pdf.set_font("DejaVu", "B" if not ordered else "", 10)
                    pdf.set_text_color(*BLUE_MED)
                    pdf.set_x(pdf.l_margin + 5)
                    pdf.cell(5, 5.4, label)
                    pdf.set_text_color(*INK)
                    pdf.set_font("DejaVu", "", 10)
                    pdf.multi_cell(0, 5.4, " ".join(parts), markdown=True, align="J", new_x="LMARGIN", new_y="NEXT")
                    if ordered:
                        idx += 1
                else:
                    i += 1
            pdf.ln(1)
            i += 1
            continue
        if t == "blockquote_open":
            i += 1
            x = pdf.l_margin + 4
            y = pdf.get_y()
            pdf.set_font("DejaVu", "I", 10)
            pdf.set_text_color(*GRAY)
            pdf.set_fill_color(*LIGHT)
            pdf.set_x(x)
            while i < n and tokens[i].type != "blockquote_close":
                if tokens[i].type == "paragraph_open" and i + 1 < n and tokens[i + 1].type == "inline":
                    content = inline_to_md(tokens[i + 1].children).strip()
                    pdf.multi_cell(pdf.w - pdf.r_margin - x, 5.4, content, markdown=True, fill=True, new_x="LMARGIN", new_y="NEXT")
                    i += 2
                else:
                    i += 1
            pdf.set_draw_color(*BLUE_MED)
            pdf.set_line_width(0.8)
            pdf.line(pdf.l_margin + 1.5, y, pdf.l_margin + 1.5, pdf.get_y())
            pdf.set_text_color(*INK)
            pdf.ln(1.5)
            i += 1
            continue
        if t == "hr":
            pdf.ln(2)
            pdf.set_draw_color(*RULE)
            pdf.set_line_width(0.3)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(2)
            i += 1
            continue
        if t == "table_open":
            i += 1
            pdf.set_font("DejaVu", "", 9)
            first = True
            while i < n and tokens[i].type != "table_close":
                if tokens[i].type == "tr_open":
                    i += 1
                    cells = []
                    is_head = False
                    while i < n and tokens[i].type != "tr_close":
                        if tokens[i].type in ("th_open", "td_open"):
                            is_head = is_head or tokens[i].type == "th_open"
                            i += 1
                            if i < n and tokens[i].type == "inline":
                                cells.append(inline_to_md(tokens[i].children).strip())
                                i += 1
                        else:
                            i += 1
                    if cells:
                        if is_head:
                            pdf.set_fill_color(*BLUE)
                            pdf.set_text_color(255, 255, 255)
                            pdf.set_font("DejaVu", "B", 9)
                        elif first:
                            pdf.set_fill_color(*LIGHT)
                            pdf.set_text_color(*INK)
                            pdf.set_font("DejaVu", "", 9)
                        else:
                            pdf.set_fill_color(255, 255, 255)
                            pdf.set_text_color(*INK)
                            pdf.set_font("DejaVu", "", 9)
                        pdf.multi_cell(0, 5.2, " | ".join(cells), fill=True, new_x="LMARGIN", new_y="NEXT")
                        first = False
                else:
                    i += 1
            pdf.set_text_color(*INK)
            pdf.ln(1.5)
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
