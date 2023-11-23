# FIDS

> Is to the Brain imaging data structure (BIDS) what the facon is to bacon.


## Install

```
pip install .
```

## Usage

```python
from pathfile import Path
from fids.fids import create_fake_bids_dataset

subjects = ["foo", 2, "01"]
sessions = [1, "mri"]
datatypes = ["anat", "func"]

create_fake_bids_dataset(
    output_dir=Path.cwd() / "sourcedata" / "fids",
    dataset_type="raw",
    subjects=subjects,
    sessions=sessions,
    datatypes=datatypes,
    tasks=["rest"],
)
```

## Similar projects

- [f-ake-mriprep](https://github.com/djarecka/fmriprep-fake)
- [nilearn's data_gen utils](https://github.com/nilearn/nilearn/blob/91218eb8548574621fe5a1eca6d8a889b12a826f/nilearn/_utils/data_gen.py#L858)
