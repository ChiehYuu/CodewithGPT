from pathlib import Path

import pandas as pd

from src.io import load_excel, profile_sheets, consolidate_frames


def test_load_and_profile(tmp_path: Path):
    df = pd.DataFrame({"A": [1, 2, None], "B": ["x", "y", "z"]})
    path = tmp_path / "sample.xlsx"
    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)
    frames = load_excel(path)
    assert "Sheet1" in frames
    profiles = profile_sheets(frames)
    assert profiles[0].rows == 3
    combined = consolidate_frames(frames)
    assert combined.shape == df.shape
