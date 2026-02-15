from fpdf import FPDF


class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'ProjectSprint Weekly Report', 0, 1, 'C')
        self.ln(10)


def generate_weekly_pdf(week_num: int, done_tasks: list, blockers: str, plans: str):
    pdf = PDFReport()
    pdf.add_page()

    # ВАЖНО: FPDF по умолчанию не поддерживает кириллицу.
    # Для MVP используем транслит или латиницу.
    # В продакшене нужно подключить шрифт: pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, text=f"Week Number: {week_num}", ln=1)

    # Section 1: Done
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, text="1. Completed Tasks:", ln=1)
    pdf.set_font("Arial", size=12)

    if not done_tasks:
        pdf.cell(0, 10, text="- No tasks completed", ln=1)
    else:
        for task in done_tasks:
            assignee = task.assignee.username if task.assignee else "Unassigned"
            # Очистка текста от символов, ломающих FPDF
            clean_title = task.title.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 10, text=f"[*] {clean_title} (by {assignee})", ln=1)

    pdf.ln(5)

    # Section 2: Blockers
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, text="2. Blockers / Issues:", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text=blockers.encode('latin-1', 'replace').decode('latin-1'))

    pdf.ln(5)

    # Section 3: Plans
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, text="3. Plans for next week:", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text=plans.encode('latin-1', 'replace').decode('latin-1'))

    filename = f"report_week_{week_num}.pdf"
    pdf.output(filename)
    return filename