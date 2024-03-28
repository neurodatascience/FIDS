from __future__ import annotations

import pytest

from fids.fids import create_fake_bids_dataset


@pytest.mark.parametrize("subjects", ["01", 1, ["1", "baz"], [1, 2], ["boo", 2]])
@pytest.mark.parametrize("sessions", [None, "01", 1, ["foo", "2"], [1, 2], ["bar", 2]])
@pytest.mark.parametrize("datatypes", ["anat", "func", "dwi", ["anat", "func"]])
def test_fids_smoke(tmp_path, subjects, sessions, datatypes):
    """Smoke test."""
    create_fake_bids_dataset(
        output_dir=tmp_path,
        dataset_type="raw",
        subjects=subjects,
        sessions=sessions,
        datatypes=datatypes,
        tasks=["rest"],
    )
