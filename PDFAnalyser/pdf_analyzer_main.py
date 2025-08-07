import streamlit as st
import json
import io
import fitz  # PyMuPDF
import pdfplumber
from typing import Dict, List, Tuple, Any
import re
from pathlib import Path
import tempfile
import os

class PDFComplianceAnalyzer:
    """
    A comprehensive PDF compliance analyzer that validates formatting and content rules.
    """
    
    def __init__(self):
        self.required_font_size = 12
        self.required_font_family = "Times New Roman"
        self.required_margin_inches = 1.0
        self.section_limits = {
            "technical_requirements": 8,
            "budget": 4,
            "qualification": 4
        }
        
    def validate_pdf_format(self, file_bytes: bytes) -> bool:
        """Validate if the uploaded file is a valid PDF."""
        try:
            # Try to open with PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            doc.close()
            return True
        except Exception:
            try:
                # Try with pdfplumber as backup
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    return len(pdf.pages) > 0
            except Exception:
                return False
    
    def extract_font_info(self, file_bytes: bytes) -> Dict[str, Any]:
        """Extract font information from PDF."""
        font_sizes = set()
        font_families = set()
        
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                font_sizes.add(round(span["size"]))
                                font_families.add(span["font"])
            
            doc.close()
            
        except Exception as e:
            st.error(f"Error extracting font info: {str(e)}")
            return {"font_sizes": set(), "font_families": set()}
        
        return {"font_sizes": font_sizes, "font_families": font_families}
    
    def extract_margin_info(self, file_bytes: bytes) -> Dict[str, float]:
        """Extract margin information from PDF."""
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                if pdf.pages:
                    page = pdf.pages[0]  # Check first page
                    
                    # Get page dimensions
                    page_width = page.width
                    page_height = page.height
                    
                    # Get text bounding box
                    if page.chars:
                        chars = page.chars
                        min_x = min(char['x0'] for char in chars)
                        max_x = max(char['x1'] for char in chars)
                        min_y = min(char['top'] for char in chars)
                        max_y = max(char['bottom'] for char in chars)
                        
                        # Convert points to inches (72 points = 1 inch)
                        left_margin = min_x / 72
                        right_margin = (page_width - max_x) / 72
                        top_margin = min_y / 72
                        bottom_margin = (page_height - max_y) / 72
                        
                        return {
                            "left": left_margin,
                            "right": right_margin,
                            "top": top_margin,
                            "bottom": bottom_margin
                        }
        except Exception as e:
            st.error(f"Error extracting margin info: {str(e)}")
        
        return {"left": 0, "right": 0, "top": 0, "bottom": 0}
    
    def detect_sections(self, file_bytes: bytes) -> Dict[str, List[int]]:
        """Detect sections in the PDF using keyword matching."""
        sections = {
            "technical_requirements": [],
            "budget": [],
            "qualification": []
        }
        
        # Keywords for section detection
        section_keywords = {
            "technical_requirements": [
                r"technical\s+requirements?",
                r"technical\s+specifications?",
                r"system\s+requirements?",
                r"technical\s+details"
            ],
            "budget": [
                r"budget",
                r"financial",
                r"cost",
                r"pricing",
                r"expenses?"
            ],
            "qualification": [
                r"qualifications?",
                r"credentials?",
                r"experience",
                r"expertise",
                r"competenc"
            ]
        }
        
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_lower = text.lower()
                        
                        for section_name, keywords in section_keywords.items():
                            for keyword_pattern in keywords:
                                if re.search(keyword_pattern, text_lower):
                                    if page_num not in sections[section_name]:
                                        sections[section_name].append(page_num)
                                    break
        except Exception as e:
            st.error(f"Error detecting sections: {str(e)}")
        
        return sections
    
    def validate_formatting(self, file_bytes: bytes) -> Dict[str, str]:
        """Validate PDF formatting requirements."""
        results = {
            "file_type": "fail",
            "font_size": "fail",
            "font_family": "fail",
            "margin": "fail"
        }
        
        # Validate file type
        if self.validate_pdf_format(file_bytes):
            results["file_type"] = "pass"
        else:
            return results  # If not a valid PDF, return early
        
        # Validate font information
        font_info = self.extract_font_info(file_bytes)
        
        # Check font size (allowing some tolerance)
        if font_info["font_sizes"]:
            if any(abs(size - self.required_font_size) <= 1 for size in font_info["font_sizes"]):
                results["font_size"] = "pass"
        
        # Check font family
        if font_info["font_families"]:
            times_variants = ["Times", "Times-Roman", "TimesNewRoman", "Times New Roman"]
            if any(any(variant.lower() in font.lower() for variant in times_variants) 
                   for font in font_info["font_families"]):
                results["font_family"] = "pass"
        
        # Validate margins
        margins = self.extract_margin_info(file_bytes)
        margin_tolerance = 0.2  # Allow 0.2 inch tolerance
        
        if all(abs(margin - self.required_margin_inches) <= margin_tolerance 
               for margin in margins.values()):
            results["margin"] = "pass"
        
        return results
    
    def validate_content(self, file_bytes: bytes) -> Dict[str, Any]:
        """Validate content section requirements."""
        sections = self.detect_sections(file_bytes)
        
        results = {}
        
        for section_name, limit in self.section_limits.items():
            pages = sections.get(section_name, [])
            page_count = len(pages) if pages else 0
            
            results[f"{section_name}_pages"] = page_count
            results[section_name] = "pass" if page_count <= limit else "fail"
        
        return results
    
    def analyze(self, file_bytes: bytes) -> Dict[str, Any]:
        """Perform complete PDF compliance analysis."""
        format_results = self.validate_formatting(file_bytes)
        content_results = self.validate_content(file_bytes)
        
        return {
            "format": format_results,
            "content": content_results
        }

def main():
    st.set_page_config(
        page_title="PDF Compliance Analyzer",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 PDF Compliance Analyzer")
    st.markdown("---")
    
    st.markdown("""
    ## Upload a PDF document to validate compliance with formatting and content rules
    
    **Formatting Requirements:**
    - Font Size: 12px
    - Font Family: Times New Roman
    - Margins: 1 inch on all sides
    
    **Content Requirements:**
    - Technical Requirements: Maximum 8 pages
    - Budget: Maximum 4 pages
    - Qualification: Maximum 4 pages
    """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document for compliance analysis"
    )
    
    if uploaded_file is not None:
        # Read file bytes
        file_bytes = uploaded_file.read()
        
        # Initialize analyzer
        analyzer = PDFComplianceAnalyzer()
        
        with st.spinner("Analyzing PDF compliance..."):
            try:
                # Perform analysis
                results = analyzer.analyze(file_bytes)
                
                # Display results
                st.success("Analysis completed!")
                
                # Format validation results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 Format Validation")
                    format_results = results["format"]
                    
                    for check, status in format_results.items():
                        icon = "✅" if status == "pass" else "❌"
                        check_name = check.replace("_", " ").title()
                        st.write(f"{icon} **{check_name}**: {status}")
                
                with col2:
                    st.subheader("📖 Content Validation")
                    content_results = results["content"]
                    
                    sections = ["technical_requirements", "budget", "qualification"]
                    for section in sections:
                        pages = content_results.get(f"{section}_pages", 0)
                        status = content_results.get(section, "fail")
                        limit = analyzer.section_limits[section]
                        
                        icon = "✅" if status == "pass" else "❌"
                        section_name = section.replace("_", " ").title()
                        st.write(f"{icon} **{section_name}**: {pages}/{limit} pages ({status})")
                
                # JSON output
                st.subheader("📄 Detailed Report")
                
                # Create downloadable JSON report
                json_report = json.dumps(results, indent=2)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.code(json_report, language="json")
                
                with col2:
                    st.download_button(
                        label="📥 Download Report",
                        data=json_report,
                        file_name=f"compliance_report_{uploaded_file.name}.json",
                        mime="application/json"
                    )
                
                # Summary
                format_passes = sum(1 for v in format_results.values() if v == "pass")
                content_passes = sum(1 for k, v in content_results.items() 
                                   if not k.endswith("_pages") and v == "pass")
                
                total_checks = len(format_results) + len([k for k in content_results.keys() 
                                                        if not k.endswith("_pages")])
                total_passes = format_passes + content_passes
                
                if total_passes == total_checks:
                    st.success(f"🎉 All {total_checks} compliance checks passed!")
                else:
                    st.warning(f"⚠️ {total_passes}/{total_checks} compliance checks passed. Please review the failed items.")
                
            except Exception as e:
                st.error(f"Error analyzing PDF: {str(e)}")
                st.info("Please ensure you've uploaded a valid PDF file.")
    
    # Instructions
    st.markdown("---")
    st.markdown("""
    ### Instructions for Use:
    1. Upload a PDF document using the file uploader above
    2. Wait for the analysis to complete
    3. Review the format and content validation results
    4. Download the detailed JSON report if needed
    
    ### Notes:
    - The analyzer uses OCR and metadata extraction for formatting validation
    - Section detection is based on keyword matching
    - Some tolerance is applied to measurements (±0.2 inches for margins, ±1px for font size)
    """)

if __name__ == "__main__":
    main()