import asyncio
import uuid
from unittest.mock import AsyncMock, patch

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base
from app.models.enums import ImageType, JobStatus, SeverityLevel
from app.models.job import Job
from app.models.result import Result
from app.schemas.result import ParsedResult
from app.services.job_processor import process_job_background
from app.services.llm_service import LLMServiceError


async def run_e2e_test():
    print("--- Starting E2E Pipeline Integration Test ---")

    # 1. Setup SQLite in-memory test database engine
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Test Success Flow
    async with async_session() as session:
        new_job = Job(
            image_url="uploads/test_satellite_ir.jpg",
            image_type=ImageType.IR,
            status=JobStatus.PENDING,
        )
        session.add(new_job)
        await session.commit()
        job_id = new_job.id
        print(f"[1] Created test job {job_id} with status PENDING")

    # Mock AsyncSessionLocal used in process_job_background to use test_session
    mock_parsed_result = ParsedResult(
        disaster_type="Wildfire",
        severity=SeverityLevel.HIGH,
        affected_area_estimate="18.4 sq km",
        description="Thermal anomalies detected active fire front with high NDVI drop.",
        confidence_score=0.92,
        latitude=34.0522,
        longitude=-118.2437,
        raw_model_output={"disaster_type": "Wildfire", "confidence": 0.92},
    )

    with patch("app.services.job_processor.AsyncSessionLocal", async_session), \
         patch("app.services.job_processor.parse_model_output", new_callable=AsyncMock) as mock_parse:
        
        mock_parse.return_value = mock_parsed_result
        
        # Execute background job processor
        await process_job_background(job_id, "uploads/test_satellite_ir.jpg")

    # Verify DB state after successful processing
    async with async_session() as session:
        query = await session.execute(select(Job).where(Job.id == job_id))
        processed_job = query.scalar_one_or_none()
        
        assert processed_job is not None
        assert processed_job.status == JobStatus.COMPLETED, f"Expected COMPLETED, got {processed_job.status}"
        print(f"[2] Job status successfully updated to: {processed_job.status}")

        result_query = await session.execute(select(Result).where(Result.job_id == job_id))
        result_record = result_query.scalar_one_or_none()

        assert result_record is not None
        assert result_record.disaster_type == "Wildfire"
        assert result_record.severity == SeverityLevel.HIGH
        print(f"[3] Result record correctly saved into DB with disaster_type: '{result_record.disaster_type}' and severity: '{result_record.severity}'")

    # 3. Test LLM Error Handling Flow
    async with async_session() as session:
        failed_job = Job(
            image_url="uploads/test_fail.jpg",
            image_type=ImageType.THERMAL,
            status=JobStatus.PENDING,
        )
        session.add(failed_job)
        await session.commit()
        failed_job_id = failed_job.id
        print(f"[4] Created second test job {failed_job_id} to verify failure handling")

    with patch("app.services.job_processor.AsyncSessionLocal", async_session), \
         patch("app.services.job_processor.parse_model_output", new_callable=AsyncMock) as mock_parse_fail:
        
        mock_parse_fail.side_effect = LLMServiceError("Gemini API rate limit exceeded")
        
        await process_job_background(failed_job_id, "uploads/test_fail.jpg")

    async with async_session() as session:
        query = await session.execute(select(Job).where(Job.id == failed_job_id))
        db_failed_job = query.scalar_one_or_none()

        assert db_failed_job is not None
        assert db_failed_job.status == JobStatus.FAILED, f"Expected FAILED, got {db_failed_job.status}"
        assert db_failed_job.error_message == "Gemini API rate limit exceeded"
        print(f"[5] Failure handling verified! Job status: '{db_failed_job.status}', error_message: '{db_failed_job.error_message}'")

    await test_engine.dispose()
    print("--- E2E Pipeline Integration Test Completed Successfully! ---")


if __name__ == "__main__":
    asyncio.run(run_e2e_test())
