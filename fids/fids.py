"""FIDS main module."""
import json
from pathlib import Path

from bids import BIDSLayout
from future import __annotations__  # noqa

DEFAUTL_NIFTI_EXT = ".nii.gz"


def dataset_description(dataset_type):
    """Return a dataset_description."""
    return {
        "BIDSVersion": "1.8.0",
        "Name": dataset_type,
        "dataset_type": dataset_type,
    }


def write_readme(output_dir: Path):
    """Write a README.md file."""
    with open(output_dir / "README.md", "w") as f:
        f.write("This is a fake BIDS dataset")


def bids_fitler_file():
    """Return a dictionary of suffixes for each datatype."""
    return {
        "fmap": {},
        "func": {"suffix": ["bold", "events"]},
        "anat": {"suffix": ["T1w"]},
    }


def fids(
    output_dir: Path = Path.cwd() / "sourcedata" / "fids",
    dataset_type: str = "raw",
    subjects: str | int = "01",
    sessions: None | str | int = "01",
    datatypes: str | list[str] = ["anat", "func"],
    tasks: str | list[str] = ["rest"],
):
    """Create a fake BIDS dataset."""
    if isinstance(subjects, str):
        subjects = [subjects]

    if isinstance(sessions, str):
        sessions = [sessions]
    if sessions is None:
        sessions = [None]

    Path.mkdir(output_dir, parents=True, exist_ok=True)

    with open(output_dir / "dataset_description.json", "w") as f:
        json.dump(dataset_description(dataset_type), f, indent=4)

    layout = BIDSLayout(output_dir, validate=False)

    for sub_label in subjects:
        entities = {"subject": sub_label}
        for ses_label in sessions:
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


def create_empty_file(layout: BIDSLayout, entities: dict[str, str]):
    """Create an empty file."""
    filepath = layout.build_path(
        source=entities,
        validate=False,
    )
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.touch()


def create_sidecar(
    layout: BIDSLayout, entities: dict[str, str], metadata: dict[str, str] = None
):
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


if __name__ == "__main__":
    fids()
