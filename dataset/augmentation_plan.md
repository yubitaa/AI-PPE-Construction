# Phase 5 — Training Augmentation Plan

## Purpose

Prepare realistic augmentation for the future PPE model-development phase.

## Training Set

Augmentation may include:

- brightness variation
- small rotations
- scaling
- horizontal flipping where appropriate
- mild blur
- other minor realistic transformations

## Validation Set

No artificial augmentation.

Validation images remain representative evaluation data.

## Test Set

No artificial augmentation.

Test images remain untouched and reserved for final evaluation.

## Important Constraint

Augmentation is prepared during Phase 5 but model training is not performed during Phase 5.

## Rationale

The transformations should represent realistic construction-site variation without creating unrealistic PPE appearances.