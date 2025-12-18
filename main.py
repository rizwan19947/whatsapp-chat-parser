#!/usr/bin/env python3
"""
WhatsApp Chat to PDF Converter

This script converts WhatsApp chat export text files to PDF format
while maintaining the authentic WhatsApp UI design.
"""

import argparse
import os
import sys
from parser import WhatsAppChatParser
from generator import PDFGenerator


def main():
    """Main entry point for the WhatsApp Chat to PDF converter"""

    parser = argparse.ArgumentParser(
        description='Convert WhatsApp chat exports to PDF with authentic UI design'
    )

    parser.add_argument(
        'input_file',
        help='Path to the WhatsApp chat export text file'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output PDF file path (default: same name as input with .pdf extension)',
        default=None
    )

    parser.add_argument(
        '--html-preview',
        help='Also generate an HTML preview file',
        action='store_true'
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_pdf = args.output
    else:
        base_name = os.path.splitext(args.input_file)[0]
        output_pdf = f"{base_name}.pdf"

    try:
        # Parse the chat file
        print(f"Parsing WhatsApp chat from: {args.input_file}")
        chat_parser = WhatsAppChatParser(args.input_file)
        messages = chat_parser.parse()

        if not messages:
            print("Error: No messages found in the chat file.")
            sys.exit(1)

        print(f"Found {len(messages)} messages from {len(chat_parser.get_participants())} participants")

        # Get chat info
        participants = chat_parser.get_participants()
        date_range = chat_parser.get_date_range()

        if date_range[0] and date_range[1]:
            print(f"Date range: {date_range[0].strftime('%d %B %Y')} - {date_range[1].strftime('%d %B %Y')}")

        # Generate PDF
        print(f"Generating PDF: {output_pdf}")
        pdf_gen = PDFGenerator()
        pdf_gen.generate(messages, output_pdf, participants)

        print(f"✓ PDF generated successfully: {output_pdf}")

        # Generate HTML preview if requested
        if args.html_preview:
            html_output = os.path.splitext(output_pdf)[0] + '.html'
            print(f"Generating HTML preview: {html_output}")
            pdf_gen.generate_html_preview(messages, html_output, participants)
            print(f"✓ HTML preview generated: {html_output}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
