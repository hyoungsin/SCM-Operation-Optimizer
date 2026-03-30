def normalize_input(parsed: dict[str, object]) -> dict[str, object]:
    return {
        "status": "normalized",
        "sheet_names": parsed.get("sheet_names", []),
        "notes": [
            "Placeholder normalization module",
            "Future rules: duplicate aggregation, negative/null to zero, warning history",
        ],
    }
