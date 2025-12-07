# pdf_generator.py
"""
Générateur de rapports PDF pour l'application de gestion de stock
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from typing import List
import io


def get_category(article):
    """Helper pour obtenir la catégorie (gère category et categorie)"""
    return getattr(article, 'category', None) or getattr(article, 'categorie', 'N/A')

def get_reference(article):
    """Helper pour obtenir la référence"""
    return getattr(article, 'reference', 'N/A')

def get_prix_unitaire(article):
    """Helper pour obtenir le prix unitaire"""
    return getattr(article, 'prix_unitaire', 0.0)


def create_inventory_pdf(articles: List, stats: dict = None) -> bytes:
    """
    Génère un PDF complet de l'inventaire
    
    Args:
        articles: Liste des articles à inclure
        stats: Statistiques optionnelles
    
    Returns:
        bytes: Contenu du PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=30, leftMargin=30,
                           topMargin=30, bottomMargin=30)
    
    # Conteneur pour les éléments du PDF
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # En-tête du rapport
    title = Paragraph("📊 RAPPORT D'INVENTAIRE", title_style)
    elements.append(title)
    
    # Date du rapport
    date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    date_para = Paragraph(f"<i>Généré le {date_str}</i>", styles['Normal'])
    elements.append(date_para)
    elements.append(Spacer(1, 20))
    
    # Statistiques globales (si fournies)
    if stats:
        elements.append(Paragraph("📈 STATISTIQUES GLOBALES", heading_style))
        
        stats_data = [
            ['Indicateur', 'Valeur'],
            ['Total articles', str(stats.get('total_articles', 0))],
            ['Stock total', str(stats.get('stock_total', 0))],
            ['Alertes stock faible', str(stats.get('alertes_stock_faible', 0))],
            ['Catégories', str(stats.get('categories', 0))]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
    
    # Liste des articles
    elements.append(Paragraph("📦 DÉTAIL DE L'INVENTAIRE", heading_style))
    elements.append(Spacer(1, 12))
    
    # En-tête du tableau
    data = [['Réf', 'Nom', 'Catégorie', 'Qté', 'Prix Unit.', 'Valeur']]
    
    # Ajout des articles
    total_value = 0
    for article in articles:
        prix = get_prix_unitaire(article)
        valeur = article.quantite * prix
        total_value += valeur
        
        row = [
            get_reference(article),
            article.nom[:30],  # Limiter la longueur
            get_category(article),
            str(article.quantite),
            f"{prix:.2f}€",
            f"{valeur:.2f}€"
        ]
        data.append(row)
    
    # Ligne de total
    data.append(['', '', '', '', 'TOTAL:', f"{total_value:.2f}€"])
    
    # Création du tableau
    table = Table(data, colWidths=[1*inch, 2.2*inch, 1.3*inch, 0.6*inch, 1*inch, 1*inch])
    
    # Style du tableau
    table_style = [
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Corps du tableau
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
        
        # Ligne de total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fbbf24')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
    ]
    
    # Alertes visuelles pour stock faible
    for i, article in enumerate(articles, start=1):
        if article.quantite <= 10:
            table_style.append(('BACKGROUND', (3, i), (3, i), colors.HexColor('#fee2e2')))
            table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#dc2626')))
    
    table.setStyle(TableStyle(table_style))
    elements.append(table)
    
    # Pied de page
    elements.append(Spacer(1, 30))
    footer = Paragraph(
        "<i>Ce rapport a été généré automatiquement par le système de gestion de stock</i>",
        styles['Normal']
    )
    elements.append(footer)
    
    # Construction du PDF
    doc.build(elements)
    
    # Récupération du contenu
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def create_low_stock_alert_pdf(articles: List) -> bytes:
    """
    Génère un PDF d'alerte pour les articles en stock faible
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Titre d'alerte
    title_style = ParagraphStyle(
        'AlertTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    title = Paragraph("🚨 ALERTE STOCK FAIBLE", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    date_para = Paragraph(f"Généré le {date_str}", styles['Normal'])
    elements.append(date_para)
    elements.append(Spacer(1, 20))
    
    # Message d'alerte
    alert_msg = Paragraph(
        f"<b>{len(articles)} article(s)</b> nécessitent un réapprovisionnement urgent !",
        styles['Normal']
    )
    elements.append(alert_msg)
    elements.append(Spacer(1, 20))
    
    # Tableau des articles
    data = [['Référence', 'Nom', 'Catégorie', 'Stock Actuel', 'Statut']]
    
    for article in articles:
        status = "🔴 URGENT" if article.quantite <= 5 else "🟡 ATTENTION"
        data.append([
            get_reference(article),
            article.nom[:35],
            get_category(article),
            str(article.quantite),
            status
        ])
    
    table = Table(data, colWidths=[1.2*inch, 2.5*inch, 1.5*inch, 1*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Recommandation
    recommendation = Paragraph(
        "<b>Action recommandée :</b> Planifier une commande de réapprovisionnement dans les plus brefs délais.",
        styles['Normal']
    )
    elements.append(recommendation)
    
    doc.build(elements)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def create_category_report_pdf(categories_stats: List) -> bytes:
    """
    Génère un rapport PDF par catégorie
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    title = Paragraph("📊 RAPPORT PAR CATÉGORIE", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Tableau des catégories
    data = [['Catégorie', 'Nombre d\'articles', 'Stock Total']]
    
    for cat in categories_stats:
        data.append([
            cat['categorie'],
            str(cat['nombre_articles']),
            str(cat['stock_total'])
        ])
    
    table = Table(data, colWidths=[3*inch, 2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightblue])
    ]))
    
    elements.append(table)
    
    doc.build(elements)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content