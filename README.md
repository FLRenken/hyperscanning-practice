# An exploration of hyperscanning data of a joint action task

## Next Steps

- [ ] Do an exploratory analysis of the dataset
- [x] ~~Compute phase lock value~~
- [ ] Include subjectivity-rating in analysis
- [ ] Extend analysis to more dyads
- [ ] Add CCorr and the alpha, beta and gamma bands, all with the same shuffled baseline
- [ ] Choose channel subsets before looking at results (e.g. frontal, central) instead of averaging all 729 pairs

## Goal

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

## Preprocessing-result

<!-- PREPROCESSING_RESULTS_START -->

| Subject | Boundary      | Practice | Real | Complete | Duet | Constant pitch |
| ------- | ------------- | -------: | ---: | -------: | ---: | -------------: |
| sub-01  | S1            |        6 |   57 |       39 |   19 |             20 |
| sub-02  | S1            |        6 |   58 |       37 |   19 |             18 |
| sub-03  | S107 fallback |        6 |   56 |       40 |   20 |             20 |
| sub-04  | S1            |        6 |   57 |       37 |   19 |             18 |
| sub-05  | S1            |        6 |   56 |       39 |   20 |             19 |
| sub-06  | S1            |        6 |   57 |       38 |   20 |             18 |
| sub-07  | S1            |        8 |   55 |       38 |   19 |             19 |
| sub-08  | S1            |        2 |   58 |       40 |   20 |             20 |
| sub-09  | S1            |        6 |   59 |       39 |   19 |             20 |
| sub-10  | S1            |        6 |   61 |       40 |   20 |             20 |
| sub-11  | S1            |        7 |   57 |       39 |   20 |             19 |
| sub-12  | S1            |        6 |   56 |       36 |   18 |             18 |
| sub-13  | S1            |        9 |   56 |       40 |   20 |             20 |
| sub-14  | S1            |        6 |   57 |       40 |   20 |             20 |
| sub-15  | S1            |        6 |   59 |       37 |   20 |             17 |
| sub-16  | S1            |        6 |   58 |       40 |   20 |             20 |
| sub-17  | S1            |        8 |   55 |       39 |   20 |             19 |
| sub-18  | S107 fallback |        6 |   59 |       37 |   19 |             18 |
| sub-19  | S1            |        6 |   57 |       40 |   20 |             20 |
| sub-20  | S1            |        6 |   59 |       39 |   20 |             19 |
| sub-21  | S1            |        6 |   62 |       38 |   19 |             19 |
| sub-22  | S1            |        8 |   58 |       40 |   20 |             20 |
| sub-23  | S1            |        6 |   56 |       40 |   20 |             20 |
| sub-24  | S1            |        7 |   60 |       39 |   19 |             20 |
| sub-25  | S1            |        6 |   57 |       40 |   20 |             20 |
| sub-26  | S1            |        6 |   60 |       40 |   20 |             20 |
| sub-27  | S1            |        6 |   56 |       39 |   19 |             20 |
| sub-28  | S1            |        6 |   56 |       40 |   20 |             20 |
| sub-29  | S1            |        6 |   56 |       36 |   16 |             20 |
| sub-30  | S1            |        9 |   63 |       40 |   20 |             20 |
| sub-31  | S1            |        6 |   56 |       38 |   19 |             19 |
| sub-32  | S1            |        6 |   57 |       39 |   20 |             19 |

<!-- PREPROCESSING_RESULTS_END -->

## Proof of Concept Analysis

### PLV (1 dyad)

For each complete trial, theta (4-8 Hz) the phase was calculated from a window of 4.5-12.5 seconds. The phase lock value was computed for every R X L channel pair, then averaged over all 729 pairs, giving one number per trial. "Real" averages trials with their true partners trial. "Shuffled" averages trials with the wrong partners trial from the same condition.

PLV Measure

<!-- PLV_RESULTS_START -->

| Condition      | Real pairs | Shuffled pairs | p-value |
| -------------- | ---------: | -------------: | ------: |
| duet           |     0.1144 |         0.1160 |  0.6015 |
| constant_pitch |     0.1172 |         0.1176 |  0.5130 |

<!-- PLV_RESULTS_END -->

There is no statistically significant excess of theta-band coupling in real pairs relative to the shuffled baseline in either condition.

**Limitations**

- This is just one dyad, with just the theta-band
- Averaging was done over all 729 channel pairs, so there's dillution in terms of localized coupling

## Glossary of Statistical Measures

### Phase-locking value

Quantifies the consisteny of phase differences between two signals across multiple trials.
For every trial, channel pair, and time point, we want the phase difference $$\Delta\phi(t) = \phi_R(t) - \phi_L(t)$$ where $$\phi_R(t)$$ and $$\phi_L(t)$$ are the instantaneous phases of the two EEG signals.

PLV ≈ 1 -> phase difference is very consistent

PLV ≈ 0 -> phase difference varies considerably

The problem is that a high PLV does not necessarily mean that the two brains are interacting. Phase locking can also occur if the pair hears the same music, moves together or are exposed to the same auditory stimulus.
