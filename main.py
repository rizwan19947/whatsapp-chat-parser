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
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console


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

    console = Console()

    try:
        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            # Task 1: Parse the chat file
            parse_task = progress.add_task("[cyan]Parsing chat file...", total=100)

            chat_parser = WhatsAppChatParser(args.input_file)

            def parse_progress(current, total):
                percentage = int((current / total) * 100)
                progress.update(parse_task, completed=percentage)

            messages = chat_parser.parse(progress_callback=parse_progress)
            progress.update(parse_task, completed=100, description="[green]✓ Parsed chat file")

            if not messages:
                console.print("[red]Error: No messages found in the chat file.")
                sys.exit(1)

            # Get chat info
            participants = chat_parser.get_participants()
            date_range = chat_parser.get_date_range()

            console.print(f"\n[bold]Found {len(messages)} messages from {len(participants)} participants[/bold]")
            if date_range[0] and date_range[1]:
                console.print(f"Date range: {date_range[0].strftime('%d %B %Y')} - {date_range[1].strftime('%d %B %Y')}")

            # Task 2: Generate PDF
            prep_task = progress.add_task("[cyan]Preparing PDF...", total=3)

            def pdf_progress(stage):
                if stage == "template_loaded":
                    progress.update(prep_task, completed=1, description="[cyan]Templates loaded")
                elif stage == "messages_processed":
                    progress.update(prep_task, completed=2, description="[cyan]Messages processed")
                elif stage == "html_rendered":
                    progress.update(prep_task, completed=3, description="[green]✓ HTML rendered")
                elif stage == "converting_to_pdf":
                    # Add a separate task for rendering PDF pages
                    render_task = progress.add_task("[cyan]Rendering PDF pages...", total=None)
                    pdf_progress.render_task = render_task
                elif stage.startswith("pdf_pages:"):
                    # Got page count after rendering
                    pages = stage.split(":")[1]
                    if hasattr(pdf_progress, 'render_task'):
                        progress.update(pdf_progress.render_task, description=f"[green]✓ Rendered {pages} pages")
                        progress.stop_task(pdf_progress.render_task)
                    # Now add task for writing PDF
                    write_task = progress.add_task(f"[cyan]Writing PDF ({pages} pages)...", total=None)
                    pdf_progress.write_task = write_task
                elif stage == "complete":
                    # Mark writing complete
                    if hasattr(pdf_progress, 'write_task'):
                        progress.update(pdf_progress.write_task, description="[green]✓ PDF written")
                        progress.stop_task(pdf_progress.write_task)

            pdf_gen = PDFGenerator()
            pdf_gen.generate(messages, output_pdf, participants, progress_callback=pdf_progress)

            console.print(f"\n[bold green]✓ PDF generated successfully:[/bold green] {output_pdf}")

            # Generate HTML preview if requested
            if args.html_preview:
                html_output = os.path.splitext(output_pdf)[0] + '.html'
                html_task = progress.add_task("[cyan]Generating HTML preview...", total=1)
                pdf_gen.generate_html_preview(messages, html_output, participants)
                progress.update(html_task, completed=1, description="[green]✓ Generated HTML preview")
                console.print(f"[bold green]✓ HTML preview generated:[/bold green] {html_output}")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
