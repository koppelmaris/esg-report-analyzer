"""Main pipeline."""

import json
import shutil
from pathlib import Path

from app.pipeline import ingest_multiple
from app.qa import analyze_company

COMPANIES = {
    "Tallink Grupp": [
        "https://image.tallink.com/image/upload/grupp/documents/sustainability-reports/Tallink-Grupp-Sustainability-Report-2024-ENG-updated.pdf",
    ],
    "Eesti Energia": [
        "https://public-docs.enefit.com/ettevottest/investorile/eesti-energia-2025-final-en.pdf",
        "https://public-docs.enefit.ee/ettevottest/investorile/ESG/Eesti-SPO-UoP.pdf",
    ],
}


def run() -> None:
    """Run the full ESG analysis pipeline for all companies."""
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    results = {}

    for company, urls in COMPANIES.items():
        print(f"\nProcessing {company}...")
        vectorstore = ingest_multiple(urls)
        report = analyze_company(company, vectorstore)
        results[company] = report.model_dump()
        print(f"Done: {company}")

    output_path = output_dir / "output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nOutput saved to {output_path}")

    ui_public = Path("ui/public/output.json")
    if ui_public.parent.exists():
        shutil.copy(output_path, ui_public)


if __name__ == "__main__":
    run()
