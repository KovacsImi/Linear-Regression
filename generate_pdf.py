# -*- coding: utf-8 -*-
"""
PDF Generalo Script az Elemzesi Osszefoglalobol (analysis_summary.md -> analysis_summary.pdf)
Hasznalja az fpdf2 csomagot, teljes magyar ekezetes karaktertamogatassal (Arial TTF).
"""

import os
import sys
from fpdf import FPDF

class SummaryPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=18)
        
        # Betutipusok regisztralasa UTF-8 tamogatassal (Windows Fonts)
        font_dir = r"C:\Windows\Fonts"
        arial_reg = os.path.join(font_dir, "arial.ttf")
        arial_bold = os.path.join(font_dir, "arialbd.ttf")
        arial_italic = os.path.join(font_dir, "ariali.ttf")
        
        if os.path.exists(arial_reg):
            self.add_font("CustomFont", "", arial_reg)
            self.add_font("CustomFont", "B", arial_bold if os.path.exists(arial_bold) else arial_reg)
            self.add_font("CustomFont", "I", arial_italic if os.path.exists(arial_italic) else arial_reg)
            self.main_font = "CustomFont"
        else:
            self.main_font = "Helvetica"

    def header(self):
        if self.page_no() > 1:
            self.set_font(self.main_font, "I", 9)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "Egészségbiztosítási Költségek – OLS Lineáris Regresszió Összefoglaló", border=0, align="L")
            self.line(10, 18, 200, 18)
            self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.main_font, "I", 8)
        self.set_text_color(140, 140, 140)
        page_str = f"{self.page_no()} / {{nb}}"
        self.cell(0, 10, page_str, border=0, align="C")

    def chapter_title(self, title):
        self.set_font(self.main_font, "B", 13)
        self.set_text_color(26, 54, 93)  # Sotetkek
        self.cell(0, 8, title, border=0, align="L")
        self.ln(9)

    def section_title(self, title):
        self.set_font(self.main_font, "B", 10.5)
        self.set_text_color(43, 76, 126)
        self.cell(0, 6, title, border=0, align="L")
        self.ln(7)

    def body_text(self, text):
        self.set_font(self.main_font, "", 9.5)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def callout(self, title, text, bg_color=(235, 243, 250), border_color=(49, 130, 206)):
        self.set_fill_color(*bg_color)
        self.set_draw_color(*border_color)
        self.set_line_width(0.6)
        
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, 190, 16, style="FD")
        self.set_line_width(0.2)
        
        self.set_xy(x + 4, y + 2)
        self.set_font(self.main_font, "B", 9)
        self.set_text_color(*border_color)
        self.cell(0, 4, title)
        
        self.set_xy(x + 4, y + 7)
        self.set_font(self.main_font, "", 8.5)
        self.set_text_color(30, 30, 30)
        self.multi_cell(182, 4, text)
        self.set_y(y + 19)

    def draw_table(self, headers, rows, col_widths, align_cols=None):
        if align_cols is None:
            align_cols = ["L"] * len(headers)
        
        # Fejlec
        self.set_fill_color(230, 238, 248)
        self.set_draw_color(180, 195, 215)
        self.set_font(self.main_font, "B", 8.5)
        self.set_text_color(20, 40, 70)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 6, header, border=1, align="C", fill=True)
        self.ln()
        
        # Sorok
        self.set_font(self.main_font, "", 8.5)
        self.set_text_color(40, 40, 40)
        fill = False
        for row in rows:
            self.set_fill_color(248, 250, 252) if fill else self.set_fill_color(255, 255, 255)
            for i, val in enumerate(row):
                self.cell(col_widths[i], 5.5, str(val), border=1, align=align_cols[i], fill=True)
            self.ln()
            fill = not fill
        self.ln(3)


def generate_pdf():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    plots_dir = os.path.join(base_dir, "plots")
    pdf_path = os.path.join(base_dir, "analysis_summary.pdf")
    
    pdf = SummaryPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # --- Cimlap / Fo fejlec ---
    pdf.set_fill_color(26, 54, 93)
    pdf.rect(10, 10, 190, 24, style="F")
    pdf.set_xy(14, 13)
    pdf.set_font(pdf.main_font, "B", 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "Egészségbiztosítási Költségek – OLS Regresszió Összefoglaló")
    pdf.set_xy(14, 23)
    pdf.set_font(pdf.main_font, "", 9)
    pdf.set_text_color(210, 225, 245)
    pdf.cell(0, 6, "Adatforrás: Kaggle (mirichoi0218/insurance) | Teljes ökonometriai munkafolyamat")
    pdf.set_y(38)
    
    # 1. Adatbazis es EDA
    pdf.chapter_title("1. Adatbázis beolvasás és leíró statisztika (EDA)")
    pdf.body_text(
        "• 1338 megfigyelés, 7 változó (age, sex, bmi, children, smoker, region, charges).\n"
        "• 1 duplikált sor kiszűrésre került -> 1337 tiszta megfigyelés, hiányzó érték nincs.\n"
        "• Célváltozó: charges (jobbra ferde eloszlás, medián: ~9382 USD, átlag: ~13279 USD)."
    )
    
    # Abra beillesztes: Charges es Smoker
    p_charges = os.path.join(plots_dir, "04_dist_charges.png")
    p_smoker = os.path.join(plots_dir, "06_count_smoker.png")
    if os.path.exists(p_charges) and os.path.exists(p_smoker):
        y_img = pdf.get_y()
        pdf.image(p_charges, x=12, y=y_img, w=90)
        pdf.image(p_smoker, x=106, y=y_img, w=90)
        pdf.set_y(y_img + 62)
    
    # 2. Spearman korrelacio es Multikollinearitas (VIF)
    pdf.chapter_title("2. Korreláció (Spearman) és Multikollinearitás (VIF)")
    pdf.body_text(
        "• One-Hot Encoding (drop_first=True) után 8 magyarázó változó maradt.\n"
        "• Legerősebb kapcsolatok a költségekkel (charges):\n"
        "   - smoker_yes: rho = 0.66 (kiemelkedően magas)\n"
        "   - age: rho = 0.53, bmi: rho = 0.12\n"
        "• Multikollinearitás teszt (VIF): Minden változó VIF értéke < 5.0 (legmagasabb: region_southeast = 1.65), "
        "így nem áll fenn káros multikollinearitás."
    )
    
    p_heat = os.path.join(plots_dir, "08_spearman_heatmap.png")
    if os.path.exists(p_heat):
        y_h = pdf.get_y()
        pdf.image(p_heat, x=25, y=y_h, w=150)
        pdf.set_y(y_h + 82)
    
    # Uj oldal a modellezesnek es diagnosztikanak
    pdf.add_page()
    
    # 3. Modellezes es Backward Elimination
    pdf.chapter_title("3. OLS Modellezés és Visszalépéses Elimináció (Backward Elimination)")
    pdf.body_text(
        "A regressziós modellt fokozatosan egyszerűsítettük 5%-os szignifikanciaszint (alpha = 0.05) alapján."
    )
    
    step_headers = ["Lépés", "Eltávolított változó", "p-érték", "Adj. R-squared"]
    step_rows = [
        ["#1", "sex_male", "0.6976", "0.7494"],
        ["#2", "region_northwest", "0.4652", "0.7495"],
        ["#3", "region_southwest", "0.0582", "0.7490"],
        ["#4", "region_southeast", "0.1356", "0.7488"]
    ]
    pdf.draw_table(step_headers, step_rows, [20, 70, 45, 50], ["C", "L", "C", "C"])
    
    pdf.callout(
        "VÉGSŐ MAGYARÁZÓ VÁLTOZÓK",
        "age (életkor) + bmi (testtömegindex) + children (gyermekek száma) + smoker_yes (dohányzás)"
    )
    
    # 4. Modell-osszehasonlitas
    pdf.chapter_title("4. Modell-összehasonlítás (Alapmodell vs. Végső modell)")
    comp_headers = ["Metrika", "Teljes modell (8 változó)", "Végső modell (4 változó)", "Változás / Értékelés"]
    comp_rows = [
        ["R-squared", "0.7507", "0.7495", "-0.12% (minimális eltérés)"],
        ["Adj. R-squared", "0.7492", "0.7488", "-0.04% (gyakorlatilag azonos)"],
        ["F-statisztika", "500.0", "996.5", "Jelentős javulás (+99.3%)"],
        ["AIC", "27094.2", "27092.8", "Alacsonyabb (parszimóniásabb)"],
        ["RMSE", "6043.85 USD", "6058.64 USD", "+14.79 USD eltérés"]
    ]
    pdf.draw_table(comp_headers, comp_rows, [35, 50, 50, 50], ["L", "C", "C", "L"])
    
    # 5. OLS Diagnosztika
    pdf.chapter_title("5. Ökonometriai és Diagnosztikai Vizsgálatok")
    diag_headers = ["Diagnosztikai teszt", "Statisztika / p-érték", "Eredmény", "Ökonometriai következtetés"]
    diag_rows = [
        ["Shapiro-Wilk teszt", "p = 0.0000", "Elvetve (p < 0.05)", "A reziduálisok nem normálisak"],
        ["Jarque-Bera teszt", "p = 0.0000", "Elvetve (p < 0.05)", "Ferde / csúcsos hiba-eloszlás"],
        ["Breusch-Pagan teszt", "LM p = 0.0000", "Heteroszkedasztikus", "Nem állandó hibavariancia"],
        ["Durbin-Watson teszt", "DW = 2.088", "Feltétel teljesül (~2.0)", "Nincs autokorreláció"],
        ["Cook-féle távolság", "112 pont > 4/n (8.4%)", "Befolyásos pontok", "Kiemelkedő költségű esetek"]
    ]
    pdf.draw_table(diag_headers, diag_rows, [45, 45, 45, 50], ["L", "C", "C", "L"])
    
    # Uj oldal a diagnosztikai abrakhoz es konkluziohoz
    pdf.add_page()
    
    pdf.chapter_title("6. Reziduális Diagnosztikai Ábrák")
    p_norm = os.path.join(plots_dir, "09_normality_check.png")
    p_fit = os.path.join(plots_dir, "10_residuals_vs_fitted.png")
    p_cook = os.path.join(plots_dir, "11_cooks_distance.png")
    
    y_d = pdf.get_y()
    if os.path.exists(p_norm) and os.path.exists(p_fit):
        pdf.image(p_norm, x=12, y=y_d, w=88)
        pdf.image(p_fit, x=106, y=y_d, w=88)
        pdf.set_y(y_d + 58)
        
    y_c = pdf.get_y()
    if os.path.exists(p_cook):
        pdf.image(p_cook, x=35, y=y_c, w=135)
        pdf.set_y(y_c + 66)
    
    # 7. Zaro megallapitasok es HC3 robusztus becsles
    pdf.chapter_title("7. Összegzés és Robusztus Becslés (HC3)")
    pdf.callout(
        "FIGYELEM: HETEROSZKEDASZTICITÁS KEZELÉSE",
        "Mivel a Breusch-Pagan teszt heteroszkedaszticitást mutatott, az elemzés automatikusan kiszámította "
        "a HC3 robusztus standard hibákat is (White-féle korrekció). A dohányzás, életkor, BMI és gyermekek "
        "száma a megnövelt standard hibák mellett is erősen szignifikáns maradt (p < 0.001).",
        bg_color=(254, 243, 199),
        border_color=(217, 119, 6)
    )
    
    pdf.ln(2)
    pdf.body_text(
        "Végső egyenlet:\n"
        "  charges = -12102.77 + 257.85 * age + 322.10 * bmi + 475.50 * children + 23811.41 * smoker_yes\n\n"
        "Legfőbb megállapítás:\n"
        "A dohányzás a legmeghatározóbb tényező: egyéb változók azonossága mellett átlagosan közel +23 811 USD "
        "többletköltséget okoz az ellátásban."
    )
    
    pdf.output(pdf_path)
    print(f"PDF sikeresen generalva: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
