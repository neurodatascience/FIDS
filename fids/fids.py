"""FIDS main module."""
from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import Any

import nibabel as nib
import numpy as np
import pandas as pd
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


def bids_filter_default() -> dict[str, dict[str, list[str]]]:
    """Return a dictionary of suffixes for each datatype."""
    return {
        "fmap": {},
        "func": {"suffix": ["bold", "events"]},
        "dwi": {"suffix": ["dwi"]},
        "anat": {"suffix": ["T1w", "T2w"]},
    }


def create_fake_bids_dataset(
    output_dir: Path | None = None,
    dataset_type: str = "raw",
    subjects: str | int | list[str | int] = "01",
    sessions: None | str | int | list[str | int | None] = "01",
    datatypes: str | list[str] | None = None,
    tasks: str | list[str] | None = None,
    runs: list[int] | None = None,
    events: list[dict[str, float | str]] | None = None,
    bids_filter: dict[str, dict[str, list[str] | dict[str, str]]] | None = None,
    add_sidecar: bool = True,
    padding=True,
) -> None:
    """Create a fake BIDS dataset."""
    (
        output_dir,
        subjects,
        sessions,
        datatypes,
        tasks,
        runs,
        events,
        bids_filter,
    ) = _sanitize_inputs(
        output_dir, subjects, sessions, datatypes, tasks, runs, events, bids_filter
    )

    Path.mkdir(output_dir, parents=True, exist_ok=True)

    with open(output_dir / "dataset_description.json", "w") as f:
        json.dump(dataset_description(dataset_type), f, indent=4)

    layout = BIDSLayout(output_dir, validate=False)

    for sub_label, ses_label, datatype_ in product(
        subjects,
        sessions,
        datatypes,
    ):
        if "suffix" not in bids_filter[datatype_]:
            continue
        for suffix_ in bids_filter[datatype_]["suffix"]:
            entities = _compile_entities(
                sub_label,
                datatype=datatype_,
                suffix=suffix_,
                ses_label=ses_label,
                bids_filter=bids_filter,
            )

            metadata = None
            if "metadata" in bids_filter[datatype_]:
                metadata = bids_filter[datatype_]["metadata"]

            if datatype_ in ["anat", "dwi"]:
                create_dummy_file(layout=layout, entities=entities, metadata=metadata)
                create_sidecar(
                    layout=layout,
                    entities=entities,
                    add_sidecar=add_sidecar,
                    metadata=metadata,
                )

            if datatype_ == "func":
                for task_, nb_runs, event in zip(tasks, runs, events):
                    entities["task"] = task_
                    if not nb_runs:
                        create_dummy_file(
                            layout=layout,
                            entities=entities,
                            events=event,
                            metadata=metadata,
                        )
                        create_sidecar(
                            layout=layout,
                            entities=entities,
                            add_sidecar=add_sidecar,
                            metadata=metadata,
                        )
                        continue

                    for i_run in range(1, nb_runs + 1):
                        entities["run"] = f"{i_run}"
                        if padding:
                            entities["run"] = f"{i_run:02.0f}"
                        create_dummy_file(
                            layout=layout,
                            entities=entities,
                            events=event,
                            metadata=metadata,
                        )
                        create_sidecar(
                            layout=layout,
                            entities=entities,
                            add_sidecar=add_sidecar,
                            metadata=metadata,
                        )


def _sanitize_inputs(
    output_dir, subjects, sessions, datatypes, tasks, runs, events, bids_filter
):
    if output_dir is None:
        output_dir = Path.cwd() / "sourcedata" / "fids"

    if isinstance(subjects, (str, int)):
        subjects = [subjects]

    if sessions is None:
        sessions = [None]
    elif isinstance(sessions, (str, int)):
        sessions = [sessions]

    if tasks is None:
        tasks = ["rest"]
    if isinstance(tasks, (str)):
        tasks = [tasks]

    if not isinstance(runs, list):
        runs = [runs]

    if not isinstance(events, list):
        events = [events]

    if bids_filter is None:
        bids_filter = bids_filter_default()

    if datatypes is None:
        datatypes = list(bids_filter.keys())
    if isinstance(datatypes, (str)):
        datatypes = [datatypes]
    datatypes = list(set(datatypes).intersection(set(bids_filter.keys())))

    return output_dir, subjects, sessions, datatypes, tasks, runs, events, bids_filter


def _compile_entities(sub_label, datatype, suffix, ses_label, bids_filter):
    entities = {
        "subject": sub_label,
        "datatype": datatype,
        "suffix": suffix,
        "extension": DEFAUTL_NIFTI_EXT,
    }
    if ses_label:
        entities["session"] = ses_label

    if "entities" in bids_filter[datatype]:
        entities = {**entities, **bids_filter[datatype]["entities"]}

    if suffix == "events":
        entities["extension"] = ".tsv"

    return entities


def create_dummy_file(
    layout: BIDSLayout,
    entities: dict[str, str | int],
    events: list[dict[str, float | str]] | None = None,
    metadata=None,
) -> None:
    """Create an empty file."""
    filepath = layout.build_path(
        source=entities,
        validate=False,
    )
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    nb_slices = None
    if metadata and "SliceTiming" in metadata:
        nb_slices = len(metadata["SliceTiming"])

    if entities["extension"] in [".nii", ".nii.gz"]:
        image = _img_3d_rand_eye(nb_slices=nb_slices)
        if entities["datatype"] in ["func", "dwi"]:
            max_time_secs = 10
            if events:
                max_time_secs = max(events["onset"]) + max(events["duration"])

            tr = None
            nb_vol = None
            if metadata and "RepetitionTime" in metadata:
                tr = metadata["RepetitionTime"]
                nb_vol = int(max_time_secs / tr)

            image = _img_4d_rand_eye(nb_slices=nb_slices, nb_vol=nb_vol)

            if tr:
                image = set_tr(image, tr)

        image.header.set_xyzt_units(t=8, xyz=2)

        nib.save(image, filepath)

    if entities["extension"] in [".tsv"]:
        df = pd.DataFrame(events)
        df.to_csv(filepath, index=False, sep="\t")

    else:
        filepath.touch()


def create_sidecar(
    layout: BIDSLayout,
    entities: dict[str, str | int],
    metadata: None | dict[str, Any] = None,
    add_sidecar: bool = True,
) -> None:
    """Create a sidecar JSON file."""
    if not add_sidecar:
        return
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
    return [10, 10, 10]


def _length_default():
    return 10


def _shape_4d_default():
    """Return default shape for a 4D image."""
    return [10, 10, 10, _length_default()]


def _img_3d_rand_eye(affine=_affine_eye(), nb_slices=None):
    """Return random 3D Nifti1Image in MNI space."""
    shape = _shape_3d_default()
    if nb_slices:
        shape[2] = nb_slices
    data = _rng().random(shape)
    return Nifti1Image(data, affine)


def _img_4d_rand_eye(affine=_affine_eye(), nb_slices=None, nb_vol=None):
    """Return random 3D Nifti1Image in MNI space."""
    shape = _shape_4d_default()
    if nb_slices:
        shape[2] = nb_slices
    if nb_vol:
        shape[3] = nb_vol
    data = _rng().random(shape)
    return Nifti1Image(data, affine)


def set_tr(img, tr):
    """Set repetition time in an image header."""
    header = img.header.copy()
    zooms = header.get_zooms()[:3] + (tr,)
    header.set_zooms(zooms)
    return img.__class__(img.get_fdata().copy(), img.affine, header)


if __name__ == "__main__":
    create_fake_bids_dataset()
