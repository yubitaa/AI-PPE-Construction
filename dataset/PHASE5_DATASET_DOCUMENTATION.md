# Phase 5 — PPE Dataset Documentation

## 1. Dataset Purpose

This dataset is prepared for the future PPE object-detection development phase.

Phase 5 does not include YOLO model training or fine-tuning.

## 2. Final Classes

| ID | Class |
|---|---|
| 0 | Person |
| 1 | Helmet |
| 2 | Vest |

No `No Helmet`, `No Vest`, or `Gloves` classes are included.

## 3. Data Sources

### Source A — PPE + Person

- Source type: Public PPE dataset
- License: CC BY 4.0
- Original candidate images: 1,203
- Used as a major source for Person, Helmet, and Vest examples.

### Source B — Construction Safety

- Source type: Public construction-safety dataset
- License: CC BY 4.0
- Original candidate images: 1,206
- Used to add missing/mixed PPE situations and construction variation.

## 3.1 Source URLs and Annotation/Export Tool

### Source A
URL:
https://universe.roboflow.com/jojo-xebec/ppe-person-ac76d-i9u1z/dataset/dataset

License:
CC BY 4.0

### Source B
URL:
https://universe.roboflow.com/jojo-xebec/construction-safety-gsnvb-fe3fz-kvvt4/dataset/dataset

License:
CC BY 4.0

### Annotation / Dataset Export Tool
Roboflow was used to inspect the source annotations and export the datasets in YOLOv8-compatible format.

The project team did not manually create the original source annotations.
The project preparation process normalized, filtered, validated, and quality-checked the source annotations.

## 4. Cleaning

The preparation process removed source-specific classes that are outside the project scope:

- Gloves
- No Helmet
- No Vest

Invalid/problematic images identified during QC were excluded.

Original raw sources remain preserved under:

`dataset/raw/`

## 5. Final Dataset Size

Total final images: 2,360

Train: 1,888

Validation: 236

Test: 236

## 6. Final Object Instances

Person: 6,944

Helmet: 6,690

Vest: 4,942

## 7. PPE Situation Statistics

Images with Helmet: 2,323

Images with Vest: 1,836

Images with both Helmet and Vest: 1,806

Images without Helmet: 37

Images without Vest: 524

## 8. Annotation Format

YOLO-compatible normalized bounding-box annotations are used.

Each image has a corresponding `.txt` label file.

Final class mapping:

0 = Person
1 = Helmet
2 = Vest

## 9. Annotation Quality Control

Automated checks were performed for:

- corrupted/unreadable images
- image/label pairing
- invalid class IDs
- invalid YOLO coordinates
- exact duplicates
- suspicious annotations

A representative visual annotation sample was manually inspected.

Problematic annotation groups identified during QC were removed from the final candidate dataset.

## 10. Dataset Split

Final split:

- Train: 80%
- Validation: 10%
- Test: 10%

The original Roboflow split was not reused for final evaluation.

Source A contiguous frame sequences were kept together to prevent leakage between train, validation, and test.

Verified result:

- Duplicate filenames across splits: 0
- Source A groups crossing splits: 0

## 11. Augmentation Strategy

Training augmentation will be prepared for the future model-development phase.

Possible realistic transformations:

- brightness variation
- small rotations
- scaling
- horizontal flipping where appropriate
- mild blur

Validation and test data remain unaugmented.

## 12. Current Limitations

Potential limitations include:

- some construction scenes may be overrepresented
- lighting and camera-angle diversity may still be imperfect
- some PPE situations are less represented than full-PPE situations
- public-source annotation quality may vary

These limitations should be considered during the later AI model-development and evaluation phases.