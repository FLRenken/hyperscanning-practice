
import json
from pathlib import Path
import numpy as np
import pandas as pd
import mne

config = json.loads(Path("data/config.json").read_text())
DATASET_PATH = Path(config["dataset_path"]).expanduser()
assert DATASET_PATH.exists(), "external disk not mounted?"

DERIV = Path(config["derivatives_path"]) / "epochs"
DERIV.mkdir(parents=True, exist_ok=True)

RESULTS = Path("results.json")

NON_EEG = {"VEOG_b", "VEOG_a", "HEOG_l", "HEOG_r", "ref_lm"}


def preprocess_subject(sub, tmin=2.0, tmax=15.0):
    raw = mne.io.read_raw_brainvision(
        DATASET_PATH / sub / "eeg" / f"{sub}_task-jointaction_eeg.vhdr",
        preload=True
    )

    # Separate participants
    halves = {}

    for suffix in ("_R", "_L"):
        picks = [
            c for c in raw.ch_names
            if c.endswith(suffix) and c[:-2] not in NON_EEG
        ]

        r = raw.copy().pick(picks)
        r.rename_channels({c: c.removesuffix(suffix) for c in r.ch_names})
        r.set_montage("standard_1020", on_missing="warn")
        halves[suffix] = r

    events, event_id = mne.events_from_annotations(raw)

    # Get numerical ID of stimuli
    code = lambda n: event_id[f"Stimulus/S{n:>3}"]

    # Determine beginning of experiment
    if "Stimulus/S  1" in event_id:
        test_start = events[events[:, 2] == code(1)][0, 0]
        boundary = "S1"
    else:
        test_start = events[events[:, 2] == code(107)][-9, 0]
        boundary = "S107 fallback"

    all_trials = events[events[:, 2] == code(105)]
    trials = all_trials[all_trials[:, 0] > test_start]

    # S10: duet, S11: constant pitch
    s10, s11 = code(10), code(11)
    cond_ev = events[np.isin(events[:, 2], [s10, s11])]

    condition = np.array([
        "duet" if cond_ev[cond_ev[:, 0] < s][-1, 2] == s10
        else "constant_pitch"
        for s in trials[:, 0]
    ])

    # Determine end of trials
    ends = np.append(trials[1:, 0], events[-1, 0] + 1)

    # Event-based quality control
    complete = np.array([
        all(
            np.any(
                (events[:, 2] == code(c))
                & (events[:, 0] >= a)
                & (events[:, 0] < b)
            )
            for c in (2, 3, 106)
        )
        for a, b in zip(trials[:, 0], ends)
    ])

    good = trials[complete]
    metadata = pd.DataFrame({"condition": condition[complete]})

    kw = dict(
        event_id={"trial_start": code(105)},
        tmin=tmin,
        tmax=tmax,
        baseline=None,
        metadata=metadata,
        preload=True
    )

    # Create epochs for both participants
    for suffix, r in halves.items():
        mne.Epochs(r, good, **kw).save(
            DERIV / f"{sub}_{suffix[1]}_long-epo.fif",
            overwrite=True
        )

    # Return subject-level preprocessing results
    return {
        "sub": sub,
        "boundary": boundary,
        "practice": len(all_trials) - len(trials),
        "real": len(trials),
        "complete": int(complete.sum()),
        "duet": int((metadata.condition == "duet").sum()),
        "constant_pitch": int(
            (metadata.condition == "constant_pitch").sum()
        )
    }


def update_preprocessing_results(subjects):
    # Load existing results, preserving notebook results
    if RESULTS.exists():
        results = json.loads(RESULTS.read_text(encoding="utf-8"))
    else:
        results = {}

    preprocessing = results.setdefault("preprocessing", {})

    for sub in subjects:
        print(f"Processing {sub}...")
        output = preprocess_subject(sub)

        # Use subject ID as dictionary key
        preprocessing[sub] = {
            k: v for k, v in output.items() if k != "sub"
        }

        print(f"  Complete: {output['complete']}/{output['real']}")
        print(f"  Duet: {output['duet']}")
        print(f"  Constant pitch: {output['constant_pitch']}")

    # Save without overwriting other notebook results
    RESULTS.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8"
    )

    print(f"\nUpdated {RESULTS} successfully.")


if __name__ == "__main__":
    subjects = sorted(
        p.name for p in DATASET_PATH.glob("sub-*")
        if p.is_dir()
    )

    update_preprocessing_results(subjects)
