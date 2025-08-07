# PDF Compliance Analyzer

A comprehensive document analyzer that validates uploaded PDF files against predefined formatting and content rules. This tool is designed for organizations that need to automatically verify proposal documents against strict formatting guidelines.

## Features

### Format Validation
- ✅ PDF file format verification
- ✅ Font size validation (12px requirement)
- ✅ Font family validation (Times New Roman requirement)
- ✅ Margin validation (1 inch on all sides)

### Content Validation
- ✅ Section detection using keyword matching
- ✅ Page count validation for each section:
  - Technical Requirements: Max 8 pages
  - Budget: Max 4 pages
  - Qualification: Max 4 pages

### Additional Features
- 🌐 Web interface using Streamlit
- 📥 Downloadable JSON compliance reports
- 📊 Visual validation results
- 🎯 Tolerance-based validation (allows minor deviations)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or download the project files**
   ```bash
   # Create a new directory for the project
   mkdir pdf-compliance-analyzer
   cd pdf-compliance-analyzer
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run pdf_analyzer.py
   ```

5. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:8501`
   - Upload a PDF file for analysis

## Usage Instructions

### Web Interface
1. Start the application using `streamlit run pdf_analyzer.py`
2. Open the web interface in your browser
3. Upload a PDF file using the file uploader
4. Wait for the analysis to complete
5. Review the validation results:
   - **Format Validation**: Shows pass/fail for formatting requirements
   - **Content Validation**: Shows page counts and compliance for each section
6. Download the detailed JSON report if needed

### Programmatic Usage
```python
from pdf_analyzer import PDFComplianceAnalyzer

# Initialize analyzer
analyzer = PDFComplianceAnalyzer()

# Read PDF file
with open('document.pdf', 'rb') as f:
    file_bytes = f.read()

# Perform analysis
results = analyzer.analyze(file_bytes)

# Print results
import json
print(json.dumps(results, indent=2))
```

## Validation Rules

### Format Requirements
| Rule | Requirement | Tolerance |
|------|-------------|-----------|
| File Type | Valid PDF | None |
| Font Size | 12px | ±1px |
| Font Family | Times New Roman | Variants accepted |
| Margins | 1 inch all sides | ±0.2 inches |

### Content Requirements
| Section | Max Pages |
|---------|-----------|
| Technical Requirements | 8 |
| Budget | 4 |
| Qualification | 4 |

## Technical Implementation

### Libraries Used
- **PyMuPDF (fitz)**: Font and metadata extraction
- **pdfplumber**: Text extraction and margin analysis
- **Streamlit**: Web interface
- **PyPDF2**: Backup PDF processing
- **pytesseract**: OCR capability (optional)

### Analysis Process
1. **File Validation**: Verify PDF format using multiple parsers
2. **Font Analysis**: Extract font information from all text spans
3. **Margin Calculation**: Analyze text positioning to determine margins
4. **Section Detection**: Use regex patterns to identify sections
5. **Report Generation**: Compile results into structured JSON output

## Sample Output

```json
{
  "format": {
    "file_type": "pass",
    "font_size": "fail",
    "font_family": "pass",
    "margin": "pass"
  },
  "content": {
    "technical_requirements_pages": 9,
    "technical_requirements": "fail",
    "budget_pages": 3,
    "budget": "pass",
    "qualification_pages": 4,
    "qualification": "pass"
  }
}
```

## Assumptions Made

### Font Detection
- Font size tolerance of ±1px to account for PDF rendering variations
- Times New Roman variants (Times, Times-Roman, TimesNewRoman) are accepted
- Analysis based on the majority font used in the document

### Margin Calculation
- Margins calculated from the outermost text boundaries
- 0.2-inch tolerance applied to account for minor formatting variations
- Based on the first page analysis (representative sample)

### Section Detection
- Keyword-based detection using regex patterns
- Case-insensitive matching
- Pages containing section keywords are counted toward that section
- Multiple sections can exist on the same page

### Content Validation
- Page counting based on keyword presence
- Sections without detected keywords show 0 pages
- Maximum page limits are strictly enforced (no tolerance)

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all requirements are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **PDF parsing errors**: The tool uses multiple PDF parsers for compatibility
   - PyMuPDF for font extraction
   - pdfplumber for text and margin analysis
   - PyPDF2 as fallback

3. **Section not detected**: Check if section headers contain the expected keywords:
   - Technical Requirements: "technical requirements", "specifications", "system requirements"
   - Budget: "budget", "financial", "cost", "pricing"
   - Qualification: "qualifications", "credentials", "experience"

4. **Font detection issues**: 
   - Embedded fonts may show different names
   - Scanned PDFs require OCR (may need additional setup)

### Performance Notes
- Large PDFs may take longer to process
- OCR processing (if needed) can be memory-intensive
- Web interface includes progress indicators for long operations

## Contributing

This tool can be extended with:
- Additional validation rules
- More sophisticated section detection using NLP/LLM
- Support for other document formats
- Batch processing capabilities
- Integration with document management systems

## License

This project is provided as-is for educational and evaluation purposes.