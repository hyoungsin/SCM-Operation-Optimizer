import re
from decimal import Decimal, InvalidOperation

REQUIRED_SHEETS = [
    "set-price",
    "set-demand",
    "set-inventory",
    "item-inventory",
    "item-delivery",
    "bom",
    "resource",
    "capacity",
    "set-shipment",
    "bod",
    "delivery",
    "air-mode",
    "demand-priority",
]

WEEK_COLUMN_PATTERN = re.compile(r"^w\d+$", re.IGNORECASE)
KNOWN_NUMERIC_COLUMNS = {
    "price",
    "holding-cost",
    "backorder-penalty",
    "usage",
    "leadtime",
    "air-leadtime",
    "air-cost",
    "priority",
    "enabled",
}


def _is_null_like(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def _is_numeric_column(header: str) -> bool:
    header_lower = header.strip().lower()
    return bool(WEEK_COLUMN_PATTERN.match(header_lower)) or header_lower in KNOWN_NUMERIC_COLUMNS


def _to_decimal(value: object) -> Decimal | None:
    if _is_null_like(value):
        return None
    if isinstance(value, bool):
        return Decimal(int(value))
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, str):
        try:
            return Decimal(value.strip())
        except InvalidOperation:
            return None
    return None


def _normalize_numeric_value(
    sheet_name: str,
    row_number: int,
    header: str,
    value: object,
    warnings: list[dict[str, str]],
) -> Decimal:
    if _is_null_like(value):
        warnings.append(
            {
                "sheet": sheet_name,
                "row": str(row_number),
                "column": header,
                "message": "Null or empty value converted to 0.",
            }
        )
        return Decimal("0")

    decimal_value = _to_decimal(value)
    if decimal_value is None:
        warnings.append(
            {
                "sheet": sheet_name,
                "row": str(row_number),
                "column": header,
                "message": f"Non-numeric value '{value}' converted to 0.",
            }
        )
        return Decimal("0")

    if decimal_value < 0:
        warnings.append(
            {
                "sheet": sheet_name,
                "row": str(row_number),
                "column": header,
                "message": f"Negative value '{value}' converted to 0.",
            }
        )
        return Decimal("0")

    return decimal_value


def _format_number(value: Decimal) -> int | float:
    return int(value) if value == value.to_integral_value() else float(value)


def _aggregate_sheet(
    sheet_name: str,
    rows: list[dict[str, object]],
    warnings: list[dict[str, str]],
) -> list[dict[str, object]]:
    if not rows:
        return []

    headers = list(rows[0].keys())
    numeric_headers = [header for header in headers if _is_numeric_column(header)]
    key_headers = [header for header in headers if header not in numeric_headers]

    grouped: dict[tuple[object, ...], dict[str, object]] = {}
    duplicate_counts: dict[tuple[object, ...], int] = {}

    for row_index, row in enumerate(rows, start=2):
        normalized_numeric: dict[str, Decimal] = {}
        for header in numeric_headers:
            normalized_numeric[header] = _normalize_numeric_value(
                sheet_name=sheet_name,
                row_number=row_index,
                header=header,
                value=row.get(header),
                warnings=warnings,
            )

        key = tuple(row.get(header) for header in key_headers)
        duplicate_counts[key] = duplicate_counts.get(key, 0) + 1

        if key not in grouped:
            grouped[key] = {header: row.get(header) for header in key_headers}
            for header in numeric_headers:
                grouped[key][header] = Decimal("0")

        for header in numeric_headers:
            grouped[key][header] += normalized_numeric[header]

    aggregated_rows: list[dict[str, object]] = []
    for key, grouped_row in grouped.items():
        if duplicate_counts[key] > 1:
            warnings.append(
                {
                    "sheet": sheet_name,
                    "row": "-",
                    "column": ",".join(key_headers) if key_headers else "all-columns",
                    "message": f"Duplicate rows detected and aggregated ({duplicate_counts[key]} rows).",
                }
            )

        finalized_row: dict[str, object] = {}
        for header, value in grouped_row.items():
            finalized_row[header] = _format_number(value) if isinstance(value, Decimal) else value
        aggregated_rows.append(finalized_row)

    return aggregated_rows


def validate_parsed_input(parsed: dict[str, object]) -> dict[str, object]:
    existing = set(parsed.get("sheet_names", []))
    missing = [sheet for sheet in REQUIRED_SHEETS if sheet not in existing]
    sheets = parsed.get("sheets", {})

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    normalized_sheets: dict[str, dict[str, object]] = {}

    for sheet in missing:
        errors.append(
            {
                "sheet": sheet,
                "message": "Required sheet is missing.",
            }
        )

    if not missing:
        for sheet_name, sheet_data in sheets.items():
            rows = sheet_data.get("rows", [])
            aggregated_rows = _aggregate_sheet(sheet_name, rows, warnings)
            normalized_sheets[sheet_name] = {
                "headers": sheet_data.get("headers", []),
                "row_count": len(aggregated_rows),
                "rows": aggregated_rows,
            }

    validation_status = "failed" if errors else ("passed_with_warnings" if warnings else "passed")

    return {
        "validation_status": validation_status,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "infos": len(normalized_sheets),
        },
        "solve_allowed": len(errors) == 0,
        "normalized_sheets": normalized_sheets,
    }
