from future import __annotations__
from bids import BIDSLayout
from pathlib import Path
import json

DEFAUTL_NIFTI_EXT = ".nii.gz"

def dataset_description(dataset_type):
    return {
        "BIDSVersion": "1.8.0",
        "Name": dataset_type,
        "dataset_type": dataset_type,
    }

def write_readme(output_dir: Path):
    with open(output_dir / "README.md", "w") as f:
        f.write("This is a fake BIDS dataset")

def bids_fitler_file():
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
