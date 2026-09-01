from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = (
    ROOT
    / "data"
    / "raw"
    / "flights"
    / "year=2026"
    / "month=04"
    / "bts_reporting_carrier_ontime_2026_04.csv"
)

OUTPUT_DIR = ROOT / "docs" / "profiling"
OUTPUT_FILE = OUTPUT_DIR / "BTS_2026_04_PROFILE.md"


# ---------------------------------------------------------
# AirOps 360 Data Contract v0.1 expectations
# ---------------------------------------------------------

REQUIRED_FIELDS = [
    "FlightDate",
    "Reporting_Airline",
    "Flight_Number_Reporting_Airline",
    "Origin",
    "Dest",
    "CRSDepTime",
    "DepTime",
    "DepDelay",
    "CRSArrTime",
    "ArrTime",
    "ArrDelay",
    "Cancelled",
    "Diverted",
    "AirTime",
    "Distance",
    "CarrierDelay",
    "WeatherDelay",
    "NASDelay",
    "SecurityDelay",
    "LateAircraftDelay",
]

CANDIDATE_KEY = [
    "FlightDate",
    "Reporting_Airline",
    "Flight_Number_Reporting_Airline",
    "Origin",
    "Dest",
    "CRSDepTime",
]


def markdown_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for row in rows:
        clean = [str(value).replace("|", "\\|") for value in row]
        lines.append("| " + " | ".join(clean) + " |")

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("AirOps 360 - BTS April 2026 Source Profile")
    print("=" * 70)

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"\nExpected BTS file was not found:\n{RAW_FILE}\n"
            "\nRename the extracted April CSV to:\n"
            "bts_reporting_carrier_ontime_2026_04.csv"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nReading:\n{RAW_FILE}")

    df = pd.read_csv(RAW_FILE, low_memory=False)

    # Strip accidental spaces around source column names.
    df.columns = [str(col).strip() for col in df.columns]

    row_count = len(df)
    column_count = len(df.columns)

    print(f"\nRows:    {row_count:,}")
    print(f"Columns: {column_count:,}")

    # -----------------------------------------------------
    # Required-field validation
    # -----------------------------------------------------

    present_required = [
        field for field in REQUIRED_FIELDS if field in df.columns
    ]

    missing_required = [
        field for field in REQUIRED_FIELDS if field not in df.columns
    ]

    # -----------------------------------------------------
    # Schema and null profile
    # -----------------------------------------------------

    schema_rows = []

    for column in df.columns:
        null_count = int(df[column].isna().sum())
        null_pct = (
            (null_count / row_count) * 100
            if row_count
            else 0
        )

        schema_rows.append(
            [
                column,
                str(df[column].dtype),
                f"{null_count:,}",
                f"{null_pct:.2f}%",
            ]
        )

    # -----------------------------------------------------
    # Date coverage
    # -----------------------------------------------------

    if "FlightDate" in df.columns:
        parsed_dates = pd.to_datetime(
            df["FlightDate"],
            errors="coerce",
        )

        valid_dates = parsed_dates.dropna()

        date_parse_failures = int(parsed_dates.isna().sum())

        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            april_mask = (
                (parsed_dates.dt.year == 2026)
                & (parsed_dates.dt.month == 4)
            )

            out_of_april_rows = int(
                parsed_dates.notna().sum()
                - april_mask.sum()
            )
        else:
            min_date = "N/A"
            max_date = "N/A"
            out_of_april_rows = 0
    else:
        min_date = "MISSING"
        max_date = "MISSING"
        date_parse_failures = row_count
        out_of_april_rows = row_count

    # -----------------------------------------------------
    # Candidate-key profile
    # -----------------------------------------------------

    key_fields_available = all(
        field in df.columns
        for field in CANDIDATE_KEY
    )

    key_null_rows = None
    complete_key_rows = None
    unique_key_rows = None
    duplicate_key_rows = None
    duplicate_key_groups = None
    uniqueness_pct = None

    if key_fields_available:
        key_has_null = df[CANDIDATE_KEY].isna().any(axis=1)

        key_null_rows = int(key_has_null.sum())

        complete_keys = df.loc[
            ~key_has_null,
            CANDIDATE_KEY
        ].copy()

        complete_key_rows = len(complete_keys)

        duplicate_mask = complete_keys.duplicated(
            keep=False
        )

        duplicate_key_rows = int(duplicate_mask.sum())

        if duplicate_key_rows:
            duplicate_key_groups = (
                complete_keys.loc[duplicate_mask]
                .groupby(
                    CANDIDATE_KEY,
                    dropna=False,
                )
                .ngroups
            )
        else:
            duplicate_key_groups = 0

        unique_key_rows = len(
            complete_keys.drop_duplicates()
        )

        uniqueness_pct = (
            unique_key_rows
            / complete_key_rows
            * 100
            if complete_key_rows
            else 0
        )

    # -----------------------------------------------------
    # Top origin airports
    # -----------------------------------------------------

    top_airports_rows = []

    if "Origin" in df.columns:
        origin_counts = (
            df["Origin"]
            .dropna()
            .astype(str)
            .value_counts()
            .head(20)
        )

        for rank, (airport, count) in enumerate(
            origin_counts.items(),
            start=1,
        ):
            pct = (
                count / row_count * 100
                if row_count
                else 0
            )

            top_airports_rows.append(
                [
                    rank,
                    airport,
                    f"{count:,}",
                    f"{pct:.2f}%",
                ]
            )

    # -----------------------------------------------------
    # Cancellation/diversion domain observations
    # -----------------------------------------------------

    domains = {}

    for column in ["Cancelled", "Diverted"]:
        if column in df.columns:
            values = (
                df[column]
                .dropna()
                .value_counts()
                .sort_index()
            )

            domains[column] = [
                (value, int(count))
                for value, count in values.items()
            ]

    # -----------------------------------------------------
    # Candidate-key component nulls
    # -----------------------------------------------------

    key_null_details = []

    if key_fields_available:
        for field in CANDIDATE_KEY:
            null_count = int(df[field].isna().sum())

            null_pct = (
                null_count / row_count * 100
                if row_count
                else 0
            )

            key_null_details.append(
                [
                    field,
                    f"{null_count:,}",
                    f"{null_pct:.4f}%",
                ]
            )

    # -----------------------------------------------------
    # Build Markdown artifact
    # -----------------------------------------------------

    generated_at = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d %H:%M:%S UTC")

    report = []

    report.append("# BTS April 2026 Source Profile v0.1")
    report.append("")
    report.append(f"**Generated:** {generated_at}")
    report.append("")
    report.append(
        "**Dataset:** Reporting Carrier On-Time Performance"
    )
    report.append("")
    report.append("**Source period:** April 2026")
    report.append("")
    report.append(
        "**Purpose:** Validate AirOps 360 Data Contract v0.1 "
        "against the actual BTS April 2026 source before "
        "Bronze/Silver implementation."
    )

    report.append("")
    report.append("## 1. Source summary")
    report.append("")
    report.append(
        markdown_table(
            ["Metric", "Observed"],
            [
                ["Source row count", f"{row_count:,}"],
                ["Source column count", f"{column_count:,}"],
                ["Minimum FlightDate", min_date],
                ["Maximum FlightDate", max_date],
                [
                    "FlightDate parse failures",
                    f"{date_parse_failures:,}",
                ],
                [
                    "Rows outside April 2026",
                    f"{out_of_april_rows:,}",
                ],
            ],
        )
    )

    report.append("")
    report.append("## 2. Required contract fields")
    report.append("")

    report.append(
        f"Required fields expected: **{len(REQUIRED_FIELDS)}**"
    )
    report.append("")
    report.append(
        f"Required fields present: **{len(present_required)}**"
    )
    report.append("")
    report.append(
        f"Required fields missing: **{len(missing_required)}**"
    )
    report.append("")

    if missing_required:
        report.append("Missing required fields:")
        report.append("")
        for field in missing_required:
            report.append(f"- `{field}`")
    else:
        report.append(
            "**Result: all required AirOps 360 v0.1 "
            "BTS fields are present.**"
        )

    report.append("")
    report.append("## 3. Candidate business-key profile")
    report.append("")

    report.append("Candidate key:")
    report.append("")
    report.append("```text")
    for field in CANDIDATE_KEY:
        report.append(field)
    report.append("```")
    report.append("")

    if key_fields_available:
        report.append(
            markdown_table(
                ["Metric", "Observed"],
                [
                    [
                        "Total source rows",
                        f"{row_count:,}",
                    ],
                    [
                        "Rows with null candidate-key component",
                        f"{key_null_rows:,}",
                    ],
                    [
                        "Rows with complete candidate key",
                        f"{complete_key_rows:,}",
                    ],
                    [
                        "Distinct complete candidate keys",
                        f"{unique_key_rows:,}",
                    ],
                    [
                        "Rows involved in duplicate candidate keys",
                        f"{duplicate_key_rows:,}",
                    ],
                    [
                        "Duplicate candidate-key groups",
                        f"{duplicate_key_groups:,}",
                    ],
                    [
                        "Complete-key uniqueness",
                        f"{uniqueness_pct:.6f}%",
                    ],
                ],
            )
        )

        report.append("")
        report.append(
            "### Candidate-key component nulls"
        )
        report.append("")

        report.append(
            markdown_table(
                ["Field", "Null count", "Null %"],
                key_null_details,
            )
        )

        report.append("")

        if (
            key_null_rows == 0
            and duplicate_key_rows == 0
        ):
            report.append(
                "**Observed result: the provisional candidate "
                "business key is unique for the April 2026 "
                "source extract.**"
            )
        else:
            report.append(
                "**Observed result: the provisional candidate "
                "business key requires review. This profiling "
                "artifact records the evidence; the Data Contract "
                "must not be changed silently.**"
            )
    else:
        report.append(
            "**Candidate-key test could not run because one or "
            "more key fields are missing from the source.**"
        )

    report.append("")
    report.append("## 4. Top origin airports")
    report.append("")

    if top_airports_rows:
        report.append(
            markdown_table(
                [
                    "Rank",
                    "Origin",
                    "Flights",
                    "Share of source",
                ],
                top_airports_rows,
            )
        )
    else:
        report.append("`Origin` was not available.")

    report.append("")
    report.append(
        "> The top-airport ranking is profiling evidence. "
        "The final AirOps weather-airport scope should be frozen "
        "only after this evidence is reviewed."
    )

    report.append("")
    report.append("## 5. Cancelled / Diverted observed domains")
    report.append("")

    for column, values in domains.items():
        report.append(f"### {column}")
        report.append("")

        domain_rows = [
            [str(value), f"{count:,}"]
            for value, count in values
        ]

        report.append(
            markdown_table(
                ["Value", "Row count"],
                domain_rows,
            )
        )
        report.append("")

    report.append("## 6. Full schema and null profile")
    report.append("")
    report.append(
        "> `Observed dtype` is pandas source inference, not the "
        "final AirOps Silver logical type."
    )
    report.append("")

    report.append(
        markdown_table(
            [
                "Column",
                "Observed dtype",
                "Null count",
                "Null %",
            ],
            schema_rows,
        )
    )

    report.append("")
    report.append("## 7. Contract decision")
    report.append("")
    report.append(
        "This document records source-profiling evidence only."
    )
    report.append("")
    report.append(
        "No AirOps 360 data-contract assumption should be "
        "changed silently as part of profiling."
    )
    report.append("")
    report.append(
        "If source grain, required-field presence, candidate-key "
        "uniqueness, or domain behavior differs from Data Contract "
        "v0.1, the discrepancy must be reviewed and documented "
        "before implementation changes are made."
    )

    OUTPUT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # Terminal summary
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("PROFILE COMPLETE")
    print("=" * 70)

    print(f"\nRows: {row_count:,}")
    print(f"Columns: {column_count:,}")

    print(
        f"Required fields missing: "
        f"{len(missing_required)}"
    )

    if missing_required:
        print(
            "Missing:",
            ", ".join(missing_required),
        )

    if key_fields_available:
        print(
            f"Candidate-key null rows: "
            f"{key_null_rows:,}"
        )

        print(
            f"Duplicate candidate-key rows: "
            f"{duplicate_key_rows:,}"
        )

        print(
            f"Duplicate candidate-key groups: "
            f"{duplicate_key_groups:,}"
        )

        print(
            f"Complete-key uniqueness: "
            f"{uniqueness_pct:.6f}%"
        )

    if top_airports_rows:
        print("\nTop 15 origin airports:")

        for row in top_airports_rows[:15]:
            print(
                f"{row[0]:>2}. "
                f"{row[1]:<5} "
                f"{row[2]:>10} "
                f"({row[3]})"
            )

    print(
        f"\nProfile artifact written to:\n"
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()