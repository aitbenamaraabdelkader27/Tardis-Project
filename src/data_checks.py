"""Check the official snapshot and print an honest quality report."""
import json
from src.data import load_dataset, quality_report


def main():
    report = quality_report(load_dataset())
    assert report["duplicate_route_months"] == 0
    assert report["eligible_rows"] > 0
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
