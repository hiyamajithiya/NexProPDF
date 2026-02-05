# NexPro PDF - Development Guide

## Project Architecture

### Technology Stack
- **Python 3.11+**: Core language
- **PyQt6**: UI framework
- **PyMuPDF (fitz)**: Primary PDF engine
- **pikepdf**: Secondary PDF operations
- **cryptography**: Encryption and security
- **SQLite**: Local data storage

### Module Structure

```
src/
├── ui/                     # User Interface
│   ├── main_window.py     # Main application window
│   ├── ribbon.py          # Ribbon toolbar (MS Office style)
│   ├── pdf_viewer.py      # PDF viewing and rendering
│   ├── left_panel.py      # Thumbnails, bookmarks, etc.
│   └── right_panel.py     # Properties, formatting, security
│
├── pdf_engine/            # PDF Processing
│   ├── pdf_core.py        # Core PDF operations
│   ├── pdf_creator.py     # PDF creation from various formats
│   └── pdf_merger.py      # Merge and split operations
│
├── security/              # Security Features
│   ├── pdf_security.py    # Encryption, passwords, permissions
│   └── pdf_redaction.py   # Redaction operations
│
├── licensing/             # License Management
│   └── license_manager.py # Subscription licensing
│
└── utilities/             # Utilities
    ├── logger.py          # Logging system
    └── config_manager.py  # Configuration management
```

## Development Setup

### Prerequisites
1. Python 3.11 or higher
2. Git
3. Visual Studio Code (recommended) or any Python IDE

### Setup Development Environment

```bash
# Clone repository
cd "d:\CTPL\NexPro PDF"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black pylint mypy
```

### Running in Development Mode

```bash
# Run application
python main.py

# Run with debug logging
python main.py --debug

# Check logs
tail -f logs/nexpro_pdf_*.log
```

## Code Guidelines

### Python Style
- Follow **PEP 8** style guide
- Use **type hints** for function parameters and returns
- Maximum line length: 100 characters
- Use **docstrings** for all classes and functions

Example:
```python
def merge_pdfs(self, input_files: List[str], output_file: str) -> bool:
    """
    Merge multiple PDF files into one

    Args:
        input_files: List of input PDF file paths
        output_file: Output PDF file path

    Returns:
        True if successful, False otherwise
    """
    # Implementation
    pass
```

### Naming Conventions
- **Classes**: PascalCase (`PDFCore`, `LicenseManager`)
- **Functions/Methods**: snake_case (`merge_pdfs`, `get_metadata`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_FILE_SIZE`, `DEFAULT_ZOOM`)
- **Private methods**: `_prefix` (`_validate_key`, `_encrypt_data`)

### Error Handling
Always use try-except blocks and log errors:

```python
try:
    # Operation
    result = some_operation()
    self.logger.info("Operation successful")
    return result
except Exception as e:
    self.logger.error(f"Error in operation: {e}")
    return None
```

### Logging
Use the logger consistently:

```python
from src.utilities.logger import get_logger

class MyClass:
    def __init__(self):
        self.logger = get_logger()

    def my_method(self):
        self.logger.info("Starting operation")
        self.logger.warning("This is a warning")
        self.logger.error("This is an error")
        self.logger.debug("Debug information")
```

## Adding New Features

### 1. UI Components

To add a new ribbon tab:

```python
# In src/ui/ribbon.py

def _create_my_tab_tools(self):
    """Create My Tab tools"""
    self._clear_tool_area()

    # Add buttons
    my_btn = self._create_tool_button("My Tool", "Tool description")
    my_btn.clicked.connect(self.on_my_tool_clicked)

    self.tool_layout.addWidget(my_btn)
    self.tool_layout.addStretch()

def on_my_tool_clicked(self):
    """Handle button click"""
    # Your implementation
    pass
```

### 2. PDF Operations

To add a new PDF operation:

```python
# In src/pdf_engine/pdf_core.py or create new module

def my_pdf_operation(self, input_file: str, params: Dict) -> bool:
    """
    New PDF operation

    Args:
        input_file: Input PDF path
        params: Operation parameters

    Returns:
        True if successful
    """
    try:
        pdf = fitz.open(input_file)

        # Your operation here
        for page in pdf:
            # Process page
            pass

        pdf.save(output_file)
        pdf.close()

        self.logger.info("Operation completed")
        return True

    except Exception as e:
        self.logger.error(f"Error: {e}")
        return False
```

### 3. Security Features

For security-related features, always:
1. Use proper encryption (AES-256)
2. Verify operations are irreversible when needed
3. Log all security operations
4. Test thoroughly with sensitive data

## Testing

### Unit Tests

Create tests in `tests/` directory:

```python
import pytest
from src.pdf_engine.pdf_core import PDFCore

def test_open_pdf():
    """Test PDF opening"""
    core = PDFCore()
    assert core.open("test.pdf") == True
    assert core.get_page_count() > 0

def test_merge_pdfs():
    """Test PDF merging"""
    from src.pdf_engine.pdf_merger import PDFMerger
    merger = PDFMerger()

    result = merger.merge_pdfs(
        ["test1.pdf", "test2.pdf"],
        "output.pdf"
    )

    assert result == True
```

Run tests:
```bash
pytest tests/
pytest tests/ -v  # Verbose
pytest tests/ --cov=src  # With coverage
```

### Manual Testing Checklist

#### PDF Operations
- [ ] Open various PDF files
- [ ] Create PDF from Word/Excel/PowerPoint
- [ ] Create PDF from images
- [ ] Merge multiple PDFs
- [ ] Split PDF by range/size
- [ ] Edit text in PDF
- [ ] Add images to PDF
- [ ] Rotate/crop pages

#### Redaction
- [ ] Manual redaction
- [ ] Text-based redaction
- [ ] Pattern redaction (PAN/Aadhaar/GSTIN/Bank)
- [ ] Verify redacted content is removed
- [ ] Metadata removal

#### Security
- [ ] Password protection
- [ ] AES-256 encryption
- [ ] Permission controls
- [ ] Text watermark
- [ ] Image watermark

#### Licensing
- [ ] License activation (online)
- [ ] License validation
- [ ] Offline grace period
- [ ] Hardware ID binding
- [ ] License expiry handling

## Building & Deployment

### Building Executable

```bash
# Build with PyInstaller
pyinstaller NexProPDF.spec

# Output will be in dist/NexProPDF/
```

### Creating Installer

Use **Inno Setup** or **NSIS** to create installer:

1. Install Inno Setup
2. Create installer script
3. Include:
   - Executable
   - Dependencies
   - Desktop shortcut
   - Start menu entry
   - Uninstaller

### Version Management

Update version in:
- `src/__init__.py`
- `config/config.yaml`
- `README.md`
- Version info file for executable

## Performance Optimization

### Large PDF Handling

For PDFs with 500+ pages:

1. **Lazy Loading**: Load pages on demand
```python
def render_page(self, page_num):
    # Only render when needed
    if page_num != self.current_page:
        self.current_page = page_num
        self._render()
```

2. **Caching**: Cache rendered pages
```python
self.page_cache = {}  # page_num: QPixmap

def get_page(self, page_num):
    if page_num not in self.page_cache:
        self.page_cache[page_num] = self._render_page(page_num)
    return self.page_cache[page_num]
```

3. **Background Workers**: Use threads for heavy operations
```python
from PyQt6.QtCore import QThread

class PDFWorker(QThread):
    def run(self):
        # Heavy operation
        pass

worker = PDFWorker()
worker.start()
```

### Memory Management

```python
# Clear cache periodically
if len(self.page_cache) > 50:
    self.page_cache.clear()

# Close documents when done
pdf.close()
```

## Security Considerations

### Code Obfuscation

For licensing protection:
```bash
pip install pyarmor
pyarmor gen --obf-code 1 main.py
```

### Secure Storage

- Use Fernet encryption for sensitive data
- Never store passwords in plain text
- Use hardware-bound licensing

### Data Privacy

- All processing must be local
- No network calls except license validation
- Clear temporary files after operations
- Secure deletion of sensitive data

## Common Issues & Solutions

### Issue: PyMuPDF not found
```bash
pip uninstall pymupdf
pip install pymupdf
```

### Issue: PyQt6 import error
```bash
pip install PyQt6 --upgrade
```

### Issue: Win32com not available
Install pywin32:
```bash
pip install pywin32
```

### Issue: Build fails with PyInstaller
Clear build directories:
```bash
rmdir /s build dist
pyinstaller --clean NexProPDF.spec
```

## Contributing

### Workflow

1. Create feature branch
```bash
git checkout -b feature/my-feature
```

2. Make changes and commit
```bash
git add .
git commit -m "Add: Description of changes"
```

3. Push and create pull request
```bash
git push origin feature/my-feature
```

### Commit Message Format

- **Add**: New feature
- **Fix**: Bug fix
- **Update**: Update existing feature
- **Refactor**: Code refactoring
- **Docs**: Documentation changes
- **Test**: Test additions/changes

Example:
```
Add: Pattern-based redaction for GSTIN numbers
Fix: PDF merge causing memory leak
Update: Improve encryption performance
```

## Resources

### Documentation
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [pikepdf Documentation](https://pikepdf.readthedocs.io/)

### PDF Standards
- [ISO 32000 (PDF Specification)](https://www.iso.org/standard/51502.html)
- [PDF/A Standard](https://en.wikipedia.org/wiki/PDF/A)

### Indian Regulations
- [IT Act 2000](https://www.meity.gov.in/content/information-technology-act-2000)
- [DPDP Act 2023](https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf)

## Support

For development questions:
- Email: dev@nexpro.com
- Internal Wiki: [Link to wiki]

---

**Happy Coding!**
