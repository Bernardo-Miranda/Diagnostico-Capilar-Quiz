from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from pathlib import Path
import math


OUT = Path("output/pdf/protocolo-anti-queda-fortalecedor-de-fios.pdf")

W, H = A4
M = 18 * mm

RED = HexColor("#d60b08")
DARK_RED = HexColor("#8f292d")
SOFT_RED = HexColor("#f9dedc")
PINK = HexColor("#f36b63")
INK = HexColor("#1d1113")
MUTED = HexColor("#6f5555")
CREAM = HexColor("#fff7f4")
LIGHT = HexColor("#fff0ed")
GREEN = HexColor("#2f9e55")
SOFT_GREEN = HexColor("#dff6e7")
GOLD = HexColor("#f4b942")
SOFT_GOLD = HexColor("#fff1ce")
GRAY = HexColor("#f6f1ef")


def txt_width(text, font="Helvetica", size=10):
    return stringWidth(str(text), font, size)


def wrap(text, max_width, font="Helvetica", size=10):
    words = str(text).replace("\n", " \n ").split()
    lines = []
    current = ""
    for word in words:
        if word == "\n":
            if current:
                lines.append(current)
                current = ""
            continue
        test = word if not current else current + " " + word
        if txt_width(test, font, size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class PDF:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.c = canvas.Canvas(str(path), pagesize=A4)
        self.page = 0

    def new_page(self, title=None, kicker=None, footer=True):
        if self.page:
            self.c.showPage()
        self.page += 1
        self.bg()
        if title:
            self.header(title, kicker)
        if footer:
            self.footer()

    def save(self):
        self.c.save()

    def bg(self):
        c = self.c
        c.setFillColor(CREAM)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(SOFT_RED)
        c.circle(W + 20 * mm, H - 30 * mm, 80 * mm, fill=1, stroke=0)
        c.setFillColor(HexColor("#ffe9e5"))
        c.circle(-15 * mm, 18 * mm, 52 * mm, fill=1, stroke=0)

    def header(self, title, kicker=None):
        c = self.c
        y = H - 24 * mm
        if kicker:
            pill(c, M, y + 4 * mm, txt_width(kicker.upper(), "Helvetica-Bold", 7) + 10 * mm, 8 * mm, RED, kicker.upper(), CREAM, 7)
            y -= 8 * mm
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 21)
        for line in wrap(title, W - 2 * M, "Helvetica-Bold", 21):
            c.drawString(M, y, line)
            y -= 8.5 * mm
        c.setStrokeColor(SOFT_RED)
        c.setLineWidth(1.2)
        c.line(M, y - 2 * mm, W - M, y - 2 * mm)

    def footer(self):
        c = self.c
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(M, 10 * mm, "Protocolo Anti Queda Fortalecedor de Fios")
        c.drawRightString(W - M, 10 * mm, f"Pagina {self.page}")


def pill(c, x, y, w, h, fill, text, text_color=colors.white, size=8):
    c.setFillColor(fill)
    c.roundRect(x, y - h, w, h, h / 2, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", size)
    c.drawCentredString(x + w / 2, y - h + (h - size) / 2 + 1.2, text)


def card(c, x, y, w, h, fill=colors.white, stroke=SOFT_RED, radius=7 * mm):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.8)
    c.roundRect(x, y - h, w, h, radius, fill=1, stroke=1)


def paragraph(c, text, x, y, width, size=10.5, leading=5.4 * mm, font="Helvetica", color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrap(text, width, font, size):
        c.drawString(x, y, line)
        y -= leading
    return y


def bullet_list(c, items, x, y, width, size=10.2, gap=2.1 * mm, bullet_color=RED):
    for item in items:
        lines = wrap(item, width - 8 * mm, "Helvetica", size)
        c.setFillColor(bullet_color)
        c.circle(x + 1.8 * mm, y + 1.4 * mm, 1.2 * mm, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica", size)
        for line in lines:
            c.drawString(x + 6 * mm, y, line)
            y -= 5.2 * mm
        y -= gap
    return y


def section_label(c, text, x, y, color=RED):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x, y, text.upper())
    c.setStrokeColor(color)
    c.setLineWidth(1.4)
    c.line(x, y - 2.5, x + 22 * mm, y - 2.5)


def draw_hair_roots(c, x, y, w, h):
    card(c, x, y, w, h, fill=HexColor("#fffdfb"), stroke=HexColor("#f2c7c3"))
    base_y = y - h + 22 * mm
    c.setFillColor(HexColor("#eeb9a7"))
    c.roundRect(x + 10 * mm, base_y, w - 20 * mm, 21 * mm, 8 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#b87968"))
    for i in range(9):
        px = x + 18 * mm + i * (w - 36 * mm) / 8
        c.ellipse(px - 3 * mm, base_y + 7 * mm, px + 3 * mm, base_y + 13 * mm, fill=1, stroke=0)
        c.setStrokeColor(HexColor("#3c2222"))
        c.setLineWidth(2)
        c.bezier(px, base_y + 12 * mm, px - 2 * mm, y - h + 45 * mm, px - 1 * mm, y - 20 * mm, px - 8 * mm, y - 8 * mm)
        c.setStrokeColor(HexColor("#6e3936"))
        c.setLineWidth(1.1)
        c.bezier(px + 1 * mm, base_y + 12 * mm, px + 2 * mm, y - h + 44 * mm, px + 3 * mm, y - 22 * mm, px + 8 * mm, y - 10 * mm)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 12 * mm, y - 12 * mm, "Raiz forte + couro cabeludo ativo")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawString(x + 12 * mm, y - 17 * mm, "Limpeza, massagem e nutricao trabalhando juntas.")


def draw_food_plate(c, x, y, w, h):
    card(c, x, y, w, h, fill=HexColor("#fffdfb"), stroke=HexColor("#f2c7c3"))
    cx, cy = x + w / 2, y - h / 2 - 3 * mm
    c.setFillColor(HexColor("#ffffff"))
    c.setStrokeColor(HexColor("#e7d2cb"))
    c.setLineWidth(2)
    c.circle(cx, cy, min(w, h) * 0.31, fill=1, stroke=1)
    foods = [
        (GREEN, -16, 8, "Fe"),
        (GOLD, 9, 12, "Zn"),
        (HexColor("#e85d75"), 17, -8, "B"),
        (HexColor("#f6a04d"), -4, -13, "C"),
        (HexColor("#9b5de5"), -22, -8, "D"),
    ]
    for color, dx, dy, label in foods:
        c.setFillColor(color)
        c.circle(cx + dx * mm, cy + dy * mm, 8 * mm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx + dx * mm, cy + dy * mm - 2.5, label)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 12 * mm, y - 12 * mm, "Nutrientes de dentro para fora")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawString(x + 12 * mm, y - 17 * mm, "Proteinas, ferro, zinco, vitaminas e agua.")


def draw_calendar(c, x, y, w, h):
    card(c, x, y, w, h, fill=colors.white, stroke=HexColor("#f2c7c3"))
    c.setFillColor(RED)
    c.roundRect(x, y - 13 * mm, w, 13 * mm, 7 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 8 * mm, y - 9 * mm, "Plano de 21 dias")
    cols, rows = 7, 3
    cell_w = (w - 16 * mm) / cols
    cell_h = (h - 27 * mm) / rows
    start_x = x + 8 * mm
    start_y = y - 20 * mm
    day = 1
    for r in range(rows):
        for col in range(cols):
            px = start_x + col * cell_w
            py = start_y - r * cell_h
            c.setFillColor(HexColor("#fff1ef") if day % 2 else HexColor("#ffffff"))
            c.setStrokeColor(HexColor("#f0cbc7"))
            c.roundRect(px, py - cell_h + 2 * mm, cell_w - 2 * mm, cell_h - 2 * mm, 2.5 * mm, fill=1, stroke=1)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 8.5)
            c.drawCentredString(px + cell_w / 2 - 1 * mm, py - cell_h / 2 - 1, str(day))
            day += 1


def draw_routine_icons(c, x, y, w):
    labels = [
        ("1", "Limpar", "preparar o couro cabeludo"),
        ("2", "Massagear", "ativar circulacao local"),
        ("3", "Nutrir", "fortalecer a raiz do fio"),
    ]
    gap = 5 * mm
    col_w = (w - 2 * gap) / 3
    for i, (num, title, sub) in enumerate(labels):
        px = x + i * (col_w + gap)
        card(c, px, y, col_w, 40 * mm, fill=colors.white, stroke=HexColor("#f0c2bd"))
        c.setFillColor(RED)
        c.circle(px + 13 * mm, y - 14 * mm, 7 * mm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(px + 13 * mm, y - 18 * mm, num)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(px + 25 * mm, y - 13 * mm, title)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8.5)
        for line in wrap(sub, col_w - 30 * mm, "Helvetica", 8.5):
            c.drawString(px + 25 * mm, y - 19 * mm, line)
            y -= 0


def draw_cover(pdf):
    c = pdf.c
    pdf.page += 1
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(RED)
    c.rect(0, H * 0.55, W, H * 0.45, fill=1, stroke=0)
    c.setFillColor(DARK_RED)
    c.circle(W - 18 * mm, H - 18 * mm, 60 * mm, fill=1, stroke=0)
    c.setFillColor(PINK)
    c.circle(30 * mm, H - 20 * mm, 38 * mm, fill=1, stroke=0)
    draw_hair_roots(c, M, H - 48 * mm, W - 2 * M, 76 * mm)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 31)
    y = H - 145 * mm
    for line in ["Protocolo Anti Queda", "Fortalecedor de Fios"]:
        c.drawString(M, y, line)
        y -= 12 * mm
    c.setFillColor(HexColor("#ffe4df"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(M, y - 2 * mm, "Guia completo digital - Acesso imediato")
    c.setStrokeColor(colors.white)
    c.setLineWidth(1.2)
    c.line(M, y - 12 * mm, W - M, y - 12 * mm)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 11.5)
    y -= 25 * mm
    for line in wrap("O protocolo de 3 passos para aplicar em casa, fortalecer a raiz dos fios e acompanhar sua evolucao nos proximos 21 dias.", W - 2 * M, "Helvetica", 11.5):
        c.drawString(M, y, line)
        y -= 6 * mm
    pill(c, M, 32 * mm, 58 * mm, 10 * mm, colors.white, "MENOS DE 10 MIN/DIA", RED, 8)
    pill(c, M + 64 * mm, 32 * mm, 55 * mm, 10 * mm, colors.white, "PDF + VIDEOS", RED, 8)
    pill(c, M + 125 * mm, 32 * mm, 48 * mm, 10 * mm, colors.white, "21 DIAS", RED, 8)


def draw_intro(pdf):
    c = pdf.c
    pdf.new_page("Como usar este protocolo", "Comece aqui")
    y = H - 55 * mm
    y = paragraph(c, "Este material foi criado para ser simples, visual e aplicavel. A proposta e combinar tres frentes: cuidado externo do couro cabeludo, massagem de ativacao e fortalecimento interno com nutrientes.", M, y, W - 2 * M, 11.5, 6.3 * mm)
    y -= 6 * mm
    draw_routine_icons(c, M, y, W - 2 * M)
    y -= 51 * mm
    section_label(c, "O que voce recebe", M, y)
    y -= 8 * mm
    y = bullet_list(c, [
        "Protocolo diario de 3 passos para aplicar em casa em menos de 10 minutos.",
        "Lista de nutrientes essenciais para fortalecer a raiz do fio de dentro para fora.",
        "Rotina de limpeza e massagem para melhorar o cuidado com o couro cabeludo.",
        "Sete habitos comuns que podem enfraquecer os fios sem voce perceber.",
        "Receitas naturais caseiras, guia alimentar e checklist de 21 dias.",
        "Orientacoes especificas para cada diagnostico do quiz."
    ], M, y, W - 2 * M)
    y -= 3 * mm
    card(c, M, y, W - 2 * M, 33 * mm, fill=SOFT_GOLD, stroke=GOLD)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(M + 8 * mm, y - 10 * mm, "Aviso importante")
    paragraph(c, "Este guia e educativo e nao substitui uma avaliacao medica ou dermatologica. Se a queda for intensa, acompanhada de dor, feridas, coceira persistente ou falhas rapidas, procure um profissional.", M + 8 * mm, y - 17 * mm, W - 2 * M - 16 * mm, 9.3, 4.5 * mm)


def draw_summary(pdf):
    c = pdf.c
    pdf.new_page("Mapa do protocolo", "Visao geral")
    y = H - 54 * mm
    items = [
        ("01", "Preparacao", "Entenda a rotina diaria e prepare seu couro cabeludo para receber o cuidado."),
        ("02", "3 passos", "Limpar, massagear e nutrir - a base do protocolo diario."),
        ("03", "Nutrientes", "Veja o que favorece a raiz do fio e como montar refeicoes mais inteligentes."),
        ("04", "Habitos", "Remova os comportamentos que sabotam a densidade e a resistencia do cabelo."),
        ("05", "Diagnostico", "Adapte o cuidado conforme o resultado do quiz."),
        ("06", "21 dias", "Acompanhe sua execucao diaria com checklist simples."),
    ]
    for num, title, desc in items:
        card(c, M, y, W - 2 * M, 26 * mm, fill=colors.white, stroke=HexColor("#f0c2bd"))
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(M + 8 * mm, y - 15 * mm, num)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(M + 28 * mm, y - 10 * mm, title)
        paragraph(c, desc, M + 28 * mm, y - 16 * mm, W - 2 * M - 35 * mm, 9.5, 4.5 * mm, color=MUTED)
        y -= 30 * mm


def draw_three_steps(pdf):
    c = pdf.c
    pdf.new_page("O protocolo diario de 3 passos", "Menos de 10 minutos")
    y = H - 54 * mm
    draw_hair_roots(c, M, y, W - 2 * M, 70 * mm)
    y -= 82 * mm
    steps = [
        ("Passo 1 - Limpeza inteligente", "Remover oleosidade excessiva, residuos e acumulo de produtos sem agredir a fibra. O objetivo e deixar o couro cabeludo respirando melhor."),
        ("Passo 2 - Massagem de ativacao", "Estimular a circulacao local com movimentos leves e constantes. Nunca use unha, nunca force e nunca transforme a massagem em atrito agressivo."),
        ("Passo 3 - Nutricao e constancia", "Fortalecer a raiz exige repeticao. A combinacao de proteinas, minerais, vitaminas, agua e sono sustenta o ambiente que favorece fios mais resistentes.")
    ]
    for title, desc in steps:
        card(c, M, y, W - 2 * M, 31 * mm, fill=colors.white, stroke=HexColor("#f0c2bd"))
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(M + 8 * mm, y - 10 * mm, title)
        paragraph(c, desc, M + 8 * mm, y - 17 * mm, W - 2 * M - 16 * mm, 9.7, 4.6 * mm, color=INK)
        y -= 36 * mm


def draw_step_page(pdf, step_num, title, subtitle, bullets, illustration):
    c = pdf.c
    pdf.new_page(title, f"Passo {step_num}")
    y = H - 54 * mm
    paragraph(c, subtitle, M, y, W - 2 * M, 11, 5.8 * mm)
    y -= 34 * mm
    if illustration == "roots":
        draw_hair_roots(c, M, y, W - 2 * M, 68 * mm)
    elif illustration == "food":
        draw_food_plate(c, M, y, W - 2 * M, 68 * mm)
    else:
        draw_calendar(c, M, y, W - 2 * M, 68 * mm)
    y -= 80 * mm
    section_label(c, "Como aplicar", M, y)
    y -= 9 * mm
    bullet_list(c, bullets, M, y, W - 2 * M)


def draw_nutrients(pdf):
    c = pdf.c
    pdf.new_page("Nutrientes essenciais para fortalecer a raiz", "De dentro para fora")
    y = H - 54 * mm
    draw_food_plate(c, M, y, W - 2 * M, 60 * mm)
    y -= 72 * mm
    nutrients = [
        ("Proteinas", "Base da estrutura do fio. Inclua ovos, peixe, frango, carnes magras, iogurte, leguminosas ou alternativas vegetais bem combinadas."),
        ("Ferro", "Ajuda no transporte de oxigenio. Boas fontes: carnes, feijoes, lentilha, espinafre e sementes. Combine vegetais com vitamina C."),
        ("Zinco", "Relacionado a reparo e crescimento. Fontes: sementes de abobora, castanhas, ovos, carnes e frutos do mar."),
        ("Biotina e complexo B", "Participam do metabolismo energetico. Fontes: ovos, aveia, leguminosas, cereais integrais e folhas."),
        ("Vitamina D", "Importante para equilibrio geral. Busque orientacao para exames e suplementacao quando necessario."),
        ("Omega 3", "Ajuda a modular processos inflamatorios. Fontes: sardinha, salmao, chia, linhaça e nozes."),
    ]
    for i, (name, desc) in enumerate(nutrients):
        x = M if i % 2 == 0 else W / 2 + 3 * mm
        yy = y - (i // 2) * 39 * mm
        card(c, x, yy, W / 2 - M - 4 * mm, 34 * mm, fill=colors.white, stroke=HexColor("#f0c2bd"))
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x + 6 * mm, yy - 9 * mm, name)
        paragraph(c, desc, x + 6 * mm, yy - 15 * mm, W / 2 - M - 16 * mm, 8.4, 3.9 * mm, color=MUTED)


def draw_routine(pdf):
    c = pdf.c
    pdf.new_page("Rotina de limpeza e massagem", "Couro cabeludo ativo")
    y = H - 54 * mm
    paragraph(c, "A rotina abaixo foi desenhada para ser simples. Ela nao depende de equipamentos caros e pode ser feita com as pontas dos dedos, respeitando a sensibilidade do couro cabeludo.", M, y, W - 2 * M, 11, 5.8 * mm)
    y -= 32 * mm
    sections = [
        ("No banho", ["Use agua morna ou fria, evitando temperatura muito quente.", "Massageie o couro cabeludo por 60 a 90 segundos com movimentos circulares.", "Enxague bem para nao deixar residuos de produto na raiz."]),
        ("Fora do banho", ["Com os dedos limpos, faca 3 minutos de massagem leve antes de dormir.", "Divida mentalmente a cabeca em frente, laterais, topo e nuca.", "A pressao deve ser confortavel. Dor e sinal de excesso."]),
        ("Depois", ["Evite prender o cabelo molhado.", "Seque sem friccionar com forca.", "Observe a queda sem contar fio por fio todos os dias, para nao gerar ansiedade."]),
    ]
    for title, bullets in sections:
        card(c, M, y, W - 2 * M, 50 * mm, fill=colors.white, stroke=HexColor("#f0c2bd"))
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(M + 8 * mm, y - 10 * mm, title)
        bullet_list(c, bullets, M + 8 * mm, y - 20 * mm, W - 2 * M - 16 * mm, 9.3, 1.5 * mm)
        y -= 57 * mm


def draw_habits(pdf):
    c = pdf.c
    pdf.new_page("Os 7 habitos que enfraquecem o cabelo", "Sabotadores silenciosos")
    y = H - 54 * mm
    habits = [
        ("1. Banho muito quente", "Resseca, aumenta sensibilidade e pode piorar oleosidade de rebote."),
        ("2. Prender com muita tracao", "Rabos apertados e coques tensionados podem fragilizar a linha frontal."),
        ("3. Dormir com cabelo molhado", "Aumenta atrito, quebra e desconforto no couro cabeludo."),
        ("4. Dieta com pouca proteina", "O fio precisa de materia-prima. Sem isso, a raiz fica sem suporte."),
        ("5. Excesso de quimica sem pausa", "Coloracoes, progressivas e descoloracoes exigem recuperacao entre processos."),
        ("6. Estresse constante sem descarga", "O corpo prioriza sobrevivencia. Sono e pausa tambem fazem parte do protocolo."),
        ("7. Trocar de produto toda semana", "Sem constancia nao ha leitura real do que esta funcionando.")
    ]
    for i, (title, desc) in enumerate(habits):
        h = 23 * mm
        card(c, M, y, W - 2 * M, h, fill=colors.white if i % 2 == 0 else HexColor("#fff4f1"), stroke=HexColor("#f0c2bd"))
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(M + 7 * mm, y - 8 * mm, title)
        paragraph(c, desc, M + 7 * mm, y - 14 * mm, W - 2 * M - 14 * mm, 8.7, 4.0 * mm, color=MUTED)
        y -= 26 * mm


def draw_recipes(pdf):
    c = pdf.c
    pdf.new_page("Bonus #1: receitas naturais caseiras", "Potencializadores")
    y = H - 54 * mm
    recipes = [
        ("Tonico suave de alecrim", "Ferva 250 ml de agua, desligue o fogo, adicione 1 colher de sopa de alecrim seco e abafe por 10 minutos. Use frio no couro cabeludo antes do banho, 2 vezes por semana. Suspenda se irritar."),
        ("Mascara de hidratacao simples", "Misture 1 colher de sopa de babosa pura com 1 colher de mascara capilar neutra. Aplique no comprimento, nao na raiz, por 10 minutos e enxague bem."),
        ("Pre-shampoo nutritivo", "Aplique algumas gotas de oleo vegetal leve no comprimento 20 minutos antes do banho. Evite excesso na raiz se houver oleosidade."),
        ("Agua aromatizada anti-descuido", "Deixe uma garrafa com agua, limao e hortela visivel. O objetivo e aumentar ingestao de agua sem depender de memoria.")
    ]
    for name, desc in recipes:
        card(c, M, y, W - 2 * M, 38 * mm, fill=colors.white, stroke=HexColor("#f0c2bd"))
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(M + 8 * mm, y - 10 * mm, name)
        paragraph(c, desc, M + 8 * mm, y - 17 * mm, W - 2 * M - 16 * mm, 9.2, 4.3 * mm, color=INK)
        y -= 43 * mm
    card(c, M, y, W - 2 * M, 22 * mm, fill=SOFT_GOLD, stroke=GOLD)
    paragraph(c, "Observacao: receitas naturais nao substituem tratamento quando ha queda intensa, alergias, dermatite, feridas ou falhas rapidas. Teste antes em pequena area.", M + 7 * mm, y - 8 * mm, W - 2 * M - 14 * mm, 8.8, 4.0 * mm)


def draw_food_guide(pdf):
    c = pdf.c
    pdf.new_page("Bonus #2: alimentos que fortalecem o cabelo", "Guia alimentar")
    y = H - 54 * mm
    groups = [
        ("Proteina em toda refeicao", ["Ovos", "Frango", "Peixe", "Iogurte natural", "Feijao com arroz", "Tofu"]),
        ("Minerais para raiz", ["Sementes de abobora", "Castanhas", "Lentilha", "Grao-de-bico", "Espinafre", "Carne magra"]),
        ("Vitaminas e antioxidantes", ["Frutas vermelhas", "Laranja", "Kiwi", "Cenoura", "Abacate", "Folhas verdes"]),
        ("Gorduras boas", ["Sardinha", "Salmao", "Azeite", "Chia", "Linhaça", "Nozes"]),
    ]
    for i, (title, foods) in enumerate(groups):
        x = M if i % 2 == 0 else W / 2 + 3 * mm
        yy = y - (i // 2) * 74 * mm
        card(c, x, yy, W / 2 - M - 4 * mm, 66 * mm, fill=colors.white, stroke=HexColor("#f0c2bd"))
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 6 * mm, yy - 10 * mm, title)
        yy2 = yy - 19 * mm
        for food in foods:
            c.setFillColor(SOFT_GREEN)
            c.roundRect(x + 6 * mm, yy2 - 6 * mm, W / 2 - M - 17 * mm, 8 * mm, 4 * mm, fill=1, stroke=0)
            c.setFillColor(GREEN)
            c.setFont("Helvetica-Bold", 8.2)
            c.drawString(x + 10 * mm, yy2 - 3.8 * mm, food)
            yy2 -= 8.2 * mm
    y -= 155 * mm
    section_label(c, "Modelo simples de prato", M, y)
    y -= 8 * mm
    bullet_list(c, [
        "1/2 prato de vegetais coloridos.",
        "1/4 prato de proteina.",
        "1/4 prato de carboidrato de qualidade.",
        "1 fonte pequena de gordura boa."
    ], M, y, W - 2 * M)


def draw_diagnosis_page(pdf, title, focus, bullets, avoid):
    c = pdf.c
    pdf.new_page(title, "Cuidado especifico do diagnostico")
    y = H - 54 * mm
    card(c, M, y, W - 2 * M, 34 * mm, fill=SOFT_RED, stroke=HexColor("#f0c2bd"))
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(M + 8 * mm, y - 10 * mm, "Foco principal")
    paragraph(c, focus, M + 8 * mm, y - 17 * mm, W - 2 * M - 16 * mm, 9.5, 4.3 * mm)
    y -= 48 * mm
    section_label(c, "Priorize", M, y)
    y -= 8 * mm
    y = bullet_list(c, bullets, M, y, W - 2 * M, 10)
    y -= 3 * mm
    card(c, M, y, W - 2 * M, 45 * mm, fill=SOFT_GOLD, stroke=GOLD)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(M + 8 * mm, y - 10 * mm, "Evite nesta fase")
    bullet_list(c, avoid, M + 8 * mm, y - 20 * mm, W - 2 * M - 16 * mm, 9.1, 1.2 * mm, bullet_color=GOLD)


def draw_checklist_pages(pdf):
    c = pdf.c
    for week, start in [("Semana 1 - Preparar", 1), ("Semana 2 - Fortalecer", 8), ("Semana 3 - Consolidar", 15)]:
        pdf.new_page(f"Plano de 21 dias: {week}", "Checklist diario")
        y = H - 53 * mm
        paragraph(c, "Marque cada item concluido. O objetivo nao e perfeicao, e consistencia. Se falhar um dia, retome no proximo sem abandonar o protocolo.", M, y, W - 2 * M, 10.5, 5.5 * mm)
        y -= 26 * mm
        for d in range(start, start + 7):
            card(c, M, y, W - 2 * M, 25 * mm, fill=colors.white, stroke=HexColor("#f0c2bd"))
            c.setFillColor(RED)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(M + 7 * mm, y - 10 * mm, f"Dia {d}")
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 8.5)
            c.drawString(M + 25 * mm, y - 9.5 * mm, "Limpeza  [  ]    Massagem  [  ]    Nutricao  [  ]    Agua  [  ]    Sono  [  ]")
            c.setStrokeColor(HexColor("#ead0cc"))
            c.line(M + 25 * mm, y - 18 * mm, W - M - 8 * mm, y - 18 * mm)
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 7.8)
            c.drawString(M + 25 * mm, y - 22 * mm, "Observacao do dia:")
            y -= 28 * mm


def draw_faq(pdf):
    c = pdf.c
    pdf.new_page("Perguntas frequentes", "Antes de comecar")
    y = H - 54 * mm
    faqs = [
        ("Em quanto tempo percebo diferenca?", "Muitas pessoas percebem melhora na sensacao de controle da rotina nos primeiros dias. Reducao visual de queda e fortalecimento variam conforme causa, constancia e historico."),
        ("Preciso comprar produtos caros?", "Nao. O protocolo prioriza rotina, massagem, nutricao e uso inteligente do que voce ja tem. Produtos podem ajudar, mas nao substituem consistencia."),
        ("Serve para homem e mulher?", "Sim. As orientacoes gerais servem para ambos, com adaptacoes por diagnostico."),
        ("Posso fazer se uso quimica?", "Sim, mas reduza agressao, evite calor excessivo e respeite pausas. Em caso de quebra severa, priorize recuperacao da fibra."),
        ("Quando devo procurar medico?", "Quando a queda e subita, intensa, com falhas, dor, feridas, coceira persistente ou quando ha suspeita hormonal, anemia, deficiencias ou efeito de medicamentos."),
    ]
    for q, a in faqs:
        card(c, M, y, W - 2 * M, 35 * mm, fill=colors.white, stroke=HexColor("#f0c2bd"))
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(M + 7 * mm, y - 9 * mm, q)
        paragraph(c, a, M + 7 * mm, y - 16 * mm, W - 2 * M - 14 * mm, 8.8, 4.1 * mm, color=MUTED)
        y -= 39 * mm


def draw_final(pdf):
    c = pdf.c
    pdf.new_page("Proximos passos", "Comece hoje")
    y = H - 58 * mm
    draw_calendar(c, M, y, W - 2 * M, 82 * mm)
    y -= 96 * mm
    paragraph(c, "A melhor rotina e aquela que voce consegue repetir. Comece hoje com a versao simples: banho com atencao na raiz, 3 minutos de massagem leve e uma refeicao com proteina.", M, y, W - 2 * M, 12, 6.4 * mm, font="Helvetica-Bold", color=INK)
    y -= 42 * mm
    card(c, M, y, W - 2 * M, 45 * mm, fill=RED, stroke=RED)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(W / 2, y - 15 * mm, "Seu cabelo precisa de constancia.")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, y - 25 * mm, "Volte ao checklist diariamente e acompanhe sua evolucao.")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(W / 2, y - 36 * mm, "Instituto Capilar")


def build():
    pdf = PDF(OUT)
    draw_cover(pdf)
    draw_intro(pdf)
    draw_summary(pdf)
    draw_three_steps(pdf)
    draw_step_page(pdf, 1, "Passo 1: limpeza inteligente", "A limpeza nao e apenas estetica. Ela prepara o couro cabeludo para receber a massagem, reduz acumulo de residuos e ajuda voce a observar melhor sinais de oleosidade, ressecamento ou sensibilidade.", [
        "Lave com agua morna ou fria, evitando agua muito quente.",
        "Aplique shampoo na raiz, nao no comprimento inteiro.",
        "Massageie com a ponta dos dedos por 60 a 90 segundos.",
        "Enxague ate sentir que nao ha residuos na raiz.",
        "Finalize sem esfregar a toalha com forca."
    ], "roots")
    draw_step_page(pdf, 2, "Passo 2: massagem de ativacao", "A massagem e o momento em que voce transforma cuidado em habito. Ela deve ser leve, constante e confortavel. Pressao exagerada nao acelera resultado.", [
        "Use as pontas dos dedos, nunca as unhas.",
        "Faca movimentos circulares pequenos por 3 minutos.",
        "Passe por frente, laterais, topo e nuca.",
        "Respire devagar durante a massagem para reduzir tensao.",
        "Repita diariamente, preferencialmente no mesmo horario."
    ], "roots")
    draw_step_page(pdf, 3, "Passo 3: nutricao e fortalecimento", "Fio forte depende de materia-prima. A raiz precisa de proteinas, minerais, vitaminas, agua e descanso. O protocolo funciona melhor quando o corpo tem base para sustentar novos fios.", [
        "Inclua proteina em pelo menos duas refeicoes ao dia.",
        "Use frutas ricas em vitamina C junto de fontes vegetais de ferro.",
        "Evite longos periodos sem comer se isso piora compulsao ou baixa energia.",
        "Beba agua ao longo do dia, nao tudo de uma vez.",
        "Priorize sono regular sempre que possivel."
    ], "food")
    draw_nutrients(pdf)
    draw_routine(pdf)
    draw_habits(pdf)
    draw_recipes(pdf)
    draw_food_guide(pdf)
    draw_diagnosis_page(pdf, "Efluvio telogeno detectado", "Reduzir gatilhos de estresse, recuperar rotina e dar suporte nutricional para que o ciclo do fio volte a se equilibrar.", [
        "Rotina leve e repetivel, sem adicionar pressao emocional.",
        "Sono e alimentacao como parte do tratamento.",
        "Massagem suave, sem friccao agressiva.",
        "Acompanhamento da queda por semana, nao por hora.",
        "Revisao de eventos recentes: parto, cirurgia, perda de peso, estresse ou mudanca hormonal."
    ], [
        "Contar fios obsessivamente todos os dias.",
        "Comecar varias solucoes ao mesmo tempo.",
        "Dietas restritivas sem acompanhamento."
    ])
    draw_diagnosis_page(pdf, "Queda androgenetica em progressao", "Estabilizar habitos que pioram afinamento e agir cedo para preservar densidade visual.", [
        "Fotografar entradas, linha frontal e topo a cada 15 dias.",
        "Evitar tracao e penteados muito apertados.",
        "Ser constante no protocolo e buscar avaliacao dermatologica.",
        "Priorizar proteina, ferro, zinco e sono.",
        "Acompanhar historico familiar sem entrar em panico."
    ], [
        "Ignorar afinamento por meses.",
        "Usar boné apertado por longos periodos com couro cabeludo abafado.",
        "Promessas milagrosas sem rotina."
    ])
    draw_diagnosis_page(pdf, "Dano quimico comprometendo a raiz", "Reduzir agressao, recuperar fibra e proteger o couro cabeludo para evitar quebra e queda difusa.", [
        "Dar pausa entre processos quimicos.",
        "Evitar calor excessivo e escovacao agressiva.",
        "Separar queda pela raiz de quebra no comprimento.",
        "Focar hidratacao e reconstrucao do comprimento.",
        "Manter limpeza suave na raiz."
    ], [
        "Descolorir ou alisar novamente em cabelo fragilizado.",
        "Prender molhado com forca.",
        "Confundir quebra com queda e tratar tudo do mesmo jeito."
    ])
    draw_diagnosis_page(pdf, "Queda acelerada em estado critico", "Criar resposta rapida de organizacao: reduzir agressao, melhorar suporte nutricional e procurar avaliacao se a queda estiver intensa.", [
        "Comecar o checklist hoje, sem esperar segunda-feira.",
        "Registrar intensidade semanalmente.",
        "Evitar quimica, calor e tracao por 21 dias.",
        "Priorizar refeicoes completas e hidratacao.",
        "Buscar profissional se houver falhas, dor, feridas ou queda muito intensa."
    ], [
        "Fazer procedimentos agressivos durante a fase critica.",
        "Pular refeicoes por ansiedade.",
        "Esperar meses sem investigar causas internas."
    ])
    draw_diagnosis_page(pdf, "Alerta de queda em evolucao", "Impedir que pequenos sinais virem um quadro maior. O foco e consistencia, prevencao e rotina simples.", [
        "Aplicar os 3 passos por 21 dias.",
        "Observar gatilhos: sono, estresse, alimentacao, quimica e tracao.",
        "Reduzir habitos sabotadores.",
        "Fortalecer a alimentacao antes de buscar solucoes complexas.",
        "Usar o checklist para criar clareza sobre evolucao."
    ], [
        "Achar que 'ainda e pouco' e nao agir.",
        "Trocar de produto toda semana.",
        "Ignorar piora progressiva."
    ])
    draw_checklist_pages(pdf)
    draw_faq(pdf)
    draw_final(pdf)
    pdf.save()
    return OUT


if __name__ == "__main__":
    out = build()
    print(out)
