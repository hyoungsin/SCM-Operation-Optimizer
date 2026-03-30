from app.repository.run_repository import get_run
from app.schemas.common import CorrectedPreviewResponse, PreviewSheet

PREVIEW_SHEETS = [
    "set-demand",
    "item-delivery",
    "capacity",
    "set-shipment",
    "delivery",
]
MAX_SAMPLE_ROWS = 10


def get_corrected_preview(run_id: str) -> CorrectedPreviewResponse | None:
    run = get_run(run_id)
    if run is None:
        return None

    validation = run.get("validation")
    normalized_sheets = run.get("normalized_sheets")
    if not validation or normalized_sheets is None:
        return CorrectedPreviewResponse(
            run_id=run_id,
            preview_generated=False,
            sheets=[],
        )

    sheet_names = [name for name in PREVIEW_SHEETS if name in normalized_sheets]
    if not sheet_names:
        sheet_names = list(normalized_sheets.keys())[:5]

    preview_sheets: list[PreviewSheet] = []
    for sheet_name in sheet_names:
        sheet_data = normalized_sheets.get(sheet_name, {})
        rows = sheet_data.get("rows", [])
        preview_sheets.append(
            PreviewSheet(
                sheet_name=sheet_name,
                row_count=sheet_data.get("row_count", len(rows)),
                sample_rows=rows[:MAX_SAMPLE_ROWS],
            )
        )

    preview_response = CorrectedPreviewResponse(
        run_id=run_id,
        preview_generated=True,
        sheets=preview_sheets,
    )
    from app.repository.run_repository import update_run

    update_run(run_id, preview=preview_response.model_dump())
    return preview_response
