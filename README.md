# An exploration of hyperscanning data of a joint action task

## Motivation

## Data

The dataset used for this is ds007471, an EEG hyperscanning study of the sense of joint agency during a musical joint-action task.

The study included 32 pairs of participants (64 people in total), each pair recorded simultaneously on a single 64-channel BrainVision file (32 channels per person, distinguished by `_R`/`_L` suffixes).

### Task

Each pair played simple tone sequences together, alternating between two conditions:

- **Musical duets**: 4 familiar melodies (Twinkle Twinkle Little Star, Hush Little Baby, B.I.N.G.O., Yankee Doodle), split into a melody part and an accompaniment part, one per participant.
- **Constant-pitch sequences**: 4 monotone control sequences (fixed pitches: A4, C5, E♭5, F♯5), same structure but with no real melodic coordination demand (low-engagement contrast condition).

Each pair ran through 8 tone sequences (4 duets + 4 constant-pitch) × 5 joint trials each = 40 trials per dyad.

Measured:

- **Joint agency rating (subjective involvement)** (1–7 self-report) after each trial: how much the participant felt their actions and the outcome were jointly theirs.
- **Synchronization performance**: The measured timing asynchrony between the two participants' note onsets, as a proportion of the beat interval, plus its variability (SD) per trial.

## Analysis

### Is increased inter-brain synchrony (IBS) associated with increased subjective involvement?: [Analysis notebook](ibs_subj_involv.ipynb)

**Plan:**

1. Load and preprocess the raw EEG
2. Load the behavioral file (agency ratings, condition labels)
3. Compute inter-brain synchrony (IBS) with HyPyP
4. Compare IBS between the duet and constant-pitch conditions, and relate that to the agency-rating difference between conditions.

**Raw Data:**

- Number of Channels: 64 Channels simultaneously (32 per person)
- Two eye-movement-channels: `VEOG_b_R` and `VEOG_a_R`
- Sampling rate: 1000 Hz
- Duration: 2,3186 seconds ≈ 38.6 minutes
- Frequency Range 1-125 Hz
-
