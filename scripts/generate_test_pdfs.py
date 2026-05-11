#!/usr/bin/env python3
"""Generate synthetic legal PDF documents for the Vandermeer & Associates demo."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, PageBreak, HRFlowable, Table, TableStyle,
)

W, H = A4
MARGIN  = 2.5 * cm
FOOT_H  = 1.4 * cm

DARK  = colors.HexColor("#1a1a2e")
MID   = colors.HexColor("#4a4a6a")
LIGHT = colors.HexColor("#9898b8")
GOLD  = colors.HexColor("#c8a96e")
RULE  = colors.HexColor("#d4d4e0")

OUT = os.path.join(os.path.dirname(__file__), "..", "test-data")
os.makedirs(OUT, exist_ok=True)

def out(name):
    return os.path.join(OUT, name)


# ── Styles ───────────────────────────────────────────────────────────────────

def S():
    s = {}
    s["title"]    = ParagraphStyle("title",    fontName="Times-Bold",   fontSize=15,   leading=21, textColor=DARK, alignment=TA_CENTER,  spaceAfter=4)
    s["subtitle"] = ParagraphStyle("subtitle", fontName="Times-Roman",  fontSize=10.5, leading=16, textColor=MID,  alignment=TA_CENTER,  spaceAfter=3)
    s["ref"]      = ParagraphStyle("ref",      fontName="Times-Roman",  fontSize=9,    leading=13, textColor=LIGHT,alignment=TA_CENTER,  spaceAfter=2)
    s["parties"]  = ParagraphStyle("parties",  fontName="Times-Roman",  fontSize=10.5, leading=17, textColor=DARK, alignment=TA_JUSTIFY, spaceBefore=6, spaceAfter=4)
    s["recital"]  = ParagraphStyle("recital",  fontName="Times-Roman",  fontSize=10.5, leading=16, textColor=DARK, alignment=TA_JUSTIFY, leftIndent=0.6*cm, spaceAfter=4)
    s["h1"]       = ParagraphStyle("h1",       fontName="Times-Bold",   fontSize=11.5, leading=17, textColor=DARK, spaceBefore=14, spaceAfter=4,  keepWithNext=1)
    s["h2"]       = ParagraphStyle("h2",       fontName="Times-Bold",   fontSize=10.5, leading=15, textColor=DARK, spaceBefore=8,  spaceAfter=3,  keepWithNext=1)
    s["body"]     = ParagraphStyle("body",     fontName="Times-Roman",  fontSize=10.5, leading=16, textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=5)
    s["clause"]   = ParagraphStyle("clause",   fontName="Times-Roman",  fontSize=10.5, leading=16, textColor=DARK, alignment=TA_JUSTIFY, leftIndent=0.5*cm, firstLineIndent=-0.5*cm, spaceAfter=5)
    s["sub"]      = ParagraphStyle("sub",      fontName="Times-Roman",  fontSize=10.5, leading=16, textColor=DARK, alignment=TA_JUSTIFY, leftIndent=1.4*cm, firstLineIndent=-0.6*cm, spaceAfter=4)
    s["bold"]     = ParagraphStyle("bold",     fontName="Times-Bold",   fontSize=10.5, leading=16, textColor=DARK, spaceAfter=4)
    s["center"]   = ParagraphStyle("center",   fontName="Times-Roman",  fontSize=10.5, leading=16, textColor=DARK, alignment=TA_CENTER,  spaceAfter=4)
    s["small"]    = ParagraphStyle("small",    fontName="Times-Roman",  fontSize=9,    leading=13, textColor=MID,  spaceAfter=3)
    s["sig"]      = ParagraphStyle("sig",      fontName="Times-Roman",  fontSize=9.5,  leading=14, textColor=MID)
    return s


# ── Page template ─────────────────────────────────────────────────────────────

def make_doc(filename, footer_title, doc_ref):
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(1.5)
        canvas.line(MARGIN, H - MARGIN + 0.35*cm, W - MARGIN, H - MARGIN + 0.35*cm)
        canvas.setFont("Times-Bold", 8)
        canvas.setFillColor(MID)
        canvas.drawString(MARGIN, H - MARGIN + 0.65*cm, "VANDERMEER & ASSOCIATES")
        canvas.setFont("Times-Roman", 8)
        canvas.drawRightString(W - MARGIN, H - MARGIN + 0.65*cm, doc_ref)
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, FOOT_H + 0.2*cm, W - MARGIN, FOOT_H + 0.2*cm)
        canvas.setFont("Times-Roman", 7.5)
        canvas.setFillColor(LIGHT)
        canvas.drawString(MARGIN, FOOT_H - 0.15*cm, footer_title[:80])
        canvas.drawCentredString(W / 2, FOOT_H - 0.15*cm, "CONFIDENTIAL")
        canvas.drawRightString(W - MARGIN, FOOT_H - 0.15*cm, f"Page {doc.page}")
        canvas.restoreState()

    doc = BaseDocTemplate(
        filename, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN + 1.3*cm, bottomMargin=MARGIN + 0.2*cm,
    )
    frame = Frame(MARGIN, MARGIN + 0.2*cm, W - 2*MARGIN, H - 2*MARGIN - 1.5*cm, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])
    return doc


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=RULE, spaceBefore=6, spaceAfter=6)

def sp(h=6):
    return Spacer(1, h)

def sig_table(st, left, right):
    def col(party):
        return [
            Paragraph(party, st["sig"]),
            Spacer(1, 20),
            Paragraph("____________________________", st["sig"]),
            Paragraph("Authorised Signatory", st["sig"]),
            Spacer(1, 5),
            Paragraph("Name: ___________________", st["sig"]),
            Paragraph("Title:  ___________________", st["sig"]),
            Paragraph("Date:  ___________________", st["sig"]),
        ]
    t = Table([[col(left), col(right)]], colWidths=[(W - 2*MARGIN) * 0.48] * 2)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t

def loss_table(data):
    t = Table(data, colWidths=[6.5*cm, 6*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f8")),
        ("FONTNAME",   (0, 0), (-1, 0), "Times-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9.5),
        ("LEADING",    (0, 0), (-1, -1), 14),
        ("GRID",       (0, 0), (-1, -1), 0.5, RULE),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t

def action_table(data):
    t = Table(data, colWidths=[0.8*cm, 5*cm, 5.8*cm, 3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f8")),
        ("FONTNAME",   (0, 0), (-1, 0), "Times-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9.5),
        ("LEADING",    (0, 0), (-1, -1), 14),
        ("GRID",       (0, 0), (-1, -1), 0.5, RULE),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


# ═══════════════════════════════════════════════════════════════════════════════
# Document 1 — Accenture Supply Agreement
# ═══════════════════════════════════════════════════════════════════════════════

def doc_accenture_supply():
    st = S()
    doc = make_doc(out("accenture-supply-agreement.pdf"),
                   "Accenture BV - Master Supply Agreement",
                   "Ref: VA/2024/MSA/0047")
    story = []

    story += [sp(4),
        Paragraph("MASTER SUPPLY AGREEMENT", st["title"]),
        Paragraph("Accenture BV and Meridian Data Solutions NV", st["subtitle"]),
        Paragraph("Agreement Reference: VA/2024/MSA/0047 &nbsp;|&nbsp; Date: 1 March 2024", st["ref"]),
        hr()]

    story += [
        Paragraph("""<b>THIS MASTER SUPPLY AGREEMENT</b> (the <b>&#8220;Agreement&#8221;</b>) is entered
            into as of 1 March 2024 (the <b>&#8220;Effective Date&#8221;</b>) by and between:""", st["body"]),
        Paragraph("""<b>Accenture BV</b>, a private limited liability company incorporated under the laws
            of the Netherlands, registered at the Dutch Chamber of Commerce under number 34117484, having
            its registered office at Gustav Mahlerplein 90, 1082 MA Amsterdam
            (<b>&#8220;Accenture&#8221;</b> or <b>&#8220;Buyer&#8221;</b>);""", st["parties"]),
        Paragraph("<b>and</b>", st["center"]),
        Paragraph("""<b>Meridian Data Solutions NV</b>, a public limited liability company incorporated
            under the laws of Belgium (CBE: 0689.221.574), having its registered office at
            Rue de la Loi 99, 1040 Brussels, Belgium (<b>&#8220;Supplier&#8221;</b>).""", st["parties"]),
        Paragraph("""Accenture and Supplier are referred to individually as a <b>&#8220;Party&#8221;</b>
            and collectively as the <b>&#8220;Parties&#8221;</b>.""", st["body"]),
        hr()]

    story += [
        Paragraph("RECITALS", st["h1"]),
        Paragraph("""(A)&nbsp;&nbsp;Accenture wishes to procure certain information technology and data
            analytics services from Supplier on the terms set out in this Agreement.""", st["recital"]),
        Paragraph("""(B)&nbsp;&nbsp;Supplier has the expertise, capacity and willingness to provide such
            services on the terms set out herein.""", st["recital"]),
        Paragraph("""(C)&nbsp;&nbsp;The Parties wish to record the terms upon which such services shall
            be provided.""", st["recital"]),
        Paragraph("""NOW, THEREFORE, in consideration of the mutual covenants contained herein,
            the Parties agree as follows:""", st["body"]),
        hr()]

    story += [
        Paragraph("1.&nbsp;&nbsp;DEFINITIONS AND INTERPRETATION", st["h1"]),
        Paragraph("""1.1&nbsp;&nbsp;In this Agreement, the following terms shall have the meanings
            ascribed to them below:""", st["clause"]),
        Paragraph("""1.1.1&nbsp;&nbsp;<b>&#8220;Deliverables&#8221;</b> means all work product, reports,
            software, data outputs and other materials to be produced by Supplier pursuant to a
            Statement of Work.""", st["sub"]),
        Paragraph("""1.1.2&nbsp;&nbsp;<b>&#8220;Fees&#8221;</b> means the amounts payable by Accenture
            to Supplier as specified in the applicable Statement of Work.""", st["sub"]),
        Paragraph("""1.1.3&nbsp;&nbsp;<b>&#8220;Intellectual Property Rights&#8221;</b> means all
            patents, copyright, database rights, trade marks, design rights, trade secrets, know-how
            and all other intellectual and industrial property rights.""", st["sub"]),
        Paragraph("""1.1.4&nbsp;&nbsp;<b>&#8220;Statement of Work&#8221;</b> or <b>&#8220;SOW&#8221;</b>
            means a document executed by both Parties referencing this Agreement and specifying the
            services, Deliverables, timelines and Fees.""", st["sub"])]

    story += [
        Paragraph("2.&nbsp;&nbsp;SUPPLY OF SERVICES", st["h1"]),
        Paragraph("""2.1&nbsp;&nbsp;Subject to the terms of this Agreement, Supplier shall provide the
            services and Deliverables as specified in each SOW executed by the Parties from time
            to time.""", st["clause"]),
        Paragraph("""2.2&nbsp;&nbsp;Supplier shall perform all services with reasonable skill, care and
            diligence, in accordance with industry best practices and applicable law.""", st["clause"]),
        Paragraph("""2.3&nbsp;&nbsp;Supplier shall assign suitably qualified and experienced personnel.
            Supplier shall promptly replace any personnel upon Accenture's reasonable written
            request.""", st["clause"]),
        Paragraph("""2.4&nbsp;&nbsp;Supplier shall not subcontract any material part of the services
            without Accenture's prior written consent, not to be unreasonably withheld.""", st["clause"])]

    story += [
        Paragraph("3.&nbsp;&nbsp;FEES AND PAYMENT", st["h1"]),
        Paragraph("""3.1&nbsp;&nbsp;In consideration of the supply of services, Accenture shall pay
            the Fees in accordance with the relevant SOW.""", st["clause"]),
        Paragraph("""3.2&nbsp;&nbsp;Supplier shall issue valid VAT invoices within five (5) Business
            Days following the end of each calendar month. Payment shall be due within forty-five (45)
            days of receipt of a correctly rendered invoice.""", st["clause"]),
        Paragraph("""3.3&nbsp;&nbsp;All Fees are exclusive of VAT, which shall be applied at the
            applicable statutory rate.""", st["clause"]),
        Paragraph("""3.4&nbsp;&nbsp;In the event of a disputed invoice, Accenture shall notify Supplier
            in writing within fifteen (15) Business Days of receipt, specifying the grounds for dispute.
            The Parties shall resolve any dispute in good faith within thirty (30) days.""", st["clause"])]

    story.append(PageBreak())

    story += [
        Paragraph("4.&nbsp;&nbsp;LIABILITY AND INDEMNIFICATION", st["h1"]),
        Paragraph("""4.1&nbsp;&nbsp;<b>Mutual Cap on Liability.</b> Subject to Clause 4.3, the aggregate
            liability of either Party to the other under or in connection with this Agreement, whether
            arising in contract, tort (including negligence) or otherwise, shall not exceed
            <b>EUR 500,000 (five hundred thousand euros)</b> per Agreement Year.""", st["clause"]),
        Paragraph("""4.2&nbsp;&nbsp;<b>Exclusion of Consequential Loss.</b> Neither Party shall be
            liable to the other for any indirect, special, incidental or consequential loss or damage,
            loss of profit, loss of revenue, loss of business or loss of anticipated savings, even if
            advised of the possibility of such loss.""", st["clause"]),
        Paragraph("""4.3&nbsp;&nbsp;<b>Unlimited Liability.</b> Nothing in this Agreement shall limit
            or exclude the liability of either Party for:""", st["clause"]),
        Paragraph("(a)&nbsp;&nbsp;death or personal injury caused by its negligence;", st["sub"]),
        Paragraph("(b)&nbsp;&nbsp;fraud or fraudulent misrepresentation; or", st["sub"]),
        Paragraph("(c)&nbsp;&nbsp;any other liability which cannot be lawfully excluded.", st["sub"]),
        Paragraph("""4.4&nbsp;&nbsp;Supplier shall indemnify and hold harmless Accenture against
            any third-party claims arising from Supplier's wilful misconduct or gross negligence in
            the performance of the services.""", st["clause"])]

    story += [
        Paragraph("5.&nbsp;&nbsp;TERM, RENEWAL AND TERMINATION", st["h1"]),
        Paragraph("""5.1&nbsp;&nbsp;<b>Initial Term.</b> This Agreement shall commence on the Effective
            Date and continue for an initial period of two (2) years (the
            <b>&#8220;Initial Term&#8221;</b>), unless earlier terminated in accordance with this
            Clause 5.""", st["clause"]),
        Paragraph("""5.2&nbsp;&nbsp;<b>Automatic Renewal.</b> Upon expiry of the Initial Term, and upon
            expiry of each subsequent Renewal Term, this Agreement shall automatically renew for
            successive periods of one (1) year (<b>&#8220;Renewal Term&#8221;</b>), unless either Party
            serves written notice of non-renewal not less than <b>ninety (90) calendar days</b> prior
            to the expiry of the then-current term.""", st["clause"]),
        Paragraph("""5.3&nbsp;&nbsp;<b>Termination for Cause.</b> Either Party may terminate this
            Agreement with immediate effect by written notice if:""", st["clause"]),
        Paragraph("""(a)&nbsp;&nbsp;the other Party commits a material breach and fails to remedy it
            within thirty (30) days of written notice specifying the breach;""", st["sub"]),
        Paragraph("""(b)&nbsp;&nbsp;the other Party becomes insolvent, is subject to administration,
            receivership, bankruptcy or any analogous procedure; or""", st["sub"]),
        Paragraph("(c)&nbsp;&nbsp;the other Party ceases or threatens to cease to carry on business.", st["sub"]),
        Paragraph("""5.4&nbsp;&nbsp;<b>Termination for Convenience.</b> Either Party may terminate this
            Agreement for convenience upon not less than one hundred and eighty (180) days' written
            notice.""", st["clause"]),
        Paragraph("""5.5&nbsp;&nbsp;<b>Consequences of Termination.</b> Upon termination or expiry:
            (i) all outstanding SOWs shall terminate unless otherwise agreed in writing; (ii) each Party
            shall promptly return or securely destroy the other's confidential information; (iii) accrued
            payment obligations shall survive.""", st["clause"])]

    story.append(PageBreak())

    story += [
        Paragraph("6.&nbsp;&nbsp;CONFIDENTIALITY", st["h1"]),
        Paragraph("""6.1&nbsp;&nbsp;Each Party undertakes to maintain strict confidentiality of the
            other Party's Confidential Information and not to disclose it to any third party without
            prior written consent, except as required by applicable law.""", st["clause"]),
        Paragraph("""6.2&nbsp;&nbsp;Confidentiality obligations under this Clause 6 shall survive
            termination or expiry of this Agreement for five (5) years.""", st["clause"])]

    story += [
        Paragraph("7.&nbsp;&nbsp;GENERAL PROVISIONS", st["h1"]),
        Paragraph("""7.1&nbsp;&nbsp;<b>Governing Law.</b> This Agreement shall be governed by the laws
            of the Netherlands.""", st["clause"]),
        Paragraph("""7.2&nbsp;&nbsp;<b>Dispute Resolution.</b> Disputes shall first be referred to senior
            management. If not resolved within thirty (30) days, either Party may refer the dispute to
            the exclusive jurisdiction of the courts of Amsterdam.""", st["clause"]),
        Paragraph("""7.3&nbsp;&nbsp;<b>Entire Agreement.</b> This Agreement constitutes the entire
            agreement between the Parties and supersedes all prior negotiations and representations.""",
            st["clause"]),
        Paragraph("""7.4&nbsp;&nbsp;<b>Amendments.</b> No amendment shall be binding unless made in
            writing and signed by authorised representatives of both Parties.""", st["clause"]),
        Paragraph("""7.5&nbsp;&nbsp;<b>Force Majeure.</b> Neither Party shall be liable for any failure
            or delay due to circumstances beyond its reasonable control.""", st["clause"]),
        sp(12),
        Paragraph("""IN WITNESS WHEREOF, the Parties have executed this Agreement as of the date
            first written above.""", st["body"]),
        sp(16),
        sig_table(st,
            "<b>For and on behalf of ACCENTURE BV</b>",
            "<b>For and on behalf of MERIDIAN DATA SOLUTIONS NV</b>")]

    doc.build(story)
    print("  ✓  accenture-supply-agreement.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
# Document 2 — Senior Associate Employment Contract
# ═══════════════════════════════════════════════════════════════════════════════

def doc_employment():
    st = S()
    doc = make_doc(out("senior-associate-employment.pdf"),
                   "Senior Associate Employment Contract - Vandermeer & Associates",
                   "Ref: VA/HR/2024/SA/018")
    story = []

    story += [sp(4),
        Paragraph("CONTRACT OF EMPLOYMENT", st["title"]),
        Paragraph("Senior Associate &#8212; Corporate &amp; Commercial Practice Group", st["subtitle"]),
        Paragraph("Ref: VA/HR/2024/SA/018 &nbsp;|&nbsp; Date: 15 January 2024", st["ref"]),
        hr()]

    story += [
        Paragraph("""<b>THIS CONTRACT OF EMPLOYMENT</b> is entered into as of 15 January 2024
            between:""", st["body"]),
        Paragraph("""<b>Vandermeer &amp; Associates NV</b>, a law firm incorporated under the laws of
            the Netherlands, having its principal place of business at Herengracht 182, 1016 BR
            Amsterdam (<b>&#8220;the Firm&#8221;</b>); and""", st["parties"]),
        Paragraph("<b>and</b>", st["center"]),
        Paragraph("""<b>Dr. Isabelle Fontaine</b>, residing at Keizersgracht 44, 1015 CT Amsterdam
            (<b>&#8220;the Employee&#8221;</b>).""", st["parties"]),
        hr()]

    story += [
        Paragraph("1.&nbsp;&nbsp;APPOINTMENT AND DUTIES", st["h1"]),
        Paragraph("""1.1&nbsp;&nbsp;The Firm appoints the Employee as <b>Senior Associate</b> in the
            Corporate &amp; Commercial Practice Group, commencing on 1 February 2024
            (<b>&#8220;Commencement Date&#8221;</b>).""", st["clause"]),
        Paragraph("""1.2&nbsp;&nbsp;The Employee shall perform such duties as are reasonably assigned
            by the Managing Partner or relevant Practice Group Head, including advising clients on
            mergers and acquisitions, commercial contracts, and corporate restructurings.""", st["clause"]),
        Paragraph("""1.3&nbsp;&nbsp;The Employee shall devote the whole of their working time, attention
            and abilities to the business of the Firm during normal working hours.""", st["clause"])]

    story += [
        Paragraph("2.&nbsp;&nbsp;REMUNERATION", st["h1"]),
        Paragraph("""2.1&nbsp;&nbsp;The Firm shall pay the Employee a gross annual salary of
            <b>EUR 128,000</b>, payable in equal monthly instalments on the last Business Day of
            each month.""", st["clause"]),
        Paragraph("""2.2&nbsp;&nbsp;The Employee shall be eligible for an annual discretionary
            performance bonus of up to 25% of base salary, subject to the Firm's bonus policy
            in force from time to time.""", st["clause"]),
        Paragraph("""2.3&nbsp;&nbsp;The Employee's salary shall be reviewed annually with effect from
            1 January of each year. The Firm is under no obligation to award any increase.""",
            st["clause"])]

    story += [
        Paragraph("3.&nbsp;&nbsp;NOTICE PERIODS AND TERMINATION", st["h1"]),
        Paragraph("""3.1&nbsp;&nbsp;<b>Notice by the Employee.</b> The Employee may terminate this
            Contract by giving the Firm not less than <b>three (3) months'</b> written
            notice.""", st["clause"]),
        Paragraph("""3.2&nbsp;&nbsp;<b>Notice by the Firm.</b> The Firm may terminate this Contract by
            giving written notice as follows:""", st["clause"]),
        Paragraph("""(a)&nbsp;&nbsp;during the first year of employment: one (1) month's notice;""",
            st["sub"]),
        Paragraph("""(b)&nbsp;&nbsp;from year two onwards: one (1) additional week per completed year
            of service, up to a maximum of thirteen (13) weeks.""", st["sub"]),
        Paragraph("""3.3&nbsp;&nbsp;<b>Summary Dismissal.</b> The Firm may terminate this Contract with
            immediate effect, without notice or payment in lieu, in the event of gross misconduct,
            dishonesty, serious breach of professional duties, or conduct likely to bring the Firm
            into disrepute.""", st["clause"]),
        Paragraph("""3.4&nbsp;&nbsp;<b>Garden Leave.</b> During any notice period, the Firm may require
            the Employee to remain away from the Firm's premises and refrain from performing any duties
            (<b>&#8220;Garden Leave&#8221;</b>). During Garden Leave, salary and benefits shall
            continue.""", st["clause"])]

    story.append(PageBreak())

    story += [
        Paragraph("4.&nbsp;&nbsp;RESTRICTIVE COVENANTS", st["h1"]),
        Paragraph("""4.1&nbsp;&nbsp;For a period of <b>twelve (12) months</b> following the Termination
            Date, the Employee shall not, without the Firm's prior written consent:""", st["clause"]),
        Paragraph("""(a)&nbsp;&nbsp;solicit or approach any client of the Firm with whom the Employee
            had material contact during the final 12 months of employment;""", st["sub"]),
        Paragraph("""(b)&nbsp;&nbsp;solicit, induce or attempt to induce any employee or partner of the
            Firm to leave their employment; or""", st["sub"]),
        Paragraph("""(c)&nbsp;&nbsp;act in a legal capacity for any direct competitor of the Firm
            operating in the Netherlands and Belgium.""", st["sub"]),
        Paragraph("""4.2&nbsp;&nbsp;The Employee acknowledges that each sub-clause constitutes an
            independent restriction and that the restrictions are reasonable and necessary to protect
            the Firm's legitimate business interests.""", st["clause"])]

    story += [
        Paragraph("5.&nbsp;&nbsp;CONFIDENTIALITY AND INTELLECTUAL PROPERTY", st["h1"]),
        Paragraph("""5.1&nbsp;&nbsp;The Employee shall maintain strict confidentiality of all client
            information, work product, business strategies and other confidential information relating
            to the Firm or its clients. This obligation continues without limitation after termination
            of employment.""", st["clause"]),
        Paragraph("""5.2&nbsp;&nbsp;All Intellectual Property Rights created by the Employee in the
            course of employment shall vest in and be the absolute property of the Firm.""", st["clause"])]

    story += [
        Paragraph("6.&nbsp;&nbsp;LIABILITY", st["h1"]),
        Paragraph("""6.1&nbsp;&nbsp;The Employee shall exercise all reasonable care and professional
            skill in performing their duties. Personal liability to the Firm for losses arising from
            negligence shall be limited to the extent of their direct culpability.""", st["clause"]),
        Paragraph("""6.2&nbsp;&nbsp;The Employee shall be covered by the Firm's professional indemnity
            insurance during the course of employment, subject to the policy terms.""", st["clause"])]

    story += [
        Paragraph("7.&nbsp;&nbsp;GOVERNING LAW", st["h1"]),
        Paragraph("""7.1&nbsp;&nbsp;This Contract shall be governed by the laws of the Netherlands.
            Disputes shall be submitted to the competent courts of Amsterdam.""", st["clause"]),
        sp(12),
        Paragraph("""IN WITNESS WHEREOF, the parties have signed this Contract on the date first
            above written.""", st["body"]),
        sp(16),
        sig_table(st,
            "<b>For and on behalf of VANDERMEER &amp; ASSOCIATES NV</b>",
            "<b>DR. ISABELLE FONTAINE</b>")]

    doc.build(story)
    print("  ✓  senior-associate-employment.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
# Document 3 — ASML Litigation Filing
# ═══════════════════════════════════════════════════════════════════════════════

def doc_asml_litigation():
    st = S()
    doc = make_doc(out("asml-litigation-filing.pdf"),
                   "ASML Holding NV v. Precision Components GmbH - District Court of Amsterdam",
                   "Case No. C/13/2024/01882")
    story = []

    story += [sp(4),
        Paragraph("IN THE DISTRICT COURT OF AMSTERDAM", st["title"]),
        Paragraph("COMMERCIAL CHAMBER", st["subtitle"]),
        Paragraph("Case No. C/13/2024/01882 &nbsp;|&nbsp; Ref: VA/LIT/2024/0093", st["ref"]),
        sp(8),
        Paragraph("STATEMENT OF CLAIM", st["title"]),
        hr()]

    story += [
        Paragraph("""<b>CLAIMANT:</b>&nbsp;&nbsp;ASML Holding NV, a public limited company incorporated
            under the laws of the Netherlands (KvK: 17070022), having its registered office at
            De Run 6501, 5504 DR Veldhoven (<b>&#8220;ASML&#8221;</b> or
            <b>&#8220;Claimant&#8221;</b>).""", st["parties"]),
        Paragraph("""<b>DEFENDANT:</b>&nbsp;&nbsp;Precision Components GmbH, a company incorporated
            under the laws of Germany (HRB 78432), having its registered office at
            Industriestrasse 47, 80339 Munich, Germany
            (<b>&#8220;Defendant&#8221;</b>).""", st["parties"]),
        hr()]

    story += [
        Paragraph("I.&nbsp;&nbsp;INTRODUCTION AND RELIEF SOUGHT", st["h1"]),
        Paragraph("""1.&nbsp;&nbsp;This action concerns the Defendant's material breach of a Supply and
            Manufacturing Agreement dated 12 September 2022 (the <b>&#8220;Agreement&#8221;</b>)
            whereby the Defendant was engaged to supply precision optical components for ASML's EUV
            lithography systems.""", st["clause"]),
        Paragraph("""2.&nbsp;&nbsp;By reason of the Defendant's breaches, ASML has suffered loss and
            damage quantified at <b>EUR 4,200,000</b> (four million two hundred thousand euros),
            comprising direct losses of EUR 2,700,000 and consequential losses of
            EUR 1,500,000.""", st["clause"]),
        Paragraph("3.&nbsp;&nbsp;ASML seeks judgment against the Defendant for:", st["clause"]),
        Paragraph("""(a)&nbsp;&nbsp;damages in the sum of EUR 4,200,000 or such other sum as the Court
            shall determine;""", st["sub"]),
        Paragraph("""(b)&nbsp;&nbsp;interest pursuant to Article 6:119a of the Dutch Civil Code
            (BW);""", st["sub"]),
        Paragraph("(c)&nbsp;&nbsp;costs of these proceedings; and", st["sub"]),
        Paragraph("(d)&nbsp;&nbsp;such further or other relief as the Court considers just.", st["sub"])]

    story += [
        Paragraph("II.&nbsp;&nbsp;FACTUAL BACKGROUND", st["h1"]),
        Paragraph("""4.&nbsp;&nbsp;On 12 September 2022, ASML and the Defendant entered into the
            Agreement for the supply of precision-ground silicon carbide mirror substrates
            (<b>&#8220;Components&#8221;</b>) for integration into ASML's NXE:3600D EUV
            platforms.""", st["clause"]),
        Paragraph("""5.&nbsp;&nbsp;The Agreement required the Defendant to deliver Components meeting
            the dimensional tolerances specified in Schedule A thereto, with delivery in quarterly
            batches of no fewer than forty (40) units.""", st["clause"]),
        Paragraph("""6.&nbsp;&nbsp;The Agreement did not provide for automatic renewal. It was fixed
            for a term of thirty-six (36) months expiring on 11 September 2025.""", st["clause"]),
        Paragraph("""7.&nbsp;&nbsp;Between Q1 2024 and Q3 2024, the Defendant delivered Components
            with surface flatness deviations exceeding the contractual tolerance of +/-0.3 nm RMS.
            ASML's quality control inspections documented deviations of between 1.2 nm and
            2.8 nm RMS.""", st["clause"]),
        Paragraph("""8.&nbsp;&nbsp;ASML notified the Defendant of the defects by letter dated
            14 May 2024 and issued a formal cure notice on 28 May 2024, affording thirty (30) days
            to remedy. The Defendant failed to deliver conforming Components within the cure
            period.""", st["clause"])]

    story.append(PageBreak())

    story += [
        Paragraph("III.&nbsp;&nbsp;LEGAL BASIS", st["h1"]),
        Paragraph("""9.&nbsp;&nbsp;The Defendant's delivery of non-conforming Components constitutes
            a non-conforming performance (<i>niet-conforme prestatie</i>) within the meaning of
            Article 7:17 of the Dutch Civil Code (BW).""", st["clause"]),
        Paragraph("""10.&nbsp;&nbsp;Pursuant to Article 6:74 BW, a party that fails to perform an
            obligation is liable to compensate the other party for the loss arising therefrom,
            provided the failure is attributable to the non-performing party.""", st["clause"]),
        Paragraph("""11.&nbsp;&nbsp;The Defendant's failure to deliver conforming Components is
            attributable to deficiencies in its manufacturing quality management system, which is
            not an event of force majeure.""", st["clause"]),
        Paragraph("""12.&nbsp;&nbsp;<b>Liability Structure.</b> The Agreement contains no general
            limitation of liability clause. Clause 18 of the Agreement provides a specific cap of
            EUR 1,000,000 on liability for damage to tooling, but this cap does not apply to the
            losses claimed herein, which relate to production downtime and lost revenues. Accordingly,
            the Defendant's liability for the losses claimed herein is uncapped.""", st["clause"]),
        Paragraph("""13.&nbsp;&nbsp;ASML is entitled to recover the full quantum of its loss as
            set out in Section IV below.""", st["clause"])]

    story += [
        Paragraph("IV.&nbsp;&nbsp;QUANTIFICATION OF LOSS", st["h1"]),
        sp(4),
        loss_table([
            ["Head of Loss", "Basis", "Amount (EUR)"],
            ["Replacement sourcing premium", "Emergency procurement, alternative supplier", "980,000"],
            ["Production line downtime", "21 days x EUR 85,714/day", "1,800,000"],
            ["Quality re-inspection costs", "ASML internal cost allocation", "220,000"],
            ["Customer delay penalties", "Contractual penalties paid to OEM customers", "700,000"],
            ["Consequential lost margin", "Q3 2024 revenue shortfall (expert report)", "500,000"],
            ["", "Total", "4,200,000"],
        ]),
        sp(8)]

    story += [
        Paragraph("V.&nbsp;&nbsp;PROCEDURAL MATTERS", st["h1"]),
        Paragraph("""14.&nbsp;&nbsp;The Agreement designates the District Court of Amsterdam
            (Rechtbank Amsterdam) as the exclusive jurisdiction, conferring jurisdiction on this
            Court.""", st["clause"]),
        Paragraph("""15.&nbsp;&nbsp;The applicable substantive law is Dutch law by express choice
            of the Parties pursuant to Article 3 of Regulation (EC) No 593/2008 (Rome I).""",
            st["clause"]),
        Paragraph("""16.&nbsp;&nbsp;ASML reserves the right to amend this Statement of Claim as
            further facts come to light and expert evidence is received.""", st["clause"]),
        sp(12),
        Paragraph("Respectfully submitted,", st["body"]),
        sp(6),
        Paragraph("""<b>Vandermeer &amp; Associates NV</b><br/>Attorneys for the Claimant<br/>
            Herengracht 182, 1016 BR Amsterdam<br/>Date: 3 June 2024""", st["body"])]

    doc.build(story)
    print("  ✓  asml-litigation-filing.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
# Document 4 — Legal Opinion: Data Processing
# ═══════════════════════════════════════════════════════════════════════════════

def doc_legal_opinion():
    st = S()
    doc = make_doc(out("legal-opinion-data-processing.pdf"),
                   "Legal Opinion - Data Processing and GDPR Liability - VA/OPN/2024/0031",
                   "Ref: VA/OPN/2024/0031 | PRIVILEGED")
    story = []

    story += [sp(4),
        Paragraph("LEGAL OPINION", st["title"]),
        Paragraph("Data Processing Arrangements and GDPR Liability Exposure", st["subtitle"]),
        Paragraph("Ref: VA/OPN/2024/0031 &nbsp;|&nbsp; Date: 20 February 2024 &nbsp;|&nbsp; PRIVILEGED &amp; CONFIDENTIAL", st["ref"]),
        hr()]

    story += [
        Paragraph("<b>CLIENT:</b>&nbsp;&nbsp;HealthBridge Analytics BV", st["bold"]),
        Paragraph("""<b>MATTER:</b>&nbsp;&nbsp;Assessment of data processing liability under the GDPR
            in connection with proposed SaaS platform deployment""", st["bold"]),
        Paragraph("""<b>PREPARED BY:</b>&nbsp;&nbsp;Dr. Isabelle Fontaine, Senior Associate;
            reviewed by Prof. Jan van Dijk, Partner""", st["bold"]),
        hr()]

    story += [
        Paragraph("1.&nbsp;&nbsp;SCOPE AND BASIS OF OPINION", st["h1"]),
        Paragraph("""1.1&nbsp;&nbsp;We have been asked to advise HealthBridge Analytics BV
            (<b>&#8220;HealthBridge&#8221;</b>) on the allocation of data controller and data processor
            responsibilities, and the associated GDPR liability exposure, arising from the proposed
            deployment of its SaaS analytics platform to three hospital networks in the Netherlands
            and Belgium.""", st["clause"]),
        Paragraph("""1.2&nbsp;&nbsp;This opinion is based on: (i) the draft Data Processing Agreement
            (<b>&#8220;DPA&#8221;</b>) provided to us on 5 February 2024; (ii) the proposed Technical
            and Organisational Measures (<b>&#8220;TOMs&#8221;</b>) schedule; and (iii) the applicable
            provisions of Regulation (EU) 2016/679 (<b>&#8220;GDPR&#8221;</b>) and the Dutch
            Implementation Act (<i>Uitvoeringswet AVG</i>).""", st["clause"]),
        Paragraph("""1.3&nbsp;&nbsp;This opinion is strictly limited to the questions identified in
            Section 2 and does not address any matters of Belgian law.""", st["clause"])]

    story += [
        Paragraph("2.&nbsp;&nbsp;QUESTIONS ADDRESSED", st["h1"]),
        Paragraph("""2.1&nbsp;&nbsp;Whether HealthBridge operates as a data processor, data controller,
            or joint controller in respect of the personal data processed through its
            platform.""", st["clause"]),
        Paragraph("""2.2&nbsp;&nbsp;The scope of HealthBridge's liability exposure under Article 82
            GDPR in the event of a personal data breach.""", st["clause"]),
        Paragraph("""2.3&nbsp;&nbsp;Whether the indemnification provisions in the draft DPA are adequate
            to protect HealthBridge from third-party claims.""", st["clause"])]

    story += [
        Paragraph("3.&nbsp;&nbsp;ANALYSIS", st["h1"]),
        Paragraph("""3.1&nbsp;&nbsp;<b>Controller/Processor Classification.</b> On the basis of the
            information provided, it is our opinion that HealthBridge operates as a
            <b>data processor</b> in respect of patient data processed on behalf of the hospital
            networks (who act as data controllers). HealthBridge determines the technical means of
            processing but not the purposes, which remain with the hospital networks.""", st["clause"]),
        Paragraph("""3.2&nbsp;&nbsp;<b>Joint Controller Risk.</b> HealthBridge's use of aggregated
            patient datasets for model training creates a meaningful risk of classification as a
            <b>joint controller</b> for that processing activity. We recommend HealthBridge either:
            (a) obtain explicit consent from the hospitals for model training use; or (b) anonymise
            training datasets to a standard compliant with Recital 26 GDPR.""", st["clause"]),
        Paragraph("""3.3&nbsp;&nbsp;<b>Article 82 Liability.</b> Under Article 82(2) GDPR, a data
            processor is liable for damage caused by processing only where it has not complied with
            GDPR obligations or acted outside the controller's lawful instructions. Given the volume
            of special category health data (Article 9 GDPR), a breach could attract fines of up to
            EUR 20 million or 4% of global turnover under Article 83(5) GDPR, and civil liability
            claims.""", st["clause"]),
        Paragraph("""3.4&nbsp;&nbsp;<b>Indemnification Assessment.</b> Clause 14.2 of the draft DPA
            limits HealthBridge's indemnification exposure to direct damages not exceeding the fees
            paid in the preceding twelve-month period. This cap is commercially reasonable but may be
            challenged as insufficient given the sensitivity of the data. We recommend HealthBridge
            maintain a minimum cyber liability insurance policy of EUR 5,000,000 per
            incident.""", st["clause"])]

    story.append(PageBreak())

    story += [
        Paragraph("4.&nbsp;&nbsp;CONCLUSIONS AND RECOMMENDATIONS", st["h1"]),
        Paragraph("""4.1&nbsp;&nbsp;HealthBridge is properly characterised as a data processor for
            primary processing activities. The joint controller risk for model training should be
            mitigated as described in paragraph 3.2 above.""", st["clause"]),
        Paragraph("""4.2&nbsp;&nbsp;HealthBridge's GDPR liability exposure is material. The
            indemnification cap in the DPA is reasonable but should be supplemented by adequate
            insurance coverage.""", st["clause"]),
        Paragraph("""4.3&nbsp;&nbsp;We recommend the following amendments to the draft DPA:""",
            st["clause"]),
        Paragraph("""(a)&nbsp;&nbsp;Insert an explicit prohibition on processing data beyond the
            documented purpose (Clause 5);""", st["sub"]),
        Paragraph("""(b)&nbsp;&nbsp;Strengthen the sub-processor notification obligation from 30 to
            14 days (Clause 8);""", st["sub"]),
        Paragraph("""(c)&nbsp;&nbsp;Include a data breach notification SLA of 24 hours to align with
            evolving supervisory expectations (Clause 11); and""", st["sub"]),
        Paragraph("""(d)&nbsp;&nbsp;Add a model training restriction clause confirming
            pseudonymisation or anonymisation requirements.""", st["sub"]),
        Paragraph("""4.4&nbsp;&nbsp;<b>This opinion is governed by Dutch law and is issued solely for
            the benefit of HealthBridge Analytics BV. It may not be relied upon by any third party
            without our prior written consent.</b>""", st["clause"]),
        sp(12),
        Paragraph("""<b>Vandermeer &amp; Associates NV</b><br/>Herengracht 182, 1016 BR
            Amsterdam<br/>20 February 2024""", st["body"])]

    doc.build(story)
    print("  ✓  legal-opinion-data-processing.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
# Document 5 — Corporate Governance Report
# ═══════════════════════════════════════════════════════════════════════════════

def doc_governance():
    st = S()
    doc = make_doc(out("corporate-governance-report.pdf"),
                   "Corporate Governance Compliance Report - NovaTech Holdings NV - FY 2023",
                   "Ref: VA/GOV/2024/0012")
    story = []

    story += [sp(4),
        Paragraph("CORPORATE GOVERNANCE COMPLIANCE REPORT", st["title"]),
        Paragraph("NovaTech Holdings NV &nbsp;|&nbsp; Financial Year 2023", st["subtitle"]),
        Paragraph("Ref: VA/GOV/2024/0012 &nbsp;|&nbsp; Prepared: 28 March 2024 &nbsp;|&nbsp; CONFIDENTIAL", st["ref"]),
        hr()]

    story += [
        Paragraph("1.&nbsp;&nbsp;EXECUTIVE SUMMARY", st["h1"]),
        Paragraph("""1.1&nbsp;&nbsp;This report has been prepared by Vandermeer &amp; Associates NV at
            the request of the Supervisory Board of NovaTech Holdings NV
            (<b>&#8220;NovaTech&#8221;</b> or the <b>&#8220;Company&#8221;</b>) to assess compliance
            with the Dutch Corporate Governance Code (<b>&#8220;DCGC&#8221;</b>) for the financial year
            ended 31 December 2023.""", st["clause"]),
        Paragraph("""1.2&nbsp;&nbsp;Overall Assessment: The Company is <b>substantially compliant</b>
            with the principles and best practice provisions of the DCGC. Three areas require remedial
            action, as detailed in Section 5 of this Report.""", st["clause"]),
        Paragraph("""1.3&nbsp;&nbsp;This report is prepared for the exclusive use of the Supervisory
            Board and the Audit Committee. It is legally privileged and confidential.""", st["clause"])]

    story += [
        Paragraph("2.&nbsp;&nbsp;BOARD COMPOSITION AND INDEPENDENCE", st["h1"]),
        Paragraph("""2.1&nbsp;&nbsp;The Management Board comprises four (4) executive directors:
            the Chief Executive Officer, Chief Financial Officer, Chief Operating Officer, and
            Chief Technology Officer.""", st["clause"]),
        Paragraph("""2.2&nbsp;&nbsp;The Supervisory Board comprises six (6) members, of whom five (5)
            are assessed as independent within the meaning of best practice provision 2.1.7 of the
            DCGC. The Chair of the Supervisory Board, Mr. E. Brouwer, is independent.""", st["clause"]),
        Paragraph("""2.3&nbsp;&nbsp;Board diversity: As of 31 December 2023, 38% of Supervisory Board
            seats and 25% of Management Board seats are held by women, consistent with Article 2:166
            BW targets.""", st["clause"]),
        Paragraph("""2.4&nbsp;&nbsp;<b>Finding:</b> One Supervisory Board member (Mr. A. De Graaf)
            has served for eleven (11) years. The DCGC recommends a maximum of three four-year terms.
            NovaTech should document the Supervisory Board's reasoning regarding
            reappointment.""", st["clause"])]

    story += [
        Paragraph("3.&nbsp;&nbsp;RISK MANAGEMENT AND INTERNAL CONTROL", st["h1"]),
        Paragraph("""3.1&nbsp;&nbsp;The Management Board has implemented an enterprise risk management
            framework aligned with ISO 31000:2018. Material risks are reported to the Audit Committee
            on a quarterly basis.""", st["clause"]),
        Paragraph("""3.2&nbsp;&nbsp;NovaTech maintains an internal audit function. The 2023 audit plan
            was approved by the Audit Committee and covered IT security, procurement processes, and
            financial reporting controls.""", st["clause"]),
        Paragraph("""3.3&nbsp;&nbsp;<b>Finding:</b> The Company's whistleblower policy has not been
            updated to reflect the requirements of the EU Whistleblower Directive as implemented by
            the Dutch <i>Wet bescherming klokkenluiders</i> (effective 18 February 2023). Immediate
            remediation is required.""", st["clause"])]

    story.append(PageBreak())

    story += [
        Paragraph("4.&nbsp;&nbsp;LIABILITY FRAMEWORK", st["h1"]),
        Paragraph("""4.1&nbsp;&nbsp;<b>Management Board Liability.</b> Under Article 2:9 BW, members
            of the Management Board may be held jointly and severally liable to the Company for
            improper management. Liability to third parties may arise under Article 6:162 BW (tort)
            where conduct amounts to serious personal culpability
            (<i>ernstig verwijt</i>).""", st["clause"]),
        Paragraph("""4.2&nbsp;&nbsp;<b>D&amp;O Insurance.</b> NovaTech maintains Directors' &amp;
            Officers' liability insurance with an aggregate limit of <b>EUR 25,000,000</b> per claim,
            subject to standard exclusions including wilful misconduct and criminal acts. The Firm
            recommends the Company review retroactive coverage for pre-acquisition liabilities
            following the NovaTech-Axion acquisition completed in Q2 2023.""", st["clause"]),
        Paragraph("""4.3&nbsp;&nbsp;<b>Discharge (Decharge).</b> The Annual General Meeting of
            15 May 2023 granted discharge to both Boards for conduct during FY 2022. Discharge for
            FY 2023 will be sought at the AGM scheduled for May 2024.""", st["clause"]),
        Paragraph("""4.4&nbsp;&nbsp;<b>Indemnification.</b> The Company's Articles of Association
            provide for indemnification of current and former board members against costs and
            liabilities incurred in connection with proceedings arising from their functions, to the
            extent permitted by law and not covered by insurance.""", st["clause"])]

    story += [
        Paragraph("5.&nbsp;&nbsp;REMEDIAL ACTION PLAN", st["h1"]),
        sp(4),
        action_table([
            ["#", "Finding", "Required Action", "Target Date"],
            ["1", "SB tenure (2.4)", "Document board decision on reappointment", "30 Apr 2024"],
            ["2", "Whistleblower policy (3.3)", "Update policy to comply with Wet bescherming klokkenluiders", "31 Mar 2024"],
            ["3", "D&O retroactive cover (4.2)", "Review and extend policy retroactive date", "30 Jun 2024"],
        ]),
        sp(8)]

    story += [
        Paragraph("6.&nbsp;&nbsp;CONCLUSIONS", st["h1"]),
        Paragraph("""6.1&nbsp;&nbsp;NovaTech Holdings NV is substantially compliant with the DCGC for
            FY 2023. The three findings identified are remediable and do not represent material
            governance failures.""", st["clause"]),
        Paragraph("""6.2&nbsp;&nbsp;Subject to implementation of the Remedial Action Plan, the
            Supervisory Board may confirm in the FY 2023 Annual Report that the Company applies the
            DCGC principles and, where deviation occurs, has adequately explained such
            deviation.""", st["clause"]),
        sp(10),
        Paragraph("""<b>Vandermeer &amp; Associates NV</b><br/>Corporate Advisory Practice<br/>
            28 March 2024""", st["body"])]

    doc.build(story)
    print("  ✓  corporate-governance-report.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
# Document 6 — Dutch Supply Agreement
# ═══════════════════════════════════════════════════════════════════════════════

def doc_dutch_supply():
    st = S()
    doc = make_doc(out("dutch-supply-agreement.pdf"),
                   "Leveringsovereenkomst - Pharos Logistiek BV en Delta Packaging NV",
                   "Ref: VA/2024/LEV/0028")
    story = []

    story += [sp(4),
        Paragraph("LEVERINGSOVEREENKOMST", st["title"]),
        Paragraph("Pharos Logistiek BV en Delta Packaging NV", st["subtitle"]),
        Paragraph("Referentie: VA/2024/LEV/0028 &nbsp;|&nbsp; Datum: 1 april 2024", st["ref"]),
        hr()]

    story += [
        Paragraph("""<b>DEZE LEVERINGSOVEREENKOMST</b> (de <b>&#8220;Overeenkomst&#8221;</b>) wordt
            aangegaan op 1 april 2024 (de <b>&#8220;Ingangsdatum&#8221;</b>) door en tussen:""",
            st["body"]),
        Paragraph("""<b>Pharos Logistiek BV</b>, een besloten vennootschap met beperkte
            aansprakelijkheid opgericht naar Nederlands recht, ingeschreven bij de Kamer van
            Koophandel onder nummer 68441293, gevestigd aan de Nieuwe Havenweg 88, 3088 AC Rotterdam
            (<b>&#8220;Afnemer&#8221;</b>);""", st["parties"]),
        Paragraph("<b>en</b>", st["center"]),
        Paragraph("""<b>Delta Packaging NV</b>, een naamloze vennootschap opgericht naar Belgisch recht,
            ingeschreven bij de Kruispuntbank van Ondernemingen onder nummer 0471.882.399, gevestigd
            aan het Industriepark 14, 2100 Antwerpen, Belgie
            (<b>&#8220;Leverancier&#8221;</b>).""", st["parties"]),
        Paragraph("""Partijen worden hierna afzonderlijk aangeduid als een
            <b>&#8220;Partij&#8221;</b> en gezamenlijk als de
            <b>&#8220;Partijen&#8221;</b>.""", st["body"]),
        hr()]

    story += [
        Paragraph("1.&nbsp;&nbsp;DEFINITIES", st["h1"]),
        Paragraph("""1.1&nbsp;&nbsp;In deze Overeenkomst hebben de volgende begrippen de hieraan
            toegekende betekenis:""", st["clause"]),
        Paragraph("""1.1.1&nbsp;&nbsp;<b>&#8220;Goederen&#8221;</b>: de verpakkingsmaterialen en
            aanverwante producten zoals omschreven in Bijlage A bij deze Overeenkomst.""", st["sub"]),
        Paragraph("""1.1.2&nbsp;&nbsp;<b>&#8220;Inkoopprijs&#8221;</b>: de overeengekomen prijs per
            eenheid zoals vermeld in de toepasselijke Inkooporder.""", st["sub"]),
        Paragraph("""1.1.3&nbsp;&nbsp;<b>&#8220;Inkooporder&#8221;</b> of <b>&#8220;IO&#8221;</b>:
            een schriftelijke bestelling door de Afnemer met verwijzing naar deze
            Overeenkomst.""", st["sub"]),
        Paragraph("""1.1.4&nbsp;&nbsp;<b>&#8220;Werkdag&#8221;</b>: iedere dag behalve een zaterdag,
            zondag of officiele feestdag in Nederland.""", st["sub"])]

    story += [
        Paragraph("2.&nbsp;&nbsp;LEVERING VAN GOEDEREN", st["h1"]),
        Paragraph("""2.1&nbsp;&nbsp;De Leverancier verbindt zich ertoe de Goederen te leveren
            overeenkomstig de specificaties in Bijlage A en de toepasselijke Inkooporders, op de
            overeengekomen leveringsdatums.""", st["clause"]),
        Paragraph("""2.2&nbsp;&nbsp;Levering geschiedt DDP (Delivered Duty Paid - Incoterms 2020) op
            het door de Afnemer aangegeven leveringsadres in Nederland.""", st["clause"]),
        Paragraph("""2.3&nbsp;&nbsp;De Leverancier zal de Afnemer onverwijld schriftelijk informeren
            indien levering op de overeengekomen datum niet haalbaar is, doch uiterlijk vijf (5)
            Werkdagen voor de geplande leveringsdatum.""", st["clause"])]

    story += [
        Paragraph("3.&nbsp;&nbsp;BETALING", st["h1"]),
        Paragraph("""3.1&nbsp;&nbsp;<b>Betalingstermijn.</b> De Afnemer zal de Inkoopprijs betalen
            binnen <b>zestig (60) Werkdagen</b> na ontvangst van een correcte factuur, mits de
            geleverde Goederen voldoen aan de overeengekomen specificaties.""", st["clause"]),
        Paragraph("""3.2&nbsp;&nbsp;<b>Factureringswijze.</b> Facturen dienen te worden ingediend via
            het elektronische inkoopplatform van de Afnemer (Coupa) en dienen in ieder geval te
            vermelden: het IO-nummer, het artikelnummer, de geleverde hoeveelheid, de eenheidsprijs
            en het toepasselijke BTW-bedrag.""", st["clause"]),
        Paragraph("""3.3&nbsp;&nbsp;<b>Rente bij te late betaling.</b> Bij overschrijding van de
            betalingstermijn is de Afnemer van rechtswege rente verschuldigd gelijk aan de wettelijke
            handelsrente als bedoeld in artikel 6:119a BW, te rekenen vanaf de vervaldag tot aan de
            dag van volledige betaling.""", st["clause"]),
        Paragraph("""3.4&nbsp;&nbsp;<b>Verrekening.</b> De Afnemer is bevoegd vorderingen op de
            Leverancier te verrekenen met betalingsverplichtingen jegens de
            Leverancier.""", st["clause"]),
        Paragraph("""3.5&nbsp;&nbsp;<b>Eigendomsvoorbehoud.</b> De Goederen blijven eigendom van de
            Leverancier totdat volledige betaling door de Afnemer heeft plaatsgevonden
            (artikel 3:92 BW).""", st["clause"])]

    story.append(PageBreak())

    story += [
        Paragraph("4.&nbsp;&nbsp;OPZEGGING EN LOOPTIJD", st["h1"]),
        Paragraph("""4.1&nbsp;&nbsp;<b>Looptijd.</b> Deze Overeenkomst treedt in werking op de
            Ingangsdatum en geldt voor een initiele periode van een (1) jaar. Zij wordt daarna
            telkens stilzwijgend verlengd voor periodes van een (1) jaar, tenzij een van de Partijen
            de Overeenkomst schriftelijk opzegt met inachtneming van een
            <b>opzegtermijn van zestig (60) Werkdagen</b> voor het verstrijken van de dan lopende
            periode.""", st["clause"]),
        Paragraph("""4.2&nbsp;&nbsp;<b>Opzegging wegens wanprestatie.</b> Iedere Partij is gerechtigd
            deze Overeenkomst met onmiddellijke ingang schriftelijk te ontbinden indien:""",
            st["clause"]),
        Paragraph("""(a)&nbsp;&nbsp;de andere Partij tekortschiet in de nakoming van een wezenlijke
            verplichting en dit verzuim niet binnen dertig (30) Werkdagen na schriftelijke
            ingebrekestelling heeft hersteld;""", st["sub"]),
        Paragraph("""(b)&nbsp;&nbsp;aan de andere Partij (voorlopige) surseance van betaling wordt
            verleend of zij in staat van faillissement wordt verklaard.""", st["sub"]),
        Paragraph("""4.3&nbsp;&nbsp;<b>Gevolgen van beeindiging.</b> Na beeindiging van deze
            Overeenkomst dienen lopende Inkooporders door de Leverancier te worden afgerond, tenzij
            de Afnemer schriftelijk anders aangeeft. Reeds betaalde maar nog niet geleverde bedragen
            worden gerestitueerd.""", st["clause"])]

    story += [
        Paragraph("5.&nbsp;&nbsp;AANSPRAKELIJKHEID", st["h1"]),
        Paragraph("""5.1&nbsp;&nbsp;<b>Beperking van aansprakelijkheid.</b> De totale aansprakelijkheid
            van de Leverancier jegens de Afnemer, ongeacht de rechtsgrond, is beperkt tot het bedrag
            dat de Afnemer in de twaalf (12) maanden voorafgaand aan het schadeveroorzakende feit
            heeft betaald, met een maximum van <b>EUR 750.000</b> per
            schadegeval.""", st["clause"]),
        Paragraph("""5.2&nbsp;&nbsp;<b>Uitsluiting gevolgschade.</b> Geen van de Partijen is jegens
            de andere Partij aansprakelijk voor indirecte schade, gevolgschade, gederfde winst,
            gederfde omzet of gederfde verwachte besparingen.""", st["clause"]),
        Paragraph("""5.3&nbsp;&nbsp;<b>Uitzonderingen.</b> De beperkingen en uitsluitingen in
            artikel 5 zijn niet van toepassing in geval van opzet of bewuste roekeloosheid van de
            aansprakelijk gestelde Partij.""", st["clause"])]

    story += [
        Paragraph("6.&nbsp;&nbsp;TOEPASSELIJK RECHT EN GESCHILLENBESLECHTING", st["h1"]),
        Paragraph("""6.1&nbsp;&nbsp;Op deze Overeenkomst is uitsluitend Nederlands recht van
            toepassing.""", st["clause"]),
        Paragraph("""6.2&nbsp;&nbsp;Geschillen worden bij uitsluiting voorgelegd aan de bevoegde
            rechter te Rotterdam.""", st["clause"]),
        sp(12),
        Paragraph("""TEN BLIJKE WAARVAN hebben de Partijen deze Overeenkomst laten ondertekenen op de
            datum als hierboven vermeld.""", st["body"]),
        sp(16),
        sig_table(st,
            "<b>Voor en namens PHAROS LOGISTIEK BV</b>",
            "<b>Voor en namens DELTA PACKAGING NV</b>")]

    doc.build(story)
    print("  ✓  dutch-supply-agreement.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
# Document 7 — Accenture NDA
# ═══════════════════════════════════════════════════════════════════════════════

def doc_nda():
    st = S()
    doc = make_doc(out("accenture-nda.pdf"),
                   "Mutual NDA - Accenture BV and Luminary AI BV",
                   "Ref: VA/2024/NDA/0061 | CONFIDENTIAL")
    story = []

    story += [sp(4),
        Paragraph("MUTUAL NON-DISCLOSURE AGREEMENT", st["title"]),
        Paragraph("Accenture BV and Luminary AI BV", st["subtitle"]),
        Paragraph("Ref: VA/2024/NDA/0061 &nbsp;|&nbsp; Date: 10 April 2024", st["ref"]),
        hr()]

    story += [
        Paragraph("""<b>THIS MUTUAL NON-DISCLOSURE AGREEMENT</b> (the
            <b>&#8220;Agreement&#8221;</b>) is entered into as of 10 April 2024 (the
            <b>&#8220;Effective Date&#8221;</b>) by and between:""", st["body"]),
        Paragraph("""<b>Accenture BV</b>, a private limited liability company incorporated under the
            laws of the Netherlands (KvK: 34117484), having its registered office at
            Gustav Mahlerplein 90, 1082 MA Amsterdam
            (<b>&#8220;Accenture&#8221;</b>); and""", st["parties"]),
        Paragraph("<b>and</b>", st["center"]),
        Paragraph("""<b>Luminary AI BV</b>, a private limited liability company incorporated under
            the laws of the Netherlands (KvK: 82956714), having its registered office at
            Science Park 400, 1098 XH Amsterdam
            (<b>&#8220;Luminary&#8221;</b>).""", st["parties"]),
        Paragraph("""Each party may be referred to as a <b>&#8220;Disclosing Party&#8221;</b> when
            disclosing Confidential Information and as a <b>&#8220;Receiving Party&#8221;</b> when
            receiving it.""", st["body"]),
        hr()]

    story += [
        Paragraph("1.&nbsp;&nbsp;DEFINITIONS", st["h1"]),
        Paragraph("""1.1&nbsp;&nbsp;<b>&#8220;Confidential Information&#8221;</b> means any non-public
            information, data, know-how, trade secrets, business plans, financial data, technical
            specifications, client lists, pricing structures and any other information designated as
            confidential or which a reasonable person would recognise as confidential given its nature
            and the circumstances of disclosure.""", st["clause"]),
        Paragraph("""1.2&nbsp;&nbsp;<b>&#8220;Permitted Purpose&#8221;</b> means the evaluation of a
            potential commercial collaboration between the Parties in the field of AI-driven supply
            chain optimisation.""", st["clause"]),
        Paragraph("""1.3&nbsp;&nbsp;Confidential Information shall not include information that:
            (a) is or becomes publicly available other than through breach of this Agreement;
            (b) was known to the Receiving Party prior to disclosure; (c) is lawfully received from
            a third party without restriction; or (d) is independently developed without reference to
            the Confidential Information.""", st["clause"])]

    story += [
        Paragraph("2.&nbsp;&nbsp;CONFIDENTIALITY OBLIGATIONS", st["h1"]),
        Paragraph("""2.1&nbsp;&nbsp;Each Receiving Party undertakes to:""", st["clause"]),
        Paragraph("""(a)&nbsp;&nbsp;keep the Disclosing Party's Confidential Information strictly
            confidential and use at least the same degree of care it uses to protect its own
            confidential information, but in no event less than reasonable care;""", st["sub"]),
        Paragraph("""(b)&nbsp;&nbsp;not disclose Confidential Information to any third party without
            the Disclosing Party's prior written consent;""", st["sub"]),
        Paragraph("""(c)&nbsp;&nbsp;use the Confidential Information solely for the Permitted
            Purpose; and""", st["sub"]),
        Paragraph("""(d)&nbsp;&nbsp;restrict disclosure to those employees, officers and professional
            advisers (<b>&#8220;Representatives&#8221;</b>) who have a genuine need to know and are
            bound by confidentiality obligations no less protective than this Agreement.""", st["sub"]),
        Paragraph("""2.2&nbsp;&nbsp;The Receiving Party shall remain liable for any breach of this
            Agreement by its Representatives.""", st["clause"]),
        Paragraph("""2.3&nbsp;&nbsp;If a Receiving Party is required to disclose Confidential
            Information by applicable law or court order, it shall: (i) give the Disclosing Party
            prompt written notice where permitted; (ii) co-operate reasonably in seeking a protective
            order; and (iii) disclose only that portion strictly required.""", st["clause"])]

    story.append(PageBreak())

    story += [
        Paragraph("3.&nbsp;&nbsp;TERM AND TERMINATION", st["h1"]),
        Paragraph("""3.1&nbsp;&nbsp;<b>Term.</b> This Agreement shall commence on the Effective Date
            and remain in force for a period of <b>two (2) years</b>, unless earlier terminated in
            accordance with Clause 3.2.""", st["clause"]),
        Paragraph("""3.2&nbsp;&nbsp;<b>Termination.</b> Either Party may terminate this Agreement upon
            <b>thirty (30) days'</b> written notice. Termination shall not affect obligations that
            have accrued prior to the date of termination.""", st["clause"]),
        Paragraph("""3.3&nbsp;&nbsp;<b>Survival of Obligations.</b> Confidentiality obligations under
            Clause 2 shall survive termination or expiry of this Agreement for a further period of
            <b>three (3) years</b>.""", st["clause"]),
        Paragraph("""3.4&nbsp;&nbsp;<b>Return or Destruction.</b> Upon termination or upon the
            Disclosing Party's written request, the Receiving Party shall promptly return or
            certifiably destroy all Confidential Information and copies thereof, and shall certify
            such return or destruction in writing within five (5) Business Days.""", st["clause"])]

    story += [
        Paragraph("4.&nbsp;&nbsp;LIABILITY AND REMEDIES", st["h1"]),
        Paragraph("""4.1&nbsp;&nbsp;Each Party acknowledges that a breach of this Agreement may cause
            irreparable harm for which monetary damages would be an inadequate remedy. Accordingly,
            the Disclosing Party shall be entitled to seek equitable relief, including injunction and
            specific performance, in addition to all other remedies available at law or in
            equity.""", st["clause"]),
        Paragraph("""4.2&nbsp;&nbsp;<b>Limitation of Liability.</b> Subject to Clause 4.1, the
            aggregate liability of either Party to the other under this Agreement shall not exceed
            <b>EUR 250,000</b> (two hundred and fifty thousand euros).""", st["clause"]),
        Paragraph("""4.3&nbsp;&nbsp;<b>Exclusion of Consequential Loss.</b> Neither Party shall be
            liable to the other for any indirect, special or consequential loss, including loss of
            profit, loss of business or loss of opportunity, arising from or in connection with this
            Agreement.""", st["clause"]),
        Paragraph("""4.4&nbsp;&nbsp;Nothing in this Agreement shall exclude or limit liability for
            fraud, wilful misconduct or any other liability that cannot be lawfully
            excluded.""", st["clause"])]

    story += [
        Paragraph("5.&nbsp;&nbsp;GENERAL", st["h1"]),
        Paragraph("""5.1&nbsp;&nbsp;<b>No Licence.</b> Nothing in this Agreement shall be construed
            as granting any licence or right in respect of any Intellectual Property Rights of the
            Disclosing Party.""", st["clause"]),
        Paragraph("""5.2&nbsp;&nbsp;<b>No Obligation.</b> This Agreement does not obligate either
            Party to proceed with any transaction or business relationship.""", st["clause"]),
        Paragraph("""5.3&nbsp;&nbsp;<b>Governing Law.</b> This Agreement shall be governed by Dutch
            law. The Parties submit to the exclusive jurisdiction of the courts of
            Amsterdam.""", st["clause"]),
        Paragraph("""5.4&nbsp;&nbsp;<b>Entire Agreement.</b> This Agreement constitutes the entire
            agreement between the Parties regarding its subject matter and supersedes all prior
            discussions and understandings.""", st["clause"]),
        sp(12),
        Paragraph("""IN WITNESS WHEREOF, the Parties have executed this Agreement as of the date
            first written above.""", st["body"]),
        sp(16),
        sig_table(st,
            "<b>For and on behalf of ACCENTURE BV</b>",
            "<b>For and on behalf of LUMINARY AI BV</b>")]

    doc.build(story)
    print("  ✓  accenture-nda.pdf")


# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generating test documents ...")
    doc_accenture_supply()
    doc_employment()
    doc_asml_litigation()
    doc_legal_opinion()
    doc_governance()
    doc_dutch_supply()
    doc_nda()
    print(f"\nAll documents written to: {os.path.abspath(OUT)}")
