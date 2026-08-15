import logging
from uuid import UUID

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.enums import JobStatus, SeverityLevel
from app.models.job import Job
from app.models.result import Result
from app.services.mock_ml import fake_llm_parse, fake_model_predict

logger = logging.getLogger(__name__)


async def process_job_background(job_id: UUID, image_path: str) -> None:
    """
    Background worker task to simulate ML inference and LLM response parsing.
    Updates job status in database to PROCESSING -> COMPLETED (or FAILED).
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

            # 2. Run mock ML vision prediction
            # PLACEHOLDER: Replace with real ML inference execution
            model_output = fake_model_predict(image_path)

            # 3. Run mock LLM output parser
            # PLACEHOLDER: Replace with real LLM API call
            parsed_data = fake_llm_parse(model_output)

            # 4. Save result to database
            severity_val = parsed_data.get("severity", "MEDIUM")
            try:
                severity_enum = SeverityLevel[severity_val]
            except KeyError:
                severity_enum = SeverityLevel.MEDIUM

            result_entry = Result(
                job_id=job.id,
                disaster_type=parsed_data.get("disaster_type", "Unknown"),
                severity=severity_enum,
                affected_area_estimate=parsed_data.get("affected_area_estimate"),
                description=parsed_data.get("description"),
                confidence_score=parsed_data.get("confidence_score"),
                latitude=parsed_data.get("latitude"),
                longitude=parsed_data.get("longitude"),
                raw_model_output=parsed_data.get("raw_model_output"),
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
                    await db.commit()
            except Exception as rollback_err:
                logger.error(f"Failed to mark job {job_id} as FAILED: {rollback_err}")
