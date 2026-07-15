"""
User settings and reports API routes
"""
import asyncio
import json
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Header, Query # type: ignore
from fastapi.responses import StreamingResponse # type: ignore
from pydantic import BaseModel # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from sqlalchemy import select, delete, func, text # type: ignore
from sqlalchemy.orm import defer # type: ignore
from datetime import datetime

from backend.app.db import get_db, User, UserSettings, Report
from backend.app.services.auth_utils import verify_access_token, encrypt_settings, decrypt_settings

router = APIRouter(prefix="/api/user", tags=["User"])

# ============== SSE: Real-time cross-device sync ==============

# Per-user SSE queues: user_id (str) -> list of asyncio.Queue
_user_queues: dict[str, list] = {}


def _notify_user(user_id: str, event_type: str = "report_changed") -> None:
    """Push a notification to all SSE connections open for this user."""
    queues = _user_queues.get(str(user_id), [])
    data = json.dumps({"type": event_type})
    for q in queues:
        try:
            q.put_nowait(data)
        except asyncio.QueueFull:
            pass  # drop if consumer is too slow


@router.get("/events")
async def user_events(token: str = Query(...)):
    """
    SSE stream for real-time cross-device sync.
    Token is passed as a query param because EventSource does not support headers.
    Sends a 'report_changed' event whenever reports are added or deleted on another device.
    """
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    queue: asyncio.Queue = asyncio.Queue(maxsize=50)
    _user_queues.setdefault(user_id, []).append(queue)

    async def event_stream():
        try:
            yield "event: connected\ndata: {}\n\n"
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=25)
                    yield f"event: report_changed\ndata: {data}\n\n"
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"  # keep connection alive through proxies
        finally:
            queues = _user_queues.get(user_id, [])
            if queue in queues:
                queues.remove(queue)
            if not queues:
                _user_queues.pop(user_id, None)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering
            "Connection": "keep-alive",
        },
    )


# ============== Pydantic Models ==============

class SettingsUpdate(BaseModel):
    """API settings to save"""
    openai_api_key: str = ""
    alpha_vantage_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    grok_api_key: str = ""
    deepseek_api_key: str = ""
    qwen_api_key: str = ""
    finmind_api_key: str = ""
    custom_base_url: str = ""
    custom_api_key: str = ""


class ReportCreate(BaseModel):
    """Report to save"""
    ticker: str
    market_type: str  # us, twse, tpex
    analysis_date: str
    result: dict
    language: Optional[str] = None


class ReportResponse(BaseModel):
    """Report response"""
    id: str
    ticker: str
    market_type: str
    analysis_date: str
    result: dict
    language: Optional[str] = None
    created_at: str


# ============== Auth Dependency ==============

async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user from JWT token (optional - returns None if not authenticated)"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    payload = verify_access_token(token)
    
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    try:
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        return result.scalar_one_or_none()
    except:
        return None


async def get_current_user_required(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Require authenticated user"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


# ============== Settings Routes ==============

@router.get("/settings")
async def get_settings(
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Get user's saved API settings (decrypted)"""
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        return {"settings": None}
    
    try:
        decrypted = decrypt_settings(settings.encrypted_settings)
        return {"settings": json.loads(decrypted)}
    except Exception as e:
        print(f"Failed to decrypt settings: {e}")
        return {"settings": None}


@router.put("/settings")
async def update_settings(
    settings_data: SettingsUpdate,
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Save user's API settings (encrypted)"""
    # Convert to JSON and encrypt
    settings_json = json.dumps(settings_data.model_dump())
    encrypted = encrypt_settings(settings_json)
    
    # Find existing settings
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.encrypted_settings = encrypted
        existing.updated_at = datetime.utcnow()
    else:
        new_settings = UserSettings(
            user_id=user.id,
            encrypted_settings=encrypted
        )
        db.add(new_settings)
    
    await db.commit()
    
    return {"success": True, "message": "Settings saved successfully"}


# ============== Reports Routes ==============

@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
    market_type: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    include_result: bool = True,
):
    """Get user's reports with optional filtering and pagination

    Args:
        market_type: Filter by market type (us, twse, tpex)
        language: Filter by language (en, zh-TW)
        limit: Maximum number of reports to return (default 100, max 500)
        offset: Number of reports to skip for pagination
        include_result: Whether to include result JSONB field (default True for backward compat).
                        Set to False for lightweight list queries.
    """
    # Cap limit at 500 to prevent memory issues
    limit = min(limit, 500)

    # Build query with filters
    query = select(Report).where(Report.user_id == user.id)

    # Skip loading the large result JSONB column when not needed
    if not include_result:
        query = query.options(defer(Report.result))

    if market_type:
        query = query.where(Report.market_type == market_type)

    if language:
        query = query.where(func.coalesce(Report.language, "zh-TW") == language)

    # Order by created_at DESC and apply pagination
    query = query.order_by(Report.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    reports = result.scalars().all()

    # Process reports
    optimized_reports = []
    for r in reports:
        if include_result and r.result and isinstance(r.result, dict):
            optimized_result = r.result
        elif include_result:
            optimized_result = r.result or {}
        else:
            optimized_result = {}

        optimized_reports.append(
            ReportResponse(
                id=str(r.id),
                ticker=r.ticker,
                market_type=r.market_type,
                analysis_date=r.analysis_date,
                result=optimized_result,
                language=r.language,
                created_at=r.created_at.isoformat() + "Z"
            )
        )

    return optimized_reports


@router.post("/reports")
async def create_report(
    report_data: ReportCreate,
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Save a report. Upserts only when ticker/date/market/language AND model names match.
    Reports with different models on the same ticker/date are stored as separate entries."""
    # Normalize language: treat None as "zh-TW" to avoid NULL matching issues
    language = report_data.language or "zh-TW"

    # Extract model names from the incoming result payload
    new_result = report_data.result or {}
    new_deep = new_result.get("deep_think_llm") or ""
    new_quick = new_result.get("quick_think_llm") or ""

    # Fetch all reports for this ticker/date/market/language, then compare models in Python
    existing_candidates_result = await db.execute(
        select(Report)
        .where(Report.user_id == user.id)
        .where(Report.ticker == report_data.ticker)
        .where(Report.analysis_date == report_data.analysis_date)
        .where(Report.market_type == report_data.market_type)
        .where(func.coalesce(Report.language, "zh-TW") == language)
    )
    existing_candidates = existing_candidates_result.scalars().all()

    existing = None
    for candidate in existing_candidates:
        candidate_result = candidate.result or {}
        candidate_deep = candidate_result.get("deep_think_llm") or ""
        candidate_quick = candidate_result.get("quick_think_llm") or ""
        # Same model (or both have no model info) → treat as same report
        if candidate_deep == new_deep and candidate_quick == new_quick:
            existing = candidate
            break

    if existing:
        # Same model + same ticker/date → update in place (true duplicate)
        existing.result = report_data.result
        existing.language = language
        await db.commit()
        _notify_user(str(user.id))
        return {
            "success": True,
            "report_id": str(existing.id),
            "message": "Report updated successfully"
        }

    # Different model (or no prior report) — create new entry
    report = Report(
        user_id=user.id,
        ticker=report_data.ticker,
        market_type=report_data.market_type,
        analysis_date=report_data.analysis_date,
        result=report_data.result,
        language=language,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    _notify_user(str(user.id))

    return {
        "success": True,
        "report_id": str(report.id),
        "message": "Report saved successfully"
    }


@router.get("/reports/counts")
async def get_report_counts(
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
    language: Optional[str] = None,
):
    """Get report counts by market_type without loading full rows (lightweight query)"""
    base_query = (
        select(
            Report.market_type,
            func.count(Report.id).label("count")
        )
        .where(Report.user_id == user.id)
        .group_by(Report.market_type)
    )

    if language:
        base_query = base_query.where(
            func.coalesce(Report.language, "zh-TW") == language
        )

    result = await db.execute(base_query)
    rows = result.all()

    counts = {"us": 0, "twse": 0, "tpex": 0}
    for market_type, count in rows:
        if market_type in counts:
            counts[market_type] = count

    total = sum(counts.values())

    return {"counts": counts, "total": total}


@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific report"""
    try:
        result = await db.execute(
            select(Report)
            .where(Report.id == UUID(report_id))
            .where(Report.user_id == user.id)
        )
        report = result.scalar_one_or_none()
    except:
        raise HTTPException(status_code=400, detail="Invalid report ID")
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return ReportResponse(
        id=str(report.id),
        ticker=report.ticker,
        market_type=report.market_type,
        analysis_date=report.analysis_date,
        result=report.result,
        language=report.language,
        created_at=report.created_at.isoformat() + "Z"
    )


@router.delete("/reports/cleanup-duplicates")
async def cleanup_duplicate_reports(
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Remove duplicate reports using SQL-level deduplication.
    Keeps only the most recent one per (ticker, analysis_date, market_type, language, deep_model, quick_model).
    Reports with different models are treated as distinct and are NOT deleted.
    """
    # Use SQL window function to find duplicates without loading all rows into memory
    # Extract model names from JSON result field so different-model reports are kept separately
    result = await db.execute(text("""
        DELETE FROM reports
        WHERE id IN (
            SELECT id FROM (
                SELECT id,
                    ROW_NUMBER() OVER (
                        PARTITION BY user_id, ticker, analysis_date, market_type,
                                     COALESCE(language, 'zh-TW'),
                                     COALESCE(result->>'deep_think_llm', ''),
                                     COALESCE(result->>'quick_think_llm', '')
                        ORDER BY created_at DESC
                    ) as rn
                FROM reports
                WHERE user_id = :user_id
            ) ranked
            WHERE rn > 1
        )
    """), {"user_id": str(user.id)})

    deleted_count = result.rowcount # type: ignore
    await db.commit()
    if deleted_count > 0:
        _notify_user(str(user.id))

    return {
        "success": True,
        "deleted": deleted_count,
        "message": f"Cleaned up {deleted_count} duplicate reports"
    }


@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: str,
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Delete a report"""
    try:
        result = await db.execute(
            select(Report)
            .where(Report.id == UUID(report_id))
            .where(Report.user_id == user.id)
        )
        report = result.scalar_one_or_none()
    except:
        raise HTTPException(status_code=400, detail="Invalid report ID")
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    await db.delete(report)
    await db.commit()
    _notify_user(str(user.id))

    return {"success": True, "message": "Report deleted successfully"}


@router.delete("/reports")
async def delete_all_reports(
    user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db)
):
    """Delete all user's reports"""
    await db.execute(
        delete(Report).where(Report.user_id == user.id)
    )
    await db.commit()
    _notify_user(str(user.id))

    return {"success": True, "message": "All reports deleted successfully"}
