# src/libriscribe/utils/context_manager.py
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_previous_chapter_context(project_dir: Path, current_chapter_num: int, token_limit: int = 3000) -> str:
    """
    Retrieves the actual text of the previous chapter to maintain continuity.
    If the text is too long, it retrieves the last 'token_limit' words.
    """
    if current_chapter_num <= 1:
        return "This is the first chapter. No previous context available."

    prev_chapter_num = current_chapter_num - 1
    
    # Check for revised version first, then original
    revised_path = project_dir / f"chapter_{prev_chapter_num}_revised.md"
    original_path = project_dir / f"chapter_{prev_chapter_num}.md"
    
    file_to_read = None
    if revised_path.exists():
        file_to_read = revised_path
        logger.info(f"Context: Using revised content from Chapter {prev_chapter_num}")
    elif original_path.exists():
        file_to_read = original_path
        logger.info(f"Context: Using original content from Chapter {prev_chapter_num}")
    else:
        logger.warning(f"Context: Chapter {prev_chapter_num} file not found.")
        return "Previous chapter content not found."

    try:
        content = file_to_read.read_text(encoding='utf-8')
        
        # Simple word truncation to fit in context window (rough approximation of tokens)
        words = content.split()
        if len(words) > token_limit:
            # Get the LAST 3000 words (the ending of the previous chapter)
            truncated_content = " ".join(words[-token_limit:])
            return f"...[Previous text truncated]...\n{truncated_content}"
        
        return content
    except Exception as e:
        logger.error(f"Error reading previous chapter: {e}")
        return "Error reading previous context."