# Changelog

All notable changes to NexPro PDF will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Forms creation and editing
- Digital signature support (Indian DSC)
- Bates numbering
- Advanced page numbering
- Auto-update functionality
- Performance optimization for 500+ page PDFs

## [1.0.0] - 2024-01-27

### Added - Core Features (Phase 1 MVP)

#### User Interface
- Professional MS Office-style ribbon interface
- Three-panel layout (left thumbnails/bookmarks, center viewer, right properties)
- Tab-based navigation (File, Edit, Pages, Security, Redaction, Forms, Signature, Tools, Help)
- PDF viewer with zoom controls and page navigation
- Responsive and clean UI design

#### PDF Creation & Conversion
- Create PDF from Word documents (.docx)
- Create PDF from Excel spreadsheets (.xlsx)
- Create PDF from PowerPoint presentations (.pptx)
- Create PDF from images (JPG, PNG)
- Batch conversion support
- Create blank PDFs
- PDF/A conversion for archival

#### PDF Editing
- View and navigate PDFs
- Add text to PDFs
- Add images to PDFs
- Insert blank pages
- Delete pages
- Reorder pages (move pages)
- Rotate pages (90, 180, 270 degrees)
- Extract text from pages
- Search text across documents

#### PDF Operations
- Merge multiple PDFs into one
- Split PDFs by:
  - Page range
  - File size
  - Number of pages per file
- Extract specific pages to new PDF
- Get and set PDF metadata
- Manage table of contents (bookmarks)

#### Redaction (Critical Module)
- Manual redaction (draw box over content)
- Text-based redaction (redact specific text)
- Pattern-based redaction for Indian documents:
  - PAN numbers (format: XXXXX9999X)
  - Aadhaar numbers (format: 9999 9999 9999)
  - GSTIN numbers
  - Bank account numbers
- Search and redact multiple terms
- Metadata removal
- Flattening for irreversible redactions
- Redaction verification

#### Security & Protection
- AES-256 encryption
- Password protection:
  - User password (for opening PDF)
  - Owner password (for editing/permissions)
- Permission controls:
  - Print permission
  - Copy content permission
  - Modify permission
  - Annotate permission
- Remove password protection
- View security information
- Text watermarks with customizable:
  - Opacity
  - Font size
  - Color
  - Rotation
- Image watermarks with position control

#### Licensing System
- Hardware-bound licensing
- Annual subscription model
- Online license activation
- Server-based validation
- Offline grace period (7 days)
- Encrypted license storage
- Hardware ID generation
- License expiry handling
- Validation logging and audit trail

#### System Features
- Comprehensive logging system
- Configuration management (YAML)
- SQLite database for local storage
- Error handling and recovery
- Professional color scheme (Blue/Slate/Grey with Green accents)
- Application settings management

#### Documentation
- README.md with comprehensive information
- QUICKSTART.md for new users
- DEVELOPMENT.md for developers
- LICENSE.txt with legal terms
- CHANGELOG.md for version tracking

#### Packaging & Distribution
- PyInstaller configuration for .exe creation
- Windows batch scripts for easy setup and launch
- .gitignore for version control
- Project structure following best practices

### Technical Implementation
- Python 3.11+ codebase
- PyQt6 for modern UI
- PyMuPDF (fitz) as primary PDF engine
- pikepdf for advanced PDF operations
- Pillow for image processing
- cryptography for encryption
- pywin32 for Windows integration (Office conversion)
- Modular architecture with clear separation of concerns

### Compliance
- ISO 32000 (PDF specification) compliant
- Indian IT Act, 2000 compliance
- DPDP Act, 2023 (Data Protection) compliant
- Privacy-first design (all processing local)
- No cloud dependency for document processing

### Security Features
- No AI features (as per requirement)
- No OCR capabilities (as per requirement)
- Offline-first operation
- Local document processing only
- Secure license validation
- Encrypted sensitive data storage

## [0.1.0] - Development Phase

### Initial Setup
- Project structure created
- Core modules implemented
- Basic UI framework established

---

## Version Numbering

- **Major version** (X.0.0): Significant changes, major new features
- **Minor version** (1.X.0): New features, improvements
- **Patch version** (1.0.X): Bug fixes, small improvements

## Release Types

- **MVP**: Minimum Viable Product (Phase 1)
- **Feature Release**: New functionality added (Phase 2, 3)
- **Maintenance Release**: Bug fixes and improvements
- **Security Release**: Security updates and fixes

---

For support or questions about releases:
- Email: support@nexpro.com
- Documentation: README.md
