"""End to end test that generates a complex dataset."""
from __future__ import annotations

import json
from pathlib import Path

from fids.fids import create_fake_bids_dataset

SUBJECTS = ["ctrl01", "blind01", "01"]
SESSIONS = ["01", "02"]

output_dir = Path() / "tmp"

# %%
# ANAT

bids_filter = {
    "anat": {"suffix": ["UNIT1", "T1w"], "entities": {"extension": ".nii"}},
}

create_fake_bids_dataset(
    output_dir=output_dir,
    subjects=SUBJECTS,
    sessions=SESSIONS[0],
    bids_filter=bids_filter,
    add_sidecar=False,
)

for inv, InversionTime in zip([1, 2], [1, 3.2]):
    bids_filter = {
        "anat": {
            "suffix": ["MP2RAGE"],
            "entities": {"inv": inv, "extension": ".nii"},
            "metadata": {
                "MagneticFieldStrength": 7,
                "RepetitionTimePreparation": 4.3,
                "InversionTime": InversionTime,
                "FlipAngle": 4,
                "FatSat": "yes",
                "EchoSpacing": 0.0072,
                "PartialFourierInSlice": 0.75,
            },
        },
    }
    create_fake_bids_dataset(
        output_dir=output_dir,
        subjects=SUBJECTS,
        sessions=SESSIONS[0],
        bids_filter=bids_filter,
        add_sidecar=True,
    )

filepath = output_dir / "T1w.json"
metadata = {
    "Modality": "MR",
    "RepetitionTime": 2.3,
    "PhaseEncodingDirection": "j-",
    "EchoTime": 0.00226,
    "InversionTime": 0.9,
    "SliceThickness": 1,
    "FlipAngle": 8,
}

with open(filepath, "w") as f:
    json.dump(metadata, f, indent=4)

#  %%
#  FUNC

metadata_rest = {
    "ImageType": "ORIGINAL\\PRIMARY\\M\\ND\\MOSAIC",
    "Modality": "MR",
    "TotalReadoutTime": 1.0035123,
    "SliceTiming": [
        0.5475,
        0,
        0.3825,
        0.055,
        0.4375,
        0.11,
        0.4925,
        0.22,
        0.6025,
        0.275,
        0.6575,
        0.3275,
        0.71,
        0.165,
        0.5475,
        0,
        0.3825,
        0.055,
        0.4375,
        0.11,
        0.4925,
        0.22,
        0.6025,
        0.275,
        0.6575,
        0.3275,
        0.71,
        0.165,
        0.5475,
        0,
        0.3825,
        0.055,
        0.4375,
        0.11,
        0.4925,
        0.22,
        0.6025,
        0.275,
        0.6575,
        0.3275,
        0.71,
        0.165,
    ],
    "RepetitionTime": 1.5,
    "PhaseEncodingDirection": "j-",
    "EffectiveEchoSpacing": 0.00024499812,
    "EchoTime": 0.03,
    "SliceThickness": 3,
    "FlipAngle": 54,
    "NumberOfVolumesDiscardedByUser": 8,
    "TaskName": "vismotion",
}

metadata_vismotion = {
    "ImageType": "ORIGINAL\\PRIMARY\\M\\ND\\MOSAIC",
    "Modality": "MR",
    "TotalReadoutTime": 1.0035123,
    "SliceTiming": [
        0.5475,
        0,
        0.3825,
        0.055,
        0.4375,
        0.11,
        0.4925,
        0.22,
        0.6025,
        0.275,
        0.6575,
        0.3275,
        0.71,
        0.165,
        0.5475,
        0,
        0.3825,
        0.055,
        0.4375,
        0.11,
        0.4925,
        0.22,
        0.6025,
        0.275,
        0.6575,
        0.3275,
        0.71,
        0.165,
        0.5475,
        0,
        0.3825,
        0.055,
        0.4375,
        0.11,
        0.4925,
        0.22,
        0.6025,
        0.275,
        0.6575,
        0.3275,
        0.71,
        0.165,
    ],
    "RepetitionTime": 1.5,
    "PhaseEncodingDirection": "j-",
    "EffectiveEchoSpacing": 0.00024499812,
    "EchoTime": 0.03,
    "SliceThickness": 3,
    "FlipAngle": 54,
    "NumberOfVolumesDiscardedByUser": 8,
    "TaskName": "vismotion",
    "PixelBandwidth": 15.873,
}

# BOLD
bids_filter = {
    "func": {
        "suffix": ["bold"],
        "entities": {"extension": ".nii"},
        "metadata": metadata_rest,
    },
}
create_fake_bids_dataset(
    output_dir=output_dir,
    subjects=SUBJECTS,
    sessions=SESSIONS,
    tasks=["rest"],
    bids_filter=bids_filter,
    add_sidecar=False,
)

for part in ["mag", "phase"]:
    bids_filter = {
        "func": {
            "suffix": ["bold"],
            "entities": {"part": part, "extension": ".nii"},
            "metadata": metadata_vismotion,
        },
    }
    create_fake_bids_dataset(
        output_dir=output_dir,
        subjects=SUBJECTS,
        sessions=SESSIONS,
        tasks=["vismotion"],
        runs=[2],
        bids_filter=bids_filter,
        add_sidecar=False,
        padding=False,
    )


bids_filter = {
    "func": {
        "suffix": ["bold"],
        "entities": {"acquisition": "1p60mm", "extension": ".nii"},
        "metadata": metadata_vismotion,
    },
}
create_fake_bids_dataset(
    output_dir=output_dir,
    subjects=SUBJECTS,
    sessions=SESSIONS,
    tasks=["vismotion"],
    runs=[1],
    bids_filter=bids_filter,
    add_sidecar=False,
    padding=False,
)

bids_filter = {
    "func": {
        "suffix": ["bold"],
        "entities": {"acquisition": "1p60mm", "direction": "PA", "extension": ".nii"},
        "metadata": metadata_vismotion,
    },
}
create_fake_bids_dataset(
    output_dir=output_dir,
    subjects=SUBJECTS,
    sessions=SESSIONS,
    tasks=["vismotion"],
    runs=[2],
    bids_filter=bids_filter,
    add_sidecar=False,
    padding=False,
)

# EVENTS
bids_filter = {
    "func": {"suffix": ["events"]},
}
onset = [3, 6]
duration = [2, 2]
trial_type = ["VisStat", "VisMot"]
create_fake_bids_dataset(
    output_dir=output_dir,
    subjects=SUBJECTS,
    sessions=SESSIONS,
    tasks=["vismotion"],
    runs=[2],
    events=[{"onset": onset, "duration": duration, "trial_type": trial_type}],
    bids_filter=bids_filter,
    add_sidecar=False,
    padding=False,
)

onset = [2, 4]
duration = [2, 2]
trial_type = ["VisMot", "VisStat"]
create_fake_bids_dataset(
    output_dir=output_dir,
    subjects=SUBJECTS,
    sessions=SESSIONS,
    tasks=["vismotion"],
    runs=[1],
    events=[{"onset": onset, "duration": duration, "trial_type": trial_type}],
    bids_filter=bids_filter,
    add_sidecar=False,
    padding=False,
)

bids_filter = {
    "func": {"suffix": ["events"], "entities": {"acquisition": "1p60mm"}},
}
onset = [4, 8]
duration = [2, 2]
trial_type = ["VisMot", "VisStat"]
create_fake_bids_dataset(
    output_dir=output_dir,
    subjects=SUBJECTS,
    sessions=SESSIONS,
    tasks=["vismotion"],
    runs=[2],
    events=[{"onset": onset, "duration": duration, "trial_type": trial_type}],
    bids_filter=bids_filter,
    add_sidecar=False,
    padding=False,
)

filepath = output_dir / "task-rest_bold.json"
with open(filepath, "w") as f:
    json.dump(metadata_rest, f, indent=4)

filepath = output_dir / "task-vismotion_bold.json"
with open(filepath, "w") as f:
    json.dump(metadata_vismotion, f, indent=4)
