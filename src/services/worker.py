from pathlib import Path
from typing import Optional, Dict
from .translator import TranslationService, TranslationError
from .extractor import FileHandler, ExtractionError
from .file_generator import FileGenerator, FileGenerationError
from ..models.enums import JobStatus
from ..utils.logger import get_logger


logger = get_logger("worker")


def process_translation(
    job_id: str,
    file_path: str,
    original_filename: str,
    source_lang: str,
    target_lang: str,
    api_key: Optional[str],
    jobs: Dict,
):
    """Background task to process translation."""
    try:
        jobs[job_id]["status"] = JobStatus.PROCESSING
        jobs[job_id]["progress"] = 0

        handler = FileHandler()
        translator = TranslationService()
        generator = FileGenerator()

        logger.info(f"Extracting text from {original_filename}")
        text = handler.extract_text(file_path)

        provider_name = "Sarvam AI" if target_lang == "hi" else "OpenAI"
        logger.info(f"Translating text using {provider_name} for {target_lang}")

        def update_progress(current: int, total: int):
            progress = int((current / total) * 100)
            jobs[job_id]["progress"] = progress
            logger.info(f"Translation progress: {progress}% ({current}/{total} chunks)")

        translated_text = translator.translate_text_chunked(
            text,
            source_lang=source_lang,
            target_lang=target_lang,
            user_api_key=api_key,
            progress_callback=update_progress,
        )

        output_filename = (
            f"{Path(original_filename).stem}_{target_lang}_translated.docx"
        )

        from ..core.config import get_settings

        settings = get_settings()
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = settings.output_dir / output_filename

        logger.info(f"Generating output file: {output_filename}")
        generator.generate(translated_text, str(output_path))

        jobs[job_id]["status"] = JobStatus.COMPLETED
        jobs[job_id]["progress"] = 100
        jobs[job_id]["translated_filename"] = str(output_path)
        jobs[job_id]["download_url"] = f"/api/v1/files/{output_filename}"

    except ExtractionError as e:
        logger.error(f"Extraction error: {e}")
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = f"Extraction failed: {str(e)}"
    except TranslationError as e:
        logger.error(f"Translation error: {e}")
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = f"Translation failed: {str(e)}"
    except FileGenerationError as e:
        logger.error(f"File generation error: {e}")
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = f"File generation failed: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = str(e)
