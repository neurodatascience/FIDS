from __future__ import annotations

from pathlib import Path

import pytest
from bids import BIDSLayout

from fids.fids import create_fake_bids_dataset


def nb_expected_files(subjects, sessions, datatypes):
    """Compute number of expected files."""
    if not isinstance(subjects, list):
        subjects = [subjects]
    if not isinstance(sessions, list):
        sessions = [sessions]
    if not isinstance(datatypes, list):
        datatypes = [datatypes]

    nb_sessions = 1
    if sessions:
        nb_sessions = sum(x is not None for x in sessions)
        if nb_sessions == 0:
            nb_sessions = 1

    nb_files_per_session = 0
    if "func" in datatypes:
        nb_files_per_session += 4

    if "anat" in datatypes:
        nb_files_per_session += 4

    if "dwi" in datatypes:
        nb_files_per_session += 2

    expected = len(subjects) * nb_sessions * nb_files_per_session
    expected += 1  # need to count ds_desc

    return expected


@pytest.mark.parametrize("subjects", ["01", 1, ["1", "baz"], [1, 2], ["boo", 2]])
@pytest.mark.parametrize("sessions", [None, "01", 1, ["foo", "2"], [1, 2], ["bar", 2]])
@pytest.mark.parametrize("datatypes", ["anat", "func", "dwi", ["anat", "func"]])
def test_fids_smoke(tmp_path, subjects, sessions, datatypes):
    """Smoke test."""
    output_dir = Path() / "tmp"
    output_dir = tmp_path

    create_fake_bids_dataset(
        output_dir=output_dir,
        dataset_type="raw",
        subjects=subjects,
        sessions=sessions,
        datatypes=datatypes,
        tasks=["task"],
    )

    layout = BIDSLayout(output_dir)
    assert len(layout.get_files()) == nb_expected_files(subjects, sessions, datatypes)


@pytest.mark.parametrize(
    "task, runs, events",
    [
        (["rest"], None, None),
        (["rest"], [3], None),
        (["rest", "main"], [1, 3], None),
        (
            ["rest", "main"],
            [1, 3],
            [None, {"onset": [0, 1], "duration": [1, 1], "trial_type": ["red", "blue"]}],
        ),
    ],
)
def test_fids_smoke_task(tmp_path, task, runs, events):
    """Smoke test with task."""
    create_fake_bids_dataset(
        output_dir=tmp_path,
        dataset_type="raw",
        datatypes=["func"],
        tasks=task,
        runs=runs,
        events=events,
    )
