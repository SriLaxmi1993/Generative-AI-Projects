"""
Utility functions for Competitor Analysis System
Includes PDF export and data formatting helpers
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib import colors
import re

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate professional PDF reports from competitor analysis results"""
    
    def __init__(self, company_name: str, industry: str):
        """
        Initialize PDF generator
        
        Args:
            company_name: Name of the company being analyzed
            industry: Industry sector
        """
        self.company_name = company_name
        self.industry = industry
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom paragraph styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading 2 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Heading 3 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['BodyText'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#2c3e50'),
            leftIndent=20,
            spaceAfter=6
        ))
    
    def generate_pdf(self, report_content: str) -> BytesIO:
        """
        Generate PDF from report content
        
        Args:
            report_content: Full report text content
            
        Returns:
            BytesIO: PDF file buffer
        """
        try:
            logger.info(f"Generating PDF report for {self.company_name}")
            
            # Create PDF document
            doc = SimpleDocTemplate(
                self.buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build content elements
            elements = []
            
            # Add title page
            elements.extend(self._create_title_page())
            
            # Parse and add report content
            elements.extend(self._parse_report_content(report_content))
            
            # Build PDF
            doc.build(elements)
            
            # Reset buffer position
            self.buffer.seek(0)
            
            logger.info("PDF generated successfully")
            return self.buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    def _create_title_page(self) -> List:
        """Create title page elements"""
        elements = []
        
        # Title
        title = Paragraph(
            "COMPETITOR ANALYSIS REPORT",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Company name
        company = Paragraph(
            f"<b>{self.company_name}</b>",
            self.styles['CustomHeading2']
        )
        elements.append(company)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Industry
        industry = Paragraph(
            f"Industry: {self.industry}",
            self.styles['CustomBody']
        )
        elements.append(industry)
        elements.append(Spacer(1, 0.1 * inch))
        
        # Date
        date = Paragraph(
            f"Report Date: {datetime.now().strftime('%B %d, %Y')}",
            self.styles['CustomBody']
        )
        elements.append(date)
        
        # Add page break
        elements.append(PageBreak())
        
        return elements
    
    def _parse_report_content(self, content: str) -> List:
        """Parse markdown-style report content into PDF elements"""
        elements = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Handle headers
            if line.startswith('# '):
                # H1
                text = line[2:].strip()
                elements.append(Paragraph(text, self.styles['CustomTitle']))
                elements.append(Spacer(1, 0.2 * inch))
                
            elif line.startswith('## '):
                # H2
                text = line[3:].strip()
                elements.append(Spacer(1, 0.15 * inch))
                elements.append(Paragraph(text, self.styles['CustomHeading2']))
                elements.append(Spacer(1, 0.1 * inch))
                
            elif line.startswith('### '):
                # H3
                text = line[4:].strip()
                elements.append(Paragraph(text, self.styles['CustomHeading3']))
                elements.append(Spacer(1, 0.05 * inch))
                
            elif line.startswith('- ') or line.startswith('* '):
                # Bullet point
                text = line[2:].strip()
                bullet = Paragraph(f"• {text}", self.styles['CustomBullet'])
                elements.append(bullet)
                
            elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
                # Numbered list
                text = line[3:].strip()
                num = line[0]
                bullet = Paragraph(f"{num}. {text}", self.styles['CustomBullet'])
                elements.append(bullet)
                
            elif line.startswith('---'):
                # Horizontal rule
                elements.append(Spacer(1, 0.1 * inch))
                
            else:
                # Regular paragraph
                if line:
                    # Clean up markdown formatting
                    text = self._clean_markdown(line)
                    para = Paragraph(text, self.styles['CustomBody'])
                    elements.append(para)
            
            i += 1
        
        return elements
    
    def _clean_markdown(self, text: str) -> str:
        """Clean markdown formatting for PDF rendering"""
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        # Code (inline)
        text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)
        
        return text


def format_report_for_display(report_content: str) -> Dict[str, str]:
    """
    Parse report content into sections for display in Streamlit tabs
    
    Args:
        report_content: Full report text
        
    Returns:
        Dict mapping section names to content
    """
    sections = {
        "overview": "",
        "detailed_analysis": "",
        "competitor_matrix": "",
        "recommendations": ""
    }
    
    try:
        # Split content into sections based on headers
        current_section = None
        current_content = []
        
        lines = report_content.split('\n')
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Detect section headers
            if 'executive summary' in line_lower or 'key findings' in line_lower:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = "overview"
                current_content = [line]
                
            elif 'detailed competitor analysis' in line_lower or 'swot' in line_lower:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = "detailed_analysis"
                current_content = [line]
                
            elif 'comparison matrix' in line_lower or 'competitive comparison' in line_lower:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = "competitor_matrix"
                current_content = [line]
                
            elif 'recommendation' in line_lower or 'strategic' in line_lower and 'recommendation' in line_lower:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = "recommendations"
                current_content = [line]
                
            else:
                if current_section:
                    current_content.append(line)
        
        # Add final section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        # If sections are empty, put everything in overview
        if not any(sections.values()):
            sections["overview"] = report_content
            
    except Exception as e:
        logger.error(f"Error formatting report: {str(e)}")
        sections["overview"] = report_content
    
    return sections


def extract_key_metrics(report_content: str) -> Dict:
    """
    Extract key metrics from the report for summary display
    
    Args:
        report_content: Full report text
        
    Returns:
        Dict containing extracted metrics
    """
    metrics = {
        "num_competitors": 0,
        "key_findings": [],
        "threat_level": "Medium",
        "opportunities": 0
    }
    
    try:
        lines = report_content.split('\n')
        
        # Count competitors (look for ### headings in competitor sections)
        for line in lines:
            if line.startswith('### ') and not any(x in line.lower() for x in ['recommendation', 'summary', 'finding']):
                metrics["num_competitors"] += 1
        
        # Extract key findings (numbered lists in key findings section)
        in_findings = False
        for line in lines:
            if 'key findings' in line.lower():
                in_findings = True
                continue
            if in_findings:
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                    metrics["key_findings"].append(line.strip()[3:].strip())
                elif line.startswith('##'):
                    break
        
        # Count opportunities
        in_opportunities = False
        for line in lines:
            if 'market opportunities' in line.lower() or 'opportunities' in line.lower():
                in_opportunities = True
                continue
            if in_opportunities:
                if line.strip().startswith(('1.', '2.', '3.', '-', '*')):
                    metrics["opportunities"] += 1
                elif line.startswith('##'):
                    break
                    
    except Exception as e:
        logger.error(f"Error extracting metrics: {str(e)}")
    
    return metrics


def clean_text_for_export(text: str) -> str:
    """
    Clean text for export (remove special characters, etc.)
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove non-printable characters
    text = ''.join(char for char in text if char.isprintable() or char == '\n')
    
    return text.strip()


def generate_filename(company_name: str, extension: str = "pdf") -> str:
    """
    Generate a clean filename for exports
    
    Args:
        company_name: Company name
        extension: File extension (default: pdf)
        
    Returns:
        Clean filename
    """
    # Clean company name
    clean_name = re.sub(r'[^\w\s-]', '', company_name)
    clean_name = re.sub(r'[-\s]+', '_', clean_name)
    
    # Add timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    
    filename = f"competitor_analysis_{clean_name}_{timestamp}.{extension}"
    
    return filename

