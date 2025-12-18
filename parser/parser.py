import re
from datetime import datetime
from typing import List, Dict, Optional, Callable


class WhatsAppMessage:
    """Represents a single WhatsApp message"""

    def __init__(self, timestamp: datetime, sender: str, content: str, is_system: bool = False):
        self.timestamp = timestamp
        self.sender = sender
        self.content = content
        self.is_system = is_system

    def __repr__(self):
        return f"WhatsAppMessage({self.timestamp}, {self.sender}, {self.content[:30]}...)"


class WhatsAppChatParser:
    """Parser for WhatsApp chat export files"""

    # Pattern to match WhatsApp message format: [DD/MM/YYYY, HH:MM:SS] Name : Message
    MESSAGE_PATTERN = re.compile(
        r'\[(\d{1,2}/\d{1,2}/\d{4}),\s(\d{1,2}:\d{2}:\d{2})\]\s([^:]+):\s(.+)'
    )

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.messages: List[WhatsAppMessage] = []

    def parse(self, progress_callback: Optional[Callable[[int, int], None]] = None) -> List[WhatsAppMessage]:
        """
        Parse the WhatsApp chat file and return list of messages

        Args:
            progress_callback: Optional callback function(current, total) for progress reporting
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        current_message: Optional[WhatsAppMessage] = None
        total_lines = len(lines)

        for idx, line in enumerate(lines, 1):
            line = line.rstrip('\n')
            match = self.MESSAGE_PATTERN.match(line)

            if match:
                # Save previous message if exists
                if current_message:
                    self.messages.append(current_message)

                # Parse new message
                date_str = match.group(1)
                time_str = match.group(2)
                sender = match.group(3).strip()
                content = match.group(4).strip()

                # Combine date and time
                datetime_str = f"{date_str} {time_str}"
                timestamp = datetime.strptime(datetime_str, "%d/%m/%Y %H:%M:%S")

                # Check if it's a system message (common indicators)
                is_system = self._is_system_message(content)

                current_message = WhatsAppMessage(timestamp, sender, content, is_system)

            elif current_message:
                # This is a continuation of the previous message (multi-line)
                current_message.content += "\n" + line

            # Report progress (every 100 lines to avoid overhead)
            if progress_callback and idx % 100 == 0:
                progress_callback(idx, total_lines)

        # Don't forget the last message
        if current_message:
            self.messages.append(current_message)

        # Report final progress
        if progress_callback:
            progress_callback(total_lines, total_lines)

        return self.messages

    def _is_system_message(self, content: str) -> bool:
        """Detect if a message is a system message"""
        system_indicators = [
            "Messages and calls are end-to-end encrypted",
            "created group",
            "added",
            "left",
            "removed",
            "changed the subject",
            "changed this group's icon",
            "changed their phone number",
            "joined using this group's invite link"
        ]

        content_lower = content.lower()
        return any(indicator.lower() in content_lower for indicator in system_indicators)

    def get_participants(self) -> List[str]:
        """Get list of unique participants (excluding system messages)"""
        participants = set()
        for msg in self.messages:
            if not msg.is_system:
                participants.add(msg.sender)
        return sorted(list(participants))

    def get_message_count(self) -> int:
        """Get total number of messages"""
        return len(self.messages)

    def get_date_range(self) -> tuple:
        """Get the start and end dates of the conversation"""
        if not self.messages:
            return None, None

        timestamps = [msg.timestamp for msg in self.messages]
        return min(timestamps), max(timestamps)
