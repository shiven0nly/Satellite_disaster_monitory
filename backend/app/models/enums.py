import enum


class ImageType(str, enum.Enum):
    IR = "IR"
    THERMAL = "THERMAL"
    OPTICAL = "OPTICAL"
    OTHER = "OTHER"


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SeverityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
