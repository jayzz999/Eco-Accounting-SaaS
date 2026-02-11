"""
Report generation service for GRI, CDP, and TCFD reports
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from typing import Dict, List, Optional
import io


class GRIReportGenerator:
    """Generate GRI-compliant sustainability reports"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=12,
            spaceBefore=12
        ))

        self.styles.add(ParagraphStyle(
            name='Subsection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=6,
            spaceBefore=6
        ))

    def generate_gri_305_report(
        self,
        organization_data: Dict,
        emissions_data: List[Dict],
        period_start: datetime,
        period_end: datetime,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate GRI 305 (Emissions) report

        Args:
            organization_data: Organization information
            emissions_data: List of emission records
            period_start: Reporting period start
            period_end: Reporting period end
            output_path: Optional file path to save PDF

        Returns:
            PDF content as bytes
        """
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        # Build document elements
        elements = []

        # Title page
        elements.append(Spacer(1, 2*inch))
        title = Paragraph(
            f"GRI 305: Emissions Report<br/>{period_start.year}",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))

        org_name = Paragraph(
            organization_data.get('name', 'Organization'),
            self.styles['CustomTitle']
        )
        elements.append(org_name)
        elements.append(Spacer(1, 0.5*inch))

        period_text = Paragraph(
            f"Reporting Period: {period_start.strftime('%B %d, %Y')} - {period_end.strftime('%B %d, %Y')}",
            self.styles['Normal']
        )
        elements.append(period_text)

        elements.append(PageBreak())

        # Executive Summary
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))

        # Calculate totals
        total_emissions = sum(e.get('total_co2e', 0) for e in emissions_data) / 1000  # Convert to tonnes
        scope_1 = sum(e.get('total_co2e', 0) for e in emissions_data if e.get('category') == 'Scope 1') / 1000
        scope_2 = sum(e.get('total_co2e', 0) for e in emissions_data if e.get('category') == 'Scope 2') / 1000
        scope_3 = sum(e.get('total_co2e', 0) for e in emissions_data if e.get('category') == 'Scope 3') / 1000

        summary_text = f"""
        This report presents the greenhouse gas (GHG) emissions inventory for {organization_data.get('name', 'the organization')}
        for the reporting period {period_start.strftime('%B %Y')} to {period_end.strftime('%B %Y')}.
        The report follows the GRI 305: Emissions standard and provides a comprehensive overview of the organization's carbon footprint.
        <br/><br/>
        <b>Key Findings:</b><br/>
        • Total GHG Emissions: {total_emissions:,.2f} tonnes CO2e<br/>
        • Scope 1 (Direct) Emissions: {scope_1:,.2f} tonnes CO2e<br/>
        • Scope 2 (Indirect - Energy) Emissions: {scope_2:,.2f} tonnes CO2e<br/>
        • Scope 3 (Other Indirect) Emissions: {scope_3:,.2f} tonnes CO2e
        """

        summary_para = Paragraph(summary_text, self.styles['Normal'])
        elements.append(summary_para)
        elements.append(Spacer(1, 20))

        # GRI 305-1: Direct (Scope 1) Emissions
        elements.append(Paragraph("GRI 305-1: Direct (Scope 1) GHG Emissions", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))

        scope1_text = f"""
        Scope 1 emissions are direct emissions from sources owned or controlled by the organization.
        For the reporting period, total Scope 1 emissions were <b>{scope_1:,.2f} tonnes CO2e</b>.
        <br/><br/>
        These emissions primarily come from:<br/>
        • Stationary combustion (heating, generators)<br/>
        • Mobile combustion (company vehicles)<br/>
        • Process emissions<br/>
        • Fugitive emissions
        """
        elements.append(Paragraph(scope1_text, self.styles['Normal']))
        elements.append(Spacer(1, 12))

        # Scope 1 breakdown table
        scope1_emissions = [e for e in emissions_data if e.get('category') == 'Scope 1']
        if scope1_emissions:
            scope1_table_data = [['Source Type', 'Consumption', 'CO2e (kg)', 'CO2e (tonnes)']]

            source_totals = {}
            for emission in scope1_emissions:
                source = emission.get('source_type', 'Unknown')
                co2e = emission.get('total_co2e', 0)
                consumption = emission.get('consumption_amount', 0)
                unit = emission.get('consumption_unit', '')

                if source not in source_totals:
                    source_totals[source] = {'co2e': 0, 'consumption': 0, 'unit': unit}
                source_totals[source]['co2e'] += co2e
                source_totals[source]['consumption'] += consumption

            for source, data in source_totals.items():
                scope1_table_data.append([
                    source.capitalize(),
                    f"{data['consumption']:,.2f} {data['unit']}",
                    f"{data['co2e']:,.2f}",
                    f"{data['co2e']/1000:,.2f}"
                ])

            scope1_table = Table(scope1_table_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
            scope1_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(scope1_table)
            elements.append(Spacer(1, 20))

        # GRI 305-2: Indirect (Scope 2) Emissions
        elements.append(PageBreak())
        elements.append(Paragraph("GRI 305-2: Energy Indirect (Scope 2) GHG Emissions", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))

        scope2_text = f"""
        Scope 2 emissions are indirect emissions from the generation of purchased energy consumed by the organization.
        For the reporting period, total Scope 2 emissions were <b>{scope_2:,.2f} tonnes CO2e</b>.
        <br/><br/>
        These emissions primarily come from:<br/>
        • Purchased electricity<br/>
        • Purchased heating<br/>
        • Purchased cooling<br/>
        • Purchased steam
        """
        elements.append(Paragraph(scope2_text, self.styles['Normal']))
        elements.append(Spacer(1, 12))

        # Scope 2 breakdown table
        scope2_emissions = [e for e in emissions_data if e.get('category') == 'Scope 2']
        if scope2_emissions:
            scope2_table_data = [['Source Type', 'Consumption', 'CO2e (kg)', 'CO2e (tonnes)']]

            source_totals = {}
            for emission in scope2_emissions:
                source = emission.get('source_type', 'Unknown')
                co2e = emission.get('total_co2e', 0)
                consumption = emission.get('consumption_amount', 0)
                unit = emission.get('consumption_unit', '')

                if source not in source_totals:
                    source_totals[source] = {'co2e': 0, 'consumption': 0, 'unit': unit}
                source_totals[source]['co2e'] += co2e
                source_totals[source]['consumption'] += consumption

            for source, data in source_totals.items():
                scope2_table_data.append([
                    source.capitalize(),
                    f"{data['consumption']:,.2f} {data['unit']}",
                    f"{data['co2e']:,.2f}",
                    f"{data['co2e']/1000:,.2f}"
                ])

            scope2_table = Table(scope2_table_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
            scope2_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(scope2_table)
            elements.append(Spacer(1, 20))

        # GRI 305-3: Other Indirect (Scope 3) Emissions
        if scope_3 > 0:
            elements.append(PageBreak())
            elements.append(Paragraph("GRI 305-3: Other Indirect (Scope 3) GHG Emissions", self.styles['SectionHeader']))
            elements.append(Spacer(1, 12))

            scope3_text = f"""
            Scope 3 emissions are all other indirect emissions that occur in the organization's value chain.
            For the reporting period, total Scope 3 emissions were <b>{scope_3:,.2f} tonnes CO2e</b>.
            """
            elements.append(Paragraph(scope3_text, self.styles['Normal']))
            elements.append(Spacer(1, 12))

        # Methodology
        elements.append(PageBreak())
        elements.append(Paragraph("Methodology and Assumptions", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))

        methodology_text = """
        <b>Calculation Approach:</b><br/>
        This GHG inventory follows the operational control approach as defined by the GHG Protocol.
        Emissions are calculated using the formula:<br/><br/>
        <i>Emissions (CO2e) = Activity Data × Emission Factor</i><br/><br/>

        <b>Emission Factors:</b><br/>
        Emission factors are sourced from internationally recognized databases including:<br/>
        • International Energy Agency (IEA)<br/>
        • U.S. Environmental Protection Agency (EPA)<br/>
        • UK Department for Environment, Food & Rural Affairs (DEFRA)<br/>
        • Intergovernmental Panel on Climate Change (IPCC)<br/><br/>

        <b>Gases Included:</b><br/>
        The inventory covers the seven greenhouse gases defined by the Kyoto Protocol:<br/>
        • Carbon Dioxide (CO2)<br/>
        • Methane (CH4)<br/>
        • Nitrous Oxide (N2O)<br/>
        • Hydrofluorocarbons (HFCs)<br/>
        • Perfluorocarbons (PFCs)<br/>
        • Sulphur Hexafluoride (SF6)<br/>
        • Nitrogen Trifluoride (NF3)<br/><br/>

        All emissions are converted to CO2 equivalent (CO2e) using global warming potential (GWP) values
        from the IPCC Fifth Assessment Report (AR5).
        """
        elements.append(Paragraph(methodology_text, self.styles['Normal']))

        # Build PDF
        doc.build(elements)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)

        return pdf_bytes

    def generate_gri_302_report(
        self,
        organization_data: Dict,
        energy_data: List[Dict],
        period_start: datetime,
        period_end: datetime
    ) -> bytes:
        """Generate GRI 302 (Energy) report"""
        # Similar structure to GRI 305 but focused on energy consumption
        # TODO: Implement energy-specific reporting
        pass

    def generate_gri_303_report(
        self,
        organization_data: Dict,
        water_data: List[Dict],
        period_start: datetime,
        period_end: datetime
    ) -> bytes:
        """Generate GRI 303 (Water) report"""
        # Similar structure to GRI 305 but focused on water usage
        # TODO: Implement water-specific reporting
        pass


class CDPReportGenerator:
    """Generate CDP (Carbon Disclosure Project) reports"""

    def generate_cdp_report(
        self,
        organization_data: Dict,
        emissions_data: List[Dict],
        period_start: datetime,
        period_end: datetime
    ) -> bytes:
        """Generate CDP climate change questionnaire response"""
        # TODO: Implement CDP reporting
        pass


class TCFDReportGenerator:
    """Generate TCFD (Task Force on Climate-related Financial Disclosures) reports"""

    def generate_tcfd_report(
        self,
        organization_data: Dict,
        emissions_data: List[Dict],
        risk_assessment: Dict,
        period_start: datetime,
        period_end: datetime
    ) -> bytes:
        """Generate TCFD-aligned climate risk disclosure"""
        # TODO: Implement TCFD reporting
        pass


# Factory functions
def get_gri_generator() -> GRIReportGenerator:
    """Get GRI report generator instance"""
    return GRIReportGenerator()


def get_cdp_generator() -> CDPReportGenerator:
    """Get CDP report generator instance"""
    return CDPReportGenerator()


def get_tcfd_generator() -> TCFDReportGenerator:
    """Get TCFD report generator instance"""
    return TCFDReportGenerator()


def get_report_generator() -> GRIReportGenerator:
    """Get default report generator instance (GRI)"""
    return GRIReportGenerator()
