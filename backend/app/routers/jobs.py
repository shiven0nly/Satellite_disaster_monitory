import os
import shutil
import uuid
from typing import Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.enums import ImageType, JobStatus
from app.models.job import Job
from app.schemas.errors import ErrorResponse
from app.schemas.job import JobListResponse, JobRead
from app.services.job_processor import process_job_background

router = APIRouter(prefix="", tags=["Jobs & Analysis"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB
UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))


@router.post(
    "/upload",
    response_model=JobRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload Satellite/IR Image for Disaster Analysis",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file type"},
        413: {"model": ErrorResponse, "description": "File size exceeds 20MB limit"},
    },
)
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    image_type: ImageType = Form(default=ImageType.OTHER),
    db: AsyncSession = Depends(get_db),
) -> JobRead:
    # 1. Validate file extension
    file_ext = os.path.splitext(file.filename or "")[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_FILE_TYPE",
                "message": f"Unsupported file extension '{file_ext}'. Allowed extensions are: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            },
        )

    # 2. Validate file size (20MB limit)
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed size of 20MB.",
            },
        )

    # 3. Create unique Job ID and local storage path
    job_id = uuid.uuid4()
    job_upload_dir = os.path.join(UPLOADS_DIR, str(job_id))
    os.makedirs(job_upload_dir, exist_ok=True)
    saved_file_path = os.path.join(job_upload_dir, file.filename or "image.jpg")

    # Save file to local disk
    # PLACEHOLDER: Replace local disk storage with AWS S3 / Google Cloud Storage upload call here
    with open(saved_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 4. Create Job record in DB with PENDING status
    image_url_path = f"/uploads/{job_id}/{file.filename}"
    new_job = Job(
        id=job_id,
        image_url=image_url_path,
        image_type=image_type,
        status=JobStatus.PENDING,
    )
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # 5. Schedule Background Task
    background_tasks.add_task(process_job_background, new_job.id, saved_file_path)

    return new_job


@router.get(
    "/results/{job_id}",
    response_model=JobRead,
    summary="Get Job Analysis Result",
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
    },
)
async def get_job_result(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> JobRead:
    stmt = select(Job).options(selectinload(Job.result)).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOB_NOT_FOUND",
                "message": f"No job found with ID {job_id}",
            },
        )

    return job


@router.get(
    "/jobs",
    response_model=JobListResponse,
    summary="List All Analysis Jobs (Paginated)",
)
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    job_status: Optional[JobStatus] = Query(None, alias="status", description="Filter by job status"),
    db: AsyncSession = Depends(get_db),
) -> JobListResponse:
    query = select(Job).options(selectinload(Job.result))
    count_query = select(func.count(Job.id))

    if job_status:
        query = query.where(Job.status == job_status)
        count_query = count_query.where(Job.status == job_status)

    query = query.order_by(Job.created_at.desc()).offset(skip).limit(limit)

    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    jobs_res = await db.execute(query)
    jobs = list(jobs_res.scalars().all())

    return JobListResponse(
        total=total,
        skip=skip,
        limit=limit,
        jobs=jobs,
    )
