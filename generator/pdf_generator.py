import os
from typing import List, Callable, Optional
from jinja2 import Template
from weasyprint import HTML, CSS
from weasyprint.document import Document
from parser.parser import WhatsAppMessage


class PDFGenerator:
    """Generate PDF from WhatsApp messages using HTML/CSS"""

    def __init__(self, template_path: str = None, css_path: str = None):
        """
        Initialize PDF generator with template and CSS paths

        Args:
            template_path: Path to HTML template file
            css_path: Path to CSS file
        """
        # Set default paths relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.template_path = template_path or os.path.join(
            project_root, 'templates', 'chat.html'
        )
        self.css_path = css_path or os.path.join(
            project_root, 'styles', 'whatsapp.css'
        )


    def generate(
        self,
        messages: List[WhatsAppMessage],
        output_path: str,
        participants: List[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Generate PDF from messages

        Args:
            messages: List of WhatsAppMessage objects
            output_path: Path where PDF should be saved
            participants: Optional list of participant names
            progress_callback: Optional callback function(stage) for progress reporting
        """
        # Read template and CSS
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        if progress_callback:
            progress_callback("template_loaded")

        # Create sender mapping (first sender = 0, others get incremental indices)
        sender_map = {}
        if participants:
            for idx, participant in enumerate(participants):
                sender_map[participant] = idx
        else:
            # Auto-detect from messages
            unique_senders = []
            for msg in messages:
                if not msg.is_system and msg.sender not in unique_senders:
                    unique_senders.append(msg.sender)
            for idx, sender in enumerate(unique_senders):
                sender_map[sender] = idx

        # Get date range
        date_range = None
        if messages:
            timestamps = [msg.timestamp for msg in messages if not msg.is_system]
            if timestamps:
                date_range = (min(timestamps), max(timestamps))

        if progress_callback:
            progress_callback("messages_processed")

        # Prepare template data
        template_data = {
            'css_content': css_content,
            'messages': messages,
            'participants': participants or list(sender_map.keys()),
            'sender_map': sender_map,
            'message_count': len([m for m in messages if not m.is_system]),
            'date_range': date_range
        }

        # Render template
        template = Template(template_content)
        html_content = template.render(**template_data)

        if progress_callback:
            progress_callback("html_rendered")

        # Generate PDF with page-by-page progress tracking
        if progress_callback:
            progress_callback("converting_to_pdf")

        # First, render the document to get page count
        html_doc = HTML(string=html_content)
        document = html_doc.render()

        total_pages = len(document.pages)

        if progress_callback:
            progress_callback(f"pdf_pages:{total_pages}")

        # Now write PDF with progress tracking for each page
        # We'll use a custom approach by writing the document
        with open(output_path, 'wb') as pdf_file:
            # Write the rendered document to PDF
            # Note: write_pdf writes all pages at once, but we've at least
            # shown the page count. For true page-by-page progress,
            # we'd need to modify WeasyPrint internals.
            document.write_pdf(pdf_file)

        if progress_callback:
            progress_callback("complete")

        return output_path

    def generate_html_preview(
        self,
        messages: List[WhatsAppMessage],
        output_path: str,
        participants: List[str] = None
    ):
        """
        Generate HTML preview (for debugging/testing)

        Args:
            messages: List of WhatsAppMessage objects
            output_path: Path where HTML should be saved
            participants: Optional list of participant names
        """
        # Read template and CSS
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        with open(self.css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        # Create sender mapping
        sender_map = {}
        if participants:
            for idx, participant in enumerate(participants):
                sender_map[participant] = idx
        else:
            unique_senders = []
            for msg in messages:
                if not msg.is_system and msg.sender not in unique_senders:
                    unique_senders.append(msg.sender)
            for idx, sender in enumerate(unique_senders):
                sender_map[sender] = idx

        # Get date range
        date_range = None
        if messages:
            timestamps = [msg.timestamp for msg in messages if not msg.is_system]
            if timestamps:
                date_range = (min(timestamps), max(timestamps))

        # Prepare template data
        template_data = {
            'css_content': css_content,
            'messages': messages,
            'participants': participants or list(sender_map.keys()),
            'sender_map': sender_map,
            'message_count': len([m for m in messages if not m.is_system]),
            'date_range': date_range
        }

        # Render template
        template = Template(template_content)
        html_content = template.render(**template_data)

        # Save HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path
