import logging
from uuid import UUID

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.enums import JobStatus
from app.models.job import Job
from app.models.result import Result
from app.services.llm_service import LLMParsingError, LLMServiceError, parse_model_output
from app.services.mock_ml import fake_model_predict

logger = logging.getLogger(__name__)


async def process_job_background(job_id: UUID, image_path: str) -> None:
    """
    Background worker task to run vision model prediction and LLM parsing.
    Updates job status in database to PROCESSING -> COMPLETED (or FAILED with error_message).
    """
    async with AsyncSessionLocal() as db:
        try:
            # 1. Retrieve Job
            stmt = select(Job).where(Job.id == job_id)
            query_result = await db.execute(stmt)
            job = query_result.scalar_one_or_none()

            if not job:
                logger.error(f"Job {job_id} not found for background execution.")
                return

            # Update job status to PROCESSING
            job.status = JobStatus.PROCESSING
            await db.commit()

            # 2. Run vision model prediction
            # PLACEHOLDER: Replace with real PyTorch/ONNX ML model inference
            model_output = fake_model_predict(image_path)

            # 3. Run real LLM output parser
            logger.info(f"Starting LLM parsing for job {job_id}...")
            try:
                parsed_result = await parse_model_output(model_output)
                logger.info(f"LLM parsing completed successfully for job {job_id}.")
            except (LLMParsingError, LLMServiceError) as llm_err:
                logger.error(f"LLM processing failed for job {job_id}: {llm_err.message}")
                await db.rollback()
                stmt = select(Job).where(Job.id == job_id)
                res = await db.execute(stmt)
                failed_job = res.scalar_one_or_none()
                if failed_job:
                    failed_job.status = JobStatus.FAILED
                    failed_job.error_message = llm_err.message
                    await db.commit()
                return

            # 4. Save result to database
            result_entry = Result(
                job_id=job.id,
                disaster_type=parsed_result.disaster_type,
                severity=parsed_result.severity,
                affected_area_estimate=parsed_result.affected_area_estimate,
                description=parsed_result.description,
                confidence_score=parsed_result.confidence_score,
                latitude=parsed_result.latitude,
                longitude=parsed_result.longitude,
                raw_model_output=parsed_result.raw_model_output,
            )
            db.add(result_entry)

            # 5. Mark job as COMPLETED
            job.status = JobStatus.COMPLETED
            await db.commit()
            logger.info(f"Job {job_id} processing completed successfully.")

        except Exception as err:
            logger.exception(f"Failed to process job {job_id}: {err}")
            await db.rollback()
            try:
                stmt = select(Job).where(Job.id == job_id)
                res = await db.execute(stmt)
                failed_job = res.scalar_one_or_none()
                if failed_job:
                    failed_job.status = JobStatus.FAILED
                    failed_job.error_message = str(err)
                    await db.commit()
            except Exception as rollback_err:
                logger.error(f"Failed to mark job {job_id} as FAILED: {rollback_err}")
