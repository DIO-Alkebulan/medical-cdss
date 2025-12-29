"""
PDF Report Generation with comprehensive medical information
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict
import os


def generate_pdf_report(analysis, patient, doctor, prediction: Dict) -> str:
    """Generate comprehensive medical report as PDF"""
    
    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reports/report_{patient.name.replace(' ', '_')}_{timestamp}.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    story.append(Paragraph("AI-ASSISTED CHEST X-RAY ANALYSIS REPORT", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Header information box
    header_data = [
        ['Report Date:', datetime.now().strftime('%B %d, %Y %I:%M %p')],
        ['Report ID:', f"RPT-{analysis.id:06d}"],
        ['Analyzing Physician:', doctor.name],
        ['Specialty:', doctor.specialty],
        ['License Number:', doctor.license_number]
    ]
    
    header_table = Table(header_data, colWidths=[2*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Patient Information Section
    story.append(Paragraph("PATIENT INFORMATION", heading_style))
    
    patient_data = [
        ['Name:', patient.name, 'Age:', f"{patient.age} years"],
        ['Gender:', patient.gender, 'Patient ID:', f"PAT-{patient.id:06d}"],
    ]
    
    patient_table = Table(patient_data, colWidths=[1.2*inch, 2*inch, 1*inch, 1.8*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f3f4f6')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Clinical Indication
    story.append(Paragraph("CLINICAL INDICATION", heading_style))
    story.append(Paragraph(f"Symptoms: {analysis.symptoms}", styles['Normal']))
    
    if patient.medical_history:
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"Medical History: {patient.medical_history}", styles['Normal']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Vital Signs
    if any([analysis.temperature, analysis.oxygen_saturation, analysis.heart_rate, analysis.respiratory_rate]):
        story.append(Paragraph("VITAL SIGNS", heading_style))
        
        vital_data = []
        if analysis.temperature:
            vital_data.append(['Temperature:', f"{analysis.temperature}°C"])
        if analysis.oxygen_saturation:
            vital_data.append(['Oxygen Saturation:', f"{analysis.oxygen_saturation}%"])
        if analysis.heart_rate:
            vital_data.append(['Heart Rate:', f"{analysis.heart_rate} bpm"])
        if analysis.respiratory_rate:
            vital_data.append(['Respiratory Rate:', f"{analysis.respiratory_rate} breaths/min"])
        
        vital_table = Table(vital_data, colWidths=[2.5*inch, 3.5*inch])
        vital_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(vital_table)
        story.append(Spacer(1, 0.2*inch))
    
    # AI Analysis Results
    story.append(Paragraph("AI ANALYSIS RESULTS", heading_style))
    
    # Color code based on severity
    severity_colors = {
        'Mild': colors.HexColor('#10b981'),
        'Moderate': colors.HexColor('#f59e0b'),
        'Severe': colors.HexColor('#ef4444'),
        'None': colors.HexColor('#6b7280')
    }
    
    severity_color = severity_colors.get(prediction['severity'], colors.grey)
    
    results_data = [
        ['Detected Condition:', prediction['disease']],
        ['Confidence Level:', f"{prediction['confidence']:.1f}%"],
        ['Severity Grade:', prediction['severity']],
        ['Affected Regions:', ', '.join(prediction['affected_regions']) if prediction['affected_regions'] else 'N/A']
    ]
    
    results_table = Table(results_data, colWidths=[2.5*inch, 3.5*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (1, 2), (1, 2), severity_color),
        ('TEXTCOLOR', (1, 2), (1, 2), colors.white)
    ]))
    story.append(results_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Findings
    story.append(Paragraph("FINDINGS", heading_style))
    
    if prediction['disease'] != 'Normal':
        findings_text = f"""
        The chest X-ray demonstrates findings consistent with {prediction['disease']}. 
        AI analysis identified abnormalities in {', '.join(prediction['affected_regions']) if prediction['affected_regions'] else 'the lung fields'} 
        with {prediction['confidence']:.1f}% confidence. The severity is assessed as {prediction['severity'].lower()}.
        """
    else:
        findings_text = "The chest X-ray demonstrates clear lung fields with no acute abnormalities detected. Cardiac silhouette is within normal limits."
    
    story.append(Paragraph(findings_text.strip(), styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Impression
    story.append(Paragraph("IMPRESSION", heading_style))
    impression_text = f"{prediction['disease']} - {prediction['severity']} severity"
    story.append(Paragraph(impression_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    story.append(Paragraph("CLINICAL RECOMMENDATIONS", heading_style))
    
    for i, rec in enumerate(prediction['recommendations'], 1):
        story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        borderWidth=1,
        borderColor=colors.grey,
        borderPadding=10,
        backColor=colors.HexColor('#f9fafb')
    )
    
    disclaimer_text = """
    <b>IMPORTANT DISCLAIMER:</b> This report has been generated with AI assistance and represents a preliminary analysis. 
    All findings must be reviewed and confirmed by a qualified radiologist or physician before making any clinical decisions. 
    This AI system is designed to assist healthcare professionals, not replace clinical judgment. 
    The final diagnosis and treatment plan should be determined by the attending physician based on complete clinical context.
    """
    
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Signature section
    signature_data = [
        ['Physician Signature:', '_' * 40],
        ['Date:', datetime.now().strftime('%B %d, %Y')]
    ]
    
    signature_table = Table(signature_data, colWidths=[2*inch, 4*inch])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
    ]))
    story.append(signature_table)
    
    # Build PDF
    doc.build(story)
    
    return filename