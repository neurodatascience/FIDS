"""FIDS main module."""
from __future__ import annotations

import json
from pathlib import Path

import nibabel as nib
import numpy as np
from bids import BIDSLayout
from nibabel import Nifti1Image


DEFAUTL_NIFTI_EXT = ".nii.gz"


def dataset_description(dataset_type: str) -> dict[str, str]:
    """Return a dataset_description."""
    return {
        "BIDSVersion": "1.8.0",
        "Name": dataset_type,
        "dataset_type": dataset_type,
    }


def write_readme(output_dir: Path) -> None:
    """Write a README.md file."""
    with open(output_dir / "README.md", "w") as f:
        f.write("This is a fake BIDS dataset")


def bids_fitler_file() -> dict[str, dict[str, list[str]]]:
    """Return a dictionary of suffixes for each datatype."""
    return {
        "fmap": {},
        "func": {"suffix": ["bold", "events"]},
        "dwi": {"suffix": ["dwi"]},
        "anat": {"suffix": ["T1w", "T2w"]},
    }


def create_fake_bids_dataset(
    output_dir: Path = Path.cwd() / "sourcedata" / "fids",
    dataset_type: str = "raw",
    subjects: str | int | list[str | int] = "01",
    sessions: None | str | int | list[str | int | None] = "01",
    datatypes: str | list[str] = ["anat", "func"],
    tasks: str | list[str] = ["rest"],
) -> None:
    """Create a fake BIDS dataset."""
    if isinstance(subjects, (str, int)):
        subjects_to_create = [subjects]
    else:
        subjects_to_create = subjects

    if sessions is None:
        sessions_to_create = [None]
    elif isinstance(sessions, (str, int)):
        sessions_to_create = [sessions]
    else:
        sessions_to_create = sessions

    if isinstance(datatypes, (str)):
        datatypes = [datatypes]

    Path.mkdir(output_dir, parents=True, exist_ok=True)

    with open(output_dir / "dataset_description.json", "w") as f:
        json.dump(dataset_description(dataset_type), f, indent=4)

    layout = BIDSLayout(output_dir, validate=False)

    for sub_label in subjects_to_create:
        entities = {"subject": sub_label}
        for ses_label in sessions_to_create:
            if ses_label:
                entities["session"] = ses_label
            for datatype_ in datatypes:
                entities["datatype"] = datatype_
                for suffix_ in bids_fitler_file()[datatype_]["suffix"]:
                    entities["suffix"] = suffix_
                    entities["extension"] = DEFAUTL_NIFTI_EXT
                    if suffix_ == "events":
                        entities["extension"] = ".tsv"
                    if datatype_ == "anat":
                        create_empty_file(layout=layout, entities=entities)
                        create_sidecar(layout=layout, entities=entities)
                    if datatype_ == "func":
                        for task_ in tasks:
                            entities["task"] = task_
                            create_empty_file(layout=layout, entities=entities)
                            create_sidecar(layout=layout, entities=entities)


def create_empty_file(layout: BIDSLayout, entities: dict[str, str | int]) -> None:
    """Create an empty file."""
    filepath = layout.build_path(
        source=entities,
        validate=False,
    )
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if entities["extension"] in [".nii", ".nii.gz"]:
        image = _img_3d_rand_eye()
        if entities["datatype"] in ["func", "dwi"]:
            image = _img_4d_rand_eye()
        nib.save(image, filepath)
    else:
        filepath.touch()


def create_sidecar(
    layout: BIDSLayout,
    entities: dict[str, str | int],
    metadata: None | dict[str, str] = None,
) -> None:
    """Create a sidecar JSON file."""
    entities["extension"] = ".json"
    filepath = layout.build_path(
        source=entities,
        validate=False,
    )
    if metadata is None:
        metadata = {}
    with open(filepath, "w") as f:
        json.dump(metadata, f, indent=4)


def _rng(seed=42):
    return np.random.default_rng(seed)


def _affine_eye():
    """Return an identity matrix affine."""
    return np.eye(4)


def _shape_3d_default():
    """Return default shape for a 3D image."""
    return (10, 10, 10)


def _length_default():
    return 10


def _shape_4d_default():
    """Return default shape for a 4D image."""
    return (10, 10, 10, _length_default())


def _img_3d_rand_eye(affine=_affine_eye()):
    """Return random 3D Nifti1Image in MNI space."""
    data = _rng().random(_shape_3d_default())
    return Nifti1Image(data, affine)


def _img_4d_rand_eye(affine=_affine_eye()):
    """Return random 3D Nifti1Image in MNI space."""
    data = _rng().random(_shape_4d_default())
    return Nifti1Image(data, affine)


if __name__ == "__main__":
    create_fake_bids_dataset()
