import argparse
import concurrent.futures
import hashlib
import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# ── Force UTF-8 output on Windows (prevents cp1252 charmap crashes when
#    medical PDFs contain Greek/special characters like α, β, μ, etc.) ─────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_ROOT = Path(__file__).resolve().parent.parent / "PMC-articles"
DEFAULT_CHECKPOINT = Path(__file__).resolve().parent / "ingestion_checkpoint.db"


@dataclass(frozen=True)
class PdfJob:
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


def checkpoint_row(db_path: Path, job: PdfJob):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM ingestion_status WHERE file_path = ?",
            (str(job.path),),
        ).fetchone()


def should_skip(db_path: Path, job: PdfJob, retry_failed: bool) -> bool:
    row = checkpoint_row(db_path, job)
    if not row:
        return False

    same_file = row["fingerprint"] == job.fingerprint
    if same_file and row["status"] == "completed":
        return True
    if same_file and row["status"] == "failed" and not retry_failed:
        return True
    return False


def mark_started(db_path: Path, job: PdfJob) -> None:
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


def mark_completed(db_path: Path, job: PdfJob, total_results: int, chunks_created: int) -> None:
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


def mark_failed(db_path: Path, job: PdfJob, error: str) -> None:
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


def discover_jobs(root: Path, folder_limit: int) -> list[PdfJob]:
    folders = sorted([p for p in root.iterdir() if p.is_dir()], key=natural_key)
    selected_folders = folders[:folder_limit]
    jobs = []

    for folder in selected_folders:
        pdfs = sorted(folder.rglob("*.pdf"), key=natural_key)
        for pdf_path in pdfs:
            jobs.append(PdfJob(
                path=pdf_path,
                source_id=build_source_id(root, pdf_path),
                fingerprint=file_fingerprint(pdf_path),
                folder=folder.name,
            ))

    return jobs


def process_job(job: PdfJob, db_path: Path, chunk_size: int, chunk_overlap: int, iter_size: int) -> tuple[str, str, int]:
    from api.services.pdf_processing_service import PDFProcessingService

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


def print_summary(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM ingestion_status
            GROUP BY status
            ORDER BY status
            """
        ).fetchall()

    print("\nCheckpoint summary:")
    for status, count in rows:
        print(f"  {status}: {count}")


def parse_args():
    parser = argparse.ArgumentParser(description="Batch ingest PMC PDFs into the GraphRAG Neo4j store.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Root PMC articles folder.")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT, help="SQLite checkpoint DB path.")
    parser.add_argument("--folders", type=int, default=45, help="Number of top-level folders to ingest.")
    parser.add_argument("--max-workers", type=int, default=1, help="Concurrent PDF workers. Start with 1 or 2.")
    parser.add_argument("--limit-pdfs", type=int, default=None, help="Optional cap for smoke-testing a small number of PDFs.")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=100)
    parser.add_argument("--iter-size", type=int, default=4, help="Chunks per graph-extraction batch inside each PDF.")
    parser.add_argument("--retry-failed", action="store_true", help="Retry PDFs marked failed in the checkpoint.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned PDFs without ingesting.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    checkpoint = args.checkpoint.resolve()

    if not root.exists():
        print(f"PMC root not found: {root}")
        return 1

    init_checkpoint(checkpoint)
    jobs = discover_jobs(root, args.folders)
    pending_jobs = [job for job in jobs if not should_skip(checkpoint, job, args.retry_failed)]
    if args.limit_pdfs is not None:
        pending_jobs = pending_jobs[:args.limit_pdfs]

    print(f"PMC root: {root}")
    print(f"Checkpoint: {checkpoint}")
    print(f"Selected folders: {args.folders}")
    print(f"Discovered PDFs: {len(jobs)}")
    print(f"Pending PDFs: {len(pending_jobs)}")
    if args.limit_pdfs is not None:
        print(f"PDF limit: {args.limit_pdfs}")
    print(f"Max workers: {args.max_workers}")

    if args.dry_run:
        for job in pending_jobs[:25]:
            print(f"  {job.folder}: {job.path.name} -> {job.source_id}")
        if len(pending_jobs) > 25:
            print(f"  ... {len(pending_jobs) - 25} more")
        return 0

    if not pending_jobs:
        print_summary(checkpoint)
        return 0

    completed = 0
    failed = 0
    max_workers = max(1, args.max_workers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                process_job,
                job,
                checkpoint,
                args.chunk_size,
                args.chunk_overlap,
                args.iter_size,
            )
            for job in pending_jobs
        ]

        for future in concurrent.futures.as_completed(futures):
            status, path, elapsed = future.result()
            if status == "completed":
                completed += 1
            else:
                failed += 1
            print(f"[{status.upper()}] {path} ({elapsed}s) | completed={completed} failed={failed}")

    print_summary(checkpoint)
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
