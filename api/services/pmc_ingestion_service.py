import concurrent.futures
import hashlib
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from api.services.pdf_processing_service import PDFProcessingService


DEFAULT_ROOT = Path(__file__).resolve().parents[3] / "PMC-articles"
DEFAULT_CHECKPOINT = Path(__file__).resolve().parents[2] / "ingestion_checkpoint.db"


@dataclass(frozen=True)
class PMCIngestionJob:
    path: Path
    source_id: str
    fingerprint: str
    folder: str


def natural_key(path: Path):
    return [int(part) if part.isdigit() else part.lower() for part in path.parts]


def file_fingerprint(path: Path) -> str:
    stat = path.stat()
    raw = f"{path.resolve()}::{stat.st_size}::{stat.st_mtime_ns}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_source_id(root: Path, pdf_path: Path) -> str:
    relative = pdf_path.relative_to(root).with_suffix("")
    return "-".join(relative.parts)


def init_checkpoint(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ingestion_status (
                file_path TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                folder TEXT NOT NULL,
                status TEXT NOT NULL,
                chunks_created INTEGER DEFAULT 0,
                total_results INTEGER DEFAULT 0,
                error_message TEXT,
                attempts INTEGER DEFAULT 0,
                started_at TEXT,
                completed_at TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ingestion_status ON ingestion_status(status)")


def clean_checkpoint(db_path: Path) -> None:
    if db_path.exists():
        db_path.unlink()
    init_checkpoint(db_path)


def checkpoint_row(db_path: Path, job: PMCIngestionJob):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM ingestion_status WHERE file_path = ?",
            (str(job.path),),
        ).fetchone()


def should_skip(db_path: Path, job: PMCIngestionJob, retry_failed: bool) -> bool:
    row = checkpoint_row(db_path, job)
    if not row:
        return False

    same_file = row["fingerprint"] == job.fingerprint
    if same_file and row["status"] == "completed":
        return True
    if same_file and row["status"] == "failed" and not retry_failed:
        return True
    return False


def mark_started(db_path: Path, job: PMCIngestionJob) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO ingestion_status (
                file_path, source_id, fingerprint, folder, status, attempts, started_at, updated_at
            )
            VALUES (?, ?, ?, ?, 'processing', 1, datetime('now'), datetime('now'))
            ON CONFLICT(file_path) DO UPDATE SET
                source_id = excluded.source_id,
                fingerprint = excluded.fingerprint,
                folder = excluded.folder,
                status = 'processing',
                attempts = ingestion_status.attempts + 1,
                error_message = NULL,
                started_at = datetime('now'),
                updated_at = datetime('now')
            """,
            (str(job.path), job.source_id, job.fingerprint, job.folder),
        )


def mark_completed(db_path: Path, job: PMCIngestionJob, total_results: int, chunks_created: int) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            UPDATE ingestion_status
            SET status = 'completed',
                total_results = ?,
                chunks_created = ?,
                error_message = NULL,
                completed_at = datetime('now'),
                updated_at = datetime('now')
            WHERE file_path = ?
            """,
            (total_results, chunks_created, str(job.path)),
        )


def mark_failed(db_path: Path, job: PMCIngestionJob, error: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            UPDATE ingestion_status
            SET status = 'failed',
                error_message = ?,
                completed_at = datetime('now'),
                updated_at = datetime('now')
            WHERE file_path = ?
            """,
            (error[:4000], str(job.path)),
        )


def discover_jobs(root: Path, folder_limit: int) -> list[PMCIngestionJob]:
    folders = sorted([p for p in root.iterdir() if p.is_dir()], key=natural_key)
    selected_folders = folders[:folder_limit]
    jobs = []

    for folder in selected_folders:
        for pdf_path in sorted(folder.rglob("*.pdf"), key=natural_key):
            jobs.append(PMCIngestionJob(
                path=pdf_path,
                source_id=build_source_id(root, pdf_path),
                fingerprint=file_fingerprint(pdf_path),
                folder=folder.name,
            ))

    return jobs


def process_job(
    job: PMCIngestionJob,
    db_path: Path,
    chunk_size: int,
    chunk_overlap: int,
    iter_size: int,
) -> tuple[str, str, int]:
    mark_started(db_path, job)
    started = time.time()

    try:
        service = PDFProcessingService(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            iter_size=iter_size,
        )
        results = service.process_pdf_file(str(job.path), source_id=job.source_id)
        chunk_ids = {result.chunk.chunk_id for result in results}
        mark_completed(db_path, job, total_results=len(results), chunks_created=len(chunk_ids))
        return ("completed", str(job.path), int(time.time() - started))
    except Exception as exc:
        mark_failed(db_path, job, str(exc))
        return ("failed", str(job.path), int(time.time() - started))


def checkpoint_summary(db_path: Path) -> dict[str, int]:
    init_checkpoint(db_path)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM ingestion_status
            GROUP BY status
            ORDER BY status
            """
        ).fetchall()
    return {status: count for status, count in rows}


def run_pmc_ingestion(
    root: Path = DEFAULT_ROOT,
    checkpoint: Path = DEFAULT_CHECKPOINT,
    folders: int = 10,
    max_workers: int = 1,
    limit_pdfs: int | None = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    iter_size: int = 4,
    retry_failed: bool = False,
    clean: bool = False,
) -> dict[str, int]:
    root = root.resolve()
    checkpoint = checkpoint.resolve()

    if not root.exists():
        raise FileNotFoundError(f"PMC root not found: {root}")

    if clean:
        clean_checkpoint(checkpoint)
    else:
        init_checkpoint(checkpoint)

    jobs = discover_jobs(root, folders)
    pending_jobs = [job for job in jobs if not should_skip(checkpoint, job, retry_failed)]
    if limit_pdfs is not None:
        pending_jobs = pending_jobs[:limit_pdfs]

    max_workers = max(1, max_workers)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_job, job, checkpoint, chunk_size, chunk_overlap, iter_size)
            for job in pending_jobs
        ]
        for future in concurrent.futures.as_completed(futures):
            status, path, elapsed = future.result()
            print(f"[{status.upper()}] {path} ({elapsed}s)")

    return checkpoint_summary(checkpoint)
