# NexPro PDF - Quick Start Guide

## Installation & Setup

### 1. Install Python 3.11+
Download from: https://www.python.org/downloads/

### 2. Install Dependencies
```bash
cd "d:\CTPL\NexPro PDF"
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python main.py
```

## First Launch

On first launch, you'll be prompted for a license key. For development/testing, the system accepts any key in the format: `XXXX-XXXX-XXXX-XXXX`

## Basic Operations

### Opening a PDF
- **File → Open** (Ctrl+O)
- Browse and select your PDF file

### Creating PDFs

#### From Images
1. Click **File** tab in ribbon
2. Click **From Images**
3. Select image files (JPG, PNG)
4. Choose output location

#### From Office Documents
1. Requires Microsoft Office or LibreOffice installed
2. Click **File** tab
3. Choose **From Word**, **From Excel**, or **From PPT**
4. Select document
5. PDF will be created automatically

### Editing PDFs

#### Edit Text
1. Click **Edit** tab
2. Click **Edit Text**
3. Click on text to edit
4. Make changes

#### Add Text Box
1. Click **Edit** tab
2. Click **Add Text**
3. Draw text box on page
4. Type your text

### Redacting Sensitive Information

#### Manual Redaction
1. Click **Redaction** tab
2. Click **Manual**
3. Draw box over content to redact
4. Click **Apply** (WARNING: Irreversible!)

#### Pattern-Based Redaction
1. Click **Redaction** tab
2. Choose pattern:
   - **PAN**: Redacts PAN numbers (XXXXX9999X)
   - **Aadhaar**: Redacts Aadhaar numbers (9999 9999 9999)
   - **GSTIN**: Redacts GST numbers
   - **Bank Acc**: Redacts bank account numbers
3. Click **Apply**

### Security Operations

#### Add Password
1. Click **Security** tab
2. Click **Password**
3. Enter user password (for opening)
4. Enter owner password (for editing) [optional]
5. Click OK

#### Encrypt PDF
1. Click **Security** tab
2. Click **Encrypt**
3. Choose encryption settings
4. Set permissions
5. Click OK

#### Add Watermark
1. Click **Security** tab
2. Click **Watermark**
3. Enter watermark text
4. Set opacity and position
5. Click Apply

### Page Operations

#### Merge PDFs
1. Click **Pages** tab
2. Click **Merge**
3. Select PDFs to merge
4. Choose output location
5. Click Merge

#### Split PDF
1. Open PDF
2. Click **Pages** tab
3. Click **Split**
4. Choose split method:
   - By page range
   - By file size
   - By bookmarks
5. Set parameters
6. Click Split

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New | Ctrl+N |
| Open | Ctrl+O |
| Save | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Copy | Ctrl+C |
| Paste | Ctrl+V |
| Zoom In | Ctrl++ |
| Zoom Out | Ctrl+- |
| Fit Page | Ctrl+0 |
| Exit | Alt+F4 |

## Navigation

### PDF Viewer Controls
- **Previous/Next Page**: Use buttons or arrow keys
- **Zoom**: Use dropdown or +/- buttons
- **Fit Page**: Makes entire page visible
- **Fit Width**: Fits page width to window

### Panels
- **Left Panel**:
  - Thumbnails: Page previews
  - Bookmarks: Document outline
  - Layers: PDF layers
  - Attachments: Embedded files

- **Right Panel**:
  - Properties: Document metadata
  - Format: Text and page formatting
  - Security: Security status and permissions

## Tips for Professional Use

### For Chartered Accountants & CS
1. Use **Pattern Redaction** for PAN/Aadhaar/GSTIN
2. Add **Watermarks** for draft documents
3. Use **Password Protection** for sensitive reports
4. **Merge** multiple statements/reports for filing

### For Legal Professionals
1. **Redact** confidential information permanently
2. **Add Bates Numbering** for discovery documents
3. **Digital Signatures** for authentication
4. **Encrypt** sensitive legal documents

### For Compliance Teams
1. **Remove Metadata** before sharing
2. **Set Permissions** to prevent unauthorized copying
3. **PDF/A Conversion** for long-term archival
4. **Audit Trail** for document handling

## Troubleshooting

### PDF Won't Open
- Check if file is corrupted
- Verify file is a valid PDF
- Check if password-protected

### Can't Edit Text
- PDF may be image-based (requires OCR - not available)
- PDF may be protected
- Use "Add Text Box" instead

### License Validation Failed
- Check internet connection
- Verify license key format
- Contact support if issue persists
- App continues in read-only mode after grace period

### Office Conversion Not Working
- Install Microsoft Office or LibreOffice
- Check file format compatibility
- Ensure file is not corrupted

## Support

For additional help:
- Email: support@nexpro.com
- Documentation: See [README.md](README.md)
- Logs: Check `logs/` directory for error details

## Important Reminders

⚠️ **Redactions are permanent** - Cannot be undone after applying
⚠️ **Always backup** important files before editing
⚠️ **Test redactions** on copies first
⚠️ **Verify security** settings before sharing sensitive documents

---

**Happy PDF Editing!**
