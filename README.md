# WhatsApp Chat to PDF Converter

Convert WhatsApp chat exports to beautifully formatted PDFs with authentic WhatsApp UI design.

## Features

- Authentic WhatsApp UI design with message bubbles, colors, and styling
- Support for system messages (encryption notices, group events, etc.)
- Date separators for easy navigation
- Multi-line message support
- Automatic participant detection and color-coding
- HTML preview option for debugging

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

Note: WeasyPrint requires some system dependencies. On Ubuntu/Debian:

```bash
sudo apt-get install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

On macOS:

```bash
brew install python3 pango
```

For other platforms, see [WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation).

## Usage

### Basic Usage

```bash
python main.py path/to/your/chat.txt
```

This will create a PDF file with the same name as your input file.

### Specify Output File

```bash
python main.py path/to/your/chat.txt -o output.pdf
```

### Generate HTML Preview

```bash
python main.py path/to/your/chat.txt --html-preview
```

This creates both a PDF and an HTML file for previewing in a browser.

## Example

Try the included sample:

```bash
python main.py samples/sample_chat.txt --html-preview
```

This will generate:
- `samples/sample_chat.pdf` - The PDF output
- `samples/sample_chat.html` - HTML preview (if --html-preview flag used)

## How to Export WhatsApp Chats

### On Android:
1. Open the chat you want to export
2. Tap the three dots menu (⋮) → More → Export chat
3. Choose "Without Media"
4. Save the .txt file

### On iPhone:
1. Open the chat you want to export
2. Tap the contact/group name at the top
3. Scroll down and tap "Export Chat"
4. Choose "Without Media"
5. Save the .txt file

## Project Structure

```
whatsapp-chat-to-pdf/
├── parser/              # WhatsApp chat parsing logic
│   ├── __init__.py
│   └── parser.py        # Parser implementation
├── generator/           # PDF generation logic
│   ├── __init__.py
│   └── pdf_generator.py # PDF generator using WeasyPrint
├── templates/           # HTML templates
│   └── chat.html        # Jinja2 template for chat rendering
├── styles/              # CSS styling
│   └── whatsapp.css     # WhatsApp-style CSS
├── samples/             # Sample chat files
│   └── sample_chat.txt  # Example chat export
├── main.py              # Main entry point
└── requirements.txt     # Python dependencies
```

## Customization

### Modifying the Design

Edit `styles/whatsapp.css` to customize:
- Colors and backgrounds
- Message bubble styling
- Fonts and spacing
- Header and footer appearance

### Modifying the Template

Edit `templates/chat.html` to change:
- Layout structure
- Information displayed in header/footer
- Date format and separators

## Supported Message Format

The parser supports the standard WhatsApp export format:

```
[DD/MM/YYYY, HH:MM:SS] Sender Name: Message content
```

Multi-line messages and system messages are automatically detected and handled.

## License

This project is open source and available for personal and educational use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
