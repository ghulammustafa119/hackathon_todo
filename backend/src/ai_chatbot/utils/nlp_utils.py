"""Natural Language Processing utilities for intent detection and parameter extraction."""

import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
from dateutil import parser


def extract_task_parameters(text: str) -> Dict[str, str]:
    """
    Extract task-related parameters from natural language text.

    Args:
        text: Natural language input to extract parameters from

    Returns:
        Dictionary containing extracted parameters (title, description, due_date)
    """
    params = {}

    # Extract due date using various patterns
    date_patterns = [
        r'tomorrow',
        r'next week',
        r'next month',
        r'in \d+ days?',
        r'on \d{4}-\d{2}-\d{2}',
        r'on [A-Za-z]+ \d{1,2}(?:st|nd|rd|th)?,? \d{4}?',
        r'by \d{4}-\d{2}-\d{2}',
        r'by [A-Za-z]+ \d{1,2}(?:st|nd|rd|th)?,? \d{4}?',
    ]

    found_dates = []
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            found_dates.append((match.start(), match.group()))

    # Sort by position in text to get the first occurrence
    found_dates.sort(key=lambda x: x[0])

    if found_dates:
        date_text = found_dates[0][1]
        parsed_date = parse_natural_date(date_text)
        if parsed_date:
            params['due_date'] = parsed_date.strftime('%Y-%m-%d')

    # Remove date references from text to better extract title/description
    clean_text = text
    for _, date_match in found_dates:
        clean_text = clean_text.replace(date_match, '', 1)

    # Look for keywords indicating description vs title
    # Find the main task action/command
    # Remove common task-related phrases
    clean_text = re.sub(r'(add|create|make|set up|establish)\s+(a|an|the)?\s*', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'(task|item|to-do|todo)', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'(to|that|should)', '', clean_text, flags=re.IGNORECASE)

    # Extract title - typically comes after action words
    # Look for the main subject of the task
    title_match = re.search(r'([^,.!?]+)', clean_text.strip())
    if title_match:
        title = title_match.group(1).strip()
        # Clean up common phrases
        title = re.sub(r'(to|for|with)\s+', '', title, count=1)
        params['title'] = title
    else:
        params['title'] = clean_text.strip() or "Untitled task"

    # Use remaining text as description if it's substantial
    if len(clean_text.split()) > 5:  # If there's more than 5 words
        params['description'] = clean_text.strip()

    return params


def parse_natural_date(date_str: str) -> Optional[datetime]:
    """
    Parse natural language date expressions into datetime objects.

    Args:
        date_str: Natural language date expression

    Returns:
        Parsed datetime object or None if parsing fails
    """
    date_str = date_str.lower().strip()

    # Handle relative dates
    if 'tomorrow' in date_str:
        return datetime.now() + timedelta(days=1)
    elif 'next week' in date_str:
        return datetime.now() + timedelta(weeks=1)
    elif 'next month' in date_str:
        return datetime.now() + timedelta(days=30)  # Approximate
    elif 'today' in date_str:
        return datetime.now()
    elif 'yesterday' in date_str:
        return datetime.now() - timedelta(days=1)

    # Handle "in X days" format
    in_days_match = re.search(r'in (\d+) days?', date_str)
    if in_days_match:
        days = int(in_days_match.group(1))
        return datetime.now() + timedelta(days=days)

    # Handle ISO format (YYYY-MM-DD)
    iso_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
    if iso_match:
        try:
            return datetime.fromisoformat(iso_match.group(1))
        except ValueError:
            pass

    # Try using dateutil parser for other formats
    try:
        return parser.parse(date_str, fuzzy=True)
    except (parser.ParserError, ValueError, OverflowError):
        # If all parsing methods fail, return None
        return None


def detect_intent(text: str) -> str:
    """
    Detect the user's intent from natural language input.

    Args:
        text: Natural language input

    Returns:
        Detected intent (create_task, list_tasks, update_task, delete_task, complete_task)
    """
    text_lower = text.lower()

    # Define keywords for each intent
    create_keywords = ['add', 'create', 'make', 'new', 'setup', 'establish', 'put in']
    list_keywords = ['show', 'list', 'display', 'see', 'view', 'get', 'fetch', 'what']
    update_keywords = ['update', 'change', 'modify', 'edit', 'adjust', 'alter']
    delete_keywords = ['delete', 'remove', 'erase', 'cancel', 'get rid of', 'eliminate']
    complete_keywords = ['complete', 'finish', 'done', 'mark', 'as done', 'accomplish']

    # Count keyword matches for each intent
    scores = {
        'create_task': sum(1 for keyword in create_keywords if keyword in text_lower),
        'list_tasks': sum(1 for keyword in list_keywords if keyword in text_lower),
        'update_task': sum(1 for keyword in update_keywords if keyword in text_lower),
        'delete_task': sum(1 for keyword in delete_keywords if keyword in text_lower),
        'complete_task': sum(1 for keyword in complete_keywords if keyword in text_lower)
    }

    # Return the intent with highest score, defaulting to list_tasks if no clear match
    max_intent = max(scores, key=scores.get)
    return max_intent if scores[max_intent] > 0 else 'list_tasks'


def extract_task_id(text: str) -> Optional[str]:
    """
    Extract task ID from natural language input.

    Args:
        text: Natural language input

    Returns:
        Extracted task ID or None if not found
    """
    # Look for UUID-like patterns in the text
    uuid_pattern = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    matches = re.findall(uuid_pattern, text, re.IGNORECASE)
    return matches[0] if matches else None


def extract_task_reference(text: str) -> Optional[str]:
    """
    Extract task reference (by title or description) from natural language input.

    Args:
        text: Natural language input

    Returns:
        Task reference string or None if not found
    """
    # Look for phrases like "the meeting task", "my grocery list", etc.
    reference_patterns = [
        r'the ([^,!.?]+) (task|item)',
        r'my ([^,!.?]+)',
        r'([^,!.?]+) (task|item)',
    ]

    for pattern in reference_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Return the first match, taking the first group (the reference part)
            reference = matches[0][0] if isinstance(matches[0], tuple) else matches[0]
            return reference.strip()

    return None


def normalize_task_title(title: str) -> str:
    """
    Normalize task title by removing common prefixes/suffixes.

    Args:
        title: Raw task title

    Returns:
        Normalized task title
    """
    title = title.strip()

    # Remove common prefixes
    prefixes = ['to ', 'for ', 'about ', 'regarding ', 'concerning ']
    for prefix in prefixes:
        if title.lower().startswith(prefix):
            title = title[len(prefix):]

    # Remove common suffixes
    suffixes = [' task', ' item', ' thing', ' stuff']
    for suffix in suffixes:
        if title.lower().endswith(suffix):
            title = title[:-len(suffix)]

    return title.strip()


def extract_completion_status(text: str) -> Optional[bool]:
    """
    Extract completion status intent from natural language input.

    Args:
        text: Natural language input

    Returns:
        Boolean completion status (True for complete, False for incomplete) or None
    """
    text_lower = text.lower()

    # Keywords indicating completion
    complete_keywords = ['complete', 'done', 'finished', 'accomplished', 'marked done']
    # Keywords indicating incompleteness
    incomplete_keywords = ['incomplete', 'not done', 'not finished', 'still pending']

    complete_score = sum(1 for keyword in complete_keywords if keyword in text_lower)
    incomplete_score = sum(1 for keyword in incomplete_keywords if keyword in text_lower)

    if complete_score > incomplete_score:
        return True
    elif incomplete_score > complete_score:
        return False
    else:
        return None  # Status unclear