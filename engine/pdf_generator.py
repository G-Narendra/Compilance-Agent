from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        # Top color accent bar
        self.set_fill_color(63, 43, 150) # Dark Indigo/Violet matching app style (#3f2b96)
        self.rect(0, 0, 210, 6, 'F')
        
        self.set_y(15)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(30, 41, 59) # Slate 800 (#1e293b)
        self.cell(0, 10, 'Compliance Audit Report', border=0, ln=1, align='L')
        
        # Sub-header line
        self.set_draw_color(226, 232, 240) # Slate 200 (#e2e8f0)
        self.set_line_width(0.5)
        self.line(15, 27, 195, 27)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(148, 163, 184) # Slate 400
        
        # Draw top line for footer
        self.set_draw_color(241, 245, 249) # Slate 100
        self.line(15, 282, 195, 282)
        
        # Page numbers and info
        self.cell(0, 10, f'Page {self.page_no()}', align='R')

def clean_text(text: str) -> str:
    # Replace common unicode chars that break fpdf2 helvetica
    replacements = {
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u00a0': ' ',
        '\u2022': '-', '\u00ad': '-'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

def add_detail_row(pdf, label: str, value: str, is_italic: bool = False):
    if not value or str(value).strip().lower() in ["none", "n/a", ""]:
        return # Skip empty or N/A fields to keep it compact and clean
        
    pdf.set_font("helvetica", 'B', 9)
    pdf.set_text_color(100, 116, 139) # Slate 500 for label
    
    # Print label
    pdf.cell(32, 5, label)
    
    # Save old left margin and set new one to indent the value
    old_l_margin = pdf.l_margin
    pdf.l_margin = 54
    pdf.set_x(54)
    
    # Print value
    pdf.set_font("helvetica", 'I' if is_italic else '', 9)
    pdf.set_text_color(30, 41, 59) # Slate 800
    pdf.multi_cell(141, 5, clean_text(str(value)))
    
    # Restore margin
    pdf.l_margin = old_l_margin
    pdf.ln(1)

def generate_audit_pdf(report: dict, target_filename: str) -> bytes:
    pdf = PDFReport()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Executive Summary
    pdf.set_font("helvetica", 'B', 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, "1. Executive Summary", ln=1)
    pdf.ln(2)
    
    score = report.get("score", 0)
    status = report.get("status", "Unknown").upper()
    
    start_y = pdf.get_y()
    pdf.ln(4)
    
    # Target Document
    pdf.set_x(20)
    pdf.set_font("helvetica", 'B', 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(45, 6, "Target Document:")
    pdf.set_font("helvetica", '', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, clean_text(target_filename), ln=1)
    
    # Timestamp
    pdf.set_x(20)
    pdf.set_font("helvetica", 'B', 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(45, 6, "Audit Date/Time:")
    pdf.set_font("helvetica", '', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ln=1)
    
    # Score
    pdf.set_x(20)
    pdf.set_font("helvetica", 'B', 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(45, 6, "Compliance Score:")
    pdf.set_font("helvetica", 'B', 10)
    score_color = (34, 197, 94) if score > 80 else (239, 68, 68)
    pdf.set_text_color(*score_color)
    pdf.cell(0, 6, f"{score}/100", ln=1)
    
    # Status
    pdf.set_x(20)
    pdf.set_font("helvetica", 'B', 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(45, 6, "Compliance Status:")
    pdf.set_font("helvetica", 'B', 10)
    status_color = (34, 197, 94) if status == "PASS" else (234, 179, 8) if status == "PARTIAL" else (239, 68, 68)
    pdf.set_text_color(*status_color)
    pdf.cell(0, 6, status, ln=1)
    
    # Summary description
    pdf.set_x(20)
    pdf.set_font("helvetica", 'B', 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(45, 6, "Key Summary:")
    
    # Save margin and set new margin for multi-cell
    old_l_margin = pdf.l_margin
    pdf.l_margin = 65
    pdf.set_x(65)
    pdf.set_font("helvetica", '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(130, 6, clean_text(report.get('summary', '')))
    pdf.l_margin = old_l_margin
    
    pdf.ln(4)
    end_y = pdf.get_y()
    
    # Draw card border around the summary
    pdf.set_draw_color(226, 232, 240) # Slate 200
    pdf.set_line_width(0.5)
    pdf.rect(15, start_y, 180, end_y - start_y, 'D')
    
    pdf.ln(8)
    
    # Detailed Findings
    findings = report.get("findings", [])
    pdf.set_font("helvetica", 'B', 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, "2. Detailed Findings", ln=1)
    pdf.ln(2)
    
    if not findings:
        pdf.set_font("helvetica", 'I', 11)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 10, "No violations found.", ln=1)
        return bytes(pdf.output())
        
    for idx, f in enumerate(findings, 1):
        sev = str(f.get("severity", "INFO")).upper()
        
        # Colors based on severity
        if sev == "CRITICAL":
            sev_color = (220, 38, 38) # Red
        elif sev == "HIGH":
            sev_color = (234, 88, 12) # Orange
        elif sev == "MEDIUM":
            sev_color = (202, 138, 4) # Yellow
        else:
            sev_color = (37, 99, 235) # Blue/Info
            
        title = f"[{sev}] {idx}. {clean_text(f.get('title', 'Untitled'))}"
        
        # Check remaining space before starting a finding
        rem_h = pdf.h - pdf.b_margin - pdf.get_y()
        if rem_h < 55: # If less than 55mm remaining, push finding to next page
            pdf.add_page()
            
        start_page = pdf.page_no()
        start_y = pdf.get_y()
        
        # Indent finding content
        pdf.l_margin = 22
        pdf.set_x(22)
        
        # Title
        pdf.set_font("helvetica", 'B', 11)
        pdf.set_text_color(*sev_color)
        pdf.multi_cell(173, 6, title)
        pdf.ln(2)
        
        # Details
        add_detail_row(pdf, "Rule ID:", f.get("rule_id", "N/A"))
        add_detail_row(pdf, "Description:", f.get("description", "N/A"))
        add_detail_row(pdf, "Evidence:", f.get("evidence", "N/A"), is_italic=True)
        add_detail_row(pdf, "Rule Citation:", f.get("rulebook_citation", "N/A"), is_italic=True)
        add_detail_row(pdf, "Recommendation:", f.get("recommendation", "N/A"))
        
        end_y = pdf.get_y()
        
        # Draw left accent line only if finding did not wrap across pages
        if pdf.page_no() == start_page:
            pdf.set_draw_color(*sev_color)
            pdf.set_line_width(1.5)
            pdf.line(17, start_y + 1, 17, end_y - 2)
        
        # Draw finding card bottom divider
        pdf.set_draw_color(241, 245, 249) # Slate 100
        pdf.set_line_width(0.5)
        pdf.line(22, end_y + 2, 195, end_y + 2)
        
        # Restore left margin
        pdf.l_margin = 15
        pdf.set_x(15)
        pdf.ln(8)
        
    return bytes(pdf.output())
