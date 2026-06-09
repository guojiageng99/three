from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.simulation import SimulationEngine


def main() -> None:
    engine = SimulationEngine()
    engine.jump_to_bookmark("reflection")

    output_dir = ROOT / "submission_docs" / "evidence"
    json_path, md_path = engine.export_evidence_files(output_dir)

    print(f"Evidence exported to: {json_path}")
    print(f"Evidence exported to: {md_path}")


if __name__ == "__main__":
    main()
