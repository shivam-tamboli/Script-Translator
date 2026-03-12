from typing import List


def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks of specified size."""
    if not text:
        return []
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    paragraphs = text.split("\n")
    current_chunk = []
    current_length = 0
    
    for paragraph in paragraphs:
        para_length = len(paragraph)
        
        if current_length + para_length + 1 > chunk_size:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_length = 0
        
        if para_length > chunk_size:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_length = 0
            
            for i in range(0, para_length, chunk_size):
                chunks.append(paragraph[i:i + chunk_size])
        else:
            current_chunk.append(paragraph)
            current_length += para_length + 1
    
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    
    return chunks
