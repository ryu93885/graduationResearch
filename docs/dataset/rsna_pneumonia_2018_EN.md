# Characteristics of the RSNA Pneumonia Detection Challenge 2018 Dataset

- **Created**: 2026-11-12
- **Updated**: 2026-11-12 (reflects the results of downloading the official files and checking the actual data; details in [`inspection_report_2026-11-12.md`](inspection_report_2026-11-12.md), in Japanese)
- **Purpose**: A summary, with sources, of the basic information on the dataset used in this graduation research. It serves as the basis for the program specifications and for statements in the progress report.
- **Materials checked**: the official RSNA distribution page, the Dataset Description (V1 02/07/2022), the Terms of Use and Attribution, and the official distribution files (all checked on 2026-11-12)
- **Note**: The full text of Shih et al. (2019) has not been checked yet (on hold under Q-06). Statements about the paper are based on excerpts of its text shown in search results.
- **About this translation**: This is an English translation of [`rsna_pneumonia_2018.md`](rsna_pneumonia_2018.md) as of 2026-11-12. The Japanese version is the original; if the two differ, the Japanese version takes precedence. The numbers R-xx and Q-xx refer to entries in [`docs/revision_report.md`](../revision_report.md) (in Japanese).

**Source categories**

| Category | Meaning |
|---|---|
| Data | Checked by a program after downloading the official distribution files (`scripts/inspect_dataset.py`) |
| Official | Checked on the official RSNA page, the Dataset Description or the Terms |
| Paper excerpt | Based on excerpts of the text of Shih et al. (2019) shown in search results (to be verified against the full text) |
| Secondary | Based on other papers or information from Kaggle |
| General knowledge | General medical knowledge about chest X-rays |
| Unverified | To be checked after obtaining the data |

---

## 1. Overview

| Item | Description | Source |
|---|---|---|
| Name | RSNA Pneumonia Detection Challenge (2018) | Official |
| Created by | RSNA, in collaboration with the STR (Society of Thoracic Radiology) and MD.ai | Official |
| Source data | The NIH chest X-ray dataset (CXR8 / ChestX-ray14) | Official |
| Images | 30,000 frontal chest X-rays | Official |
| Annotations | Image-level labels and bounding boxes (2D ROIs) of opacities suspicious for pneumonia | Official |
| Competition | Held on Kaggle, with more than 1,400 teams. The task was to detect and localize opacities suspicious for pneumonia | Official |
| Competition metric | Mean Average Precision over IoU thresholds from 0.4 to 0.75 | Secondary |

## 2. How the dataset was built

1. **NIH ChestX-ray14**: 112,120 frontal images of 30,805 patients. The disease labels were extracted automatically from radiology reports by natural language processing and contain errors. (Secondary)
2. **Image selection**: 30,000 images were selected from the NIH images. (Official) They consist of 15,000 images positive for pneumonia, infiltration or consolidation according to the NIH labels, 7,500 "No Finding" images, and 7,500 images with other findings. (Data: `subset_init_label` in the mapping file)
   - After re-reading, only 5,113 (34%) of the 15,000 images that NIH labelled as pneumonia-related became Lung Opacity. Of the 7,500 NIH "No Finding" images, 668 also became Lung Opacity. (Data)
   - → **The dataset deliberately over-samples suspected pneumonia cases.** Its positive rate differs from that in clinical practice (R-18).
3. **Re-reading**: Radiologists manually re-labelled the images and drew bounding boxes on MD.ai. (Official)
4. **Kaggle competition (2018)**: Run in two stages, stage 1 and stage 2. (Secondary)
5. **Official RSNA distribution**: The images, the annotations and the mapping to the NIH dataset are distributed. (Official)

## 3. Background

### 3.1 View position (PA and AP) (General knowledge)

| | PA (posteroanterior) | AP (anteroposterior) |
|---|---|---|
| X-ray direction | Enters from the back and reaches a detector on the chest side | Enters from the chest side and reaches a detector on the back side |
| How it is taken | Standing, in the radiology department | With a portable unit, in bed (lying down or sitting) |
| Patients | Mostly ambulatory | Mostly inpatients or severely ill |
| Image features | The heart appears close to its actual size | The heart appears enlarged; the scapulae tend to overlap the lungs |

Because an AP view is itself associated with more severe illness, it is a candidate shortcut for the model (R-06).

### 3.2 Opacity

- A region that lets less X-ray through and appears whiter than its surroundings. (General knowledge)
- Pneumonia appears as consolidation or ground-glass opacity. However, atelectasis, pleural effusion, pulmonary edema, masses and other conditions also appear white. (General knowledge)
- In this dataset, boxes were drawn around "an area more opaque than the surrounding area which, **in a patient with cough and fever**, would have a low to high likelihood of being pneumonia", based on the Fleischner Society definition. (Paper excerpt)
- The readers judged from the images alone, without clinical information, so **the labels are a classification of imaging findings, not diagnoses**.

## 4. Images

| Item | Description | Source |
|---|---|---|
| Number | 30,000 (PA 16,248 / AP 13,752; AP is about 46%) | Official, Data |
| Format | NIH PNG images converted to DICOM | Official |
| DICOM tags added | Sex, age and view position (AP / PA) | Official |
| Size | 1024×1024 pixels (all 30,000 images) | Data |
| Bit depth and color | 8 bits, MONOCHROME2 (0 = black) | Data |
| Pixel compression | **JPEG Baseline (lossy)**. Reading the pixels requires a JPEG decoder such as Pillow | Data |
| PixelSpacing (physical size of one pixel) | Differs between images (mainly 0.139 / 0.143 / 0.168 / 0.171 / 0.194 mm). May reflect differences in imaging devices | Data |
| Age | Stored as a string (e.g. `46`). Six images have values over 100, with a maximum of 412 (probably input errors) | Data |
| Institution | A single institution, the NIH Clinical Center | Official (from the attribution in the Terms) |
| Personal information burned into images | "No / Removed" according to the Dataset Description | Official |
| Text markers burned into images | Seen in some images (visual check). The proportion has not been checked | Data |

**View position and positive rate (Data)**

| View position | Positive rate | Share of positive images |
|---|---|---|
| AP | 40.5% | 77.3% |
| PA | 10.0% | 22.7% |

Predicting positives from the view position alone already gives an ROC-AUC of 0.708. Even within PA images, the positive rate ranges from 8.1% to 14.3% depending on PixelSpacing.

**Implications for this study**
- The metadata available from DICOM are sex, age and view position, plus PixelSpacing. There are no device or institution names (R-19).
- The view position can be a strong shortcut (R-06).
- Because there is only one institution, there is no confounding by institution. On the other hand, it is unknown whether the results would be the same at other institutions.

## 5. Labels

### 5.1 Original labels and distributed classes

| Original label assigned by readers (Paper excerpt) | Class in the distribution | Target |
|---|---|---|
| Opacity (High / Medium / Low Probability) | Lung Opacity (with boxes) | 1 |
| No Opacity / Not Normal | No Lung Opacity / Not Normal | 0 |
| Normal | Normal | 0 |

- There was also a "Question" flag for sending an image to a chest specialist for review. (Paper excerpt)
- **Lung Opacity** also includes "low probability" opacities (R-17). The choice between high and medium probability varied between readers. (Paper excerpt)
- **No Lung Opacity / Not Normal** means "there may be opacities in the lungs, but none suspicious for pneumonia". It does not mean that there is no opacity. (Paper excerpt)

### 5.2 Counts

**Final labels in the official distribution (`Calculated` group; Data)**

| Class | Images | Notes |
|---|---|---|
| Lung Opacity | 7,106 | 11,390 boxes in total. Positive rate 23.9% |
| No Lung Opacity / Not Normal | 12,788 | |
| Normal | 9,790 | |
| Total | 29,684 | Same as the Kaggle train + test (26,684 + 3,000) |
| No final label | 316 | Probably excluded images (R-23) |

**For reference: Kaggle stage 2 train (Secondary)**: Lung Opacity 6,012 images (9,555 boxes), Not Normal 11,821 images, Normal 8,851 images; 26,684 images in total.

### 5.3 Readers' probability labels (Data)

Breakdown of the probability grades of the boxes drawn by readers. In single reads (Team 1), most boxes are "medium", and about 22% are "low" (R-17).

| Group | High | Medium | Low |
|---|---|---|---|
| Team 1 (single read) | 1,437 | 8,837 | 2,891 |
| Team 2 | 856 | 1,721 | 957 |
| Team 2a | 669 | 1,334 | 913 |

## 6. Bounding boxes

| Item | Description | Source |
|---|---|---|
| How they were drawn | The smallest rectangle that contains the whole suspicious opacity. Separate opacities get separate boxes | Paper excerpt |
| Format (Kaggle version) | Top-left corner `x, y` and `width, height` on the 1024×1024 image, in pixels | Secondary |
| Format (official distribution) | MD.ai JSON. The `data` field of each annotation holds `{x, y, width, height}` (with decimals). We confirmed that `x, y` is the top-left corner by overlaying boxes on the images | Data |
| Boxes per image | 1 box: 3,030 images; 2 boxes: 3,892; 3 boxes: 160; 4 boxes: 24 | Data |
| Images read by three readers | The **intersection (overlapping part)** of the readers' boxes was adopted, so these boxes tend to be smaller (Paper excerpt). In fact, the median box area was 3.8% of the image for multi-read images and 6.5% for single-read images (Data) | Paper excerpt, Data |
| Location | 6,025 boxes in the left half of the image (the patient's right lung side) and 5,365 in the right half. No box extends beyond the image | Data |
| Negative images | No boxes (this is why the box transplantation in R-01 is needed) | Data |

A box is not the outline of the lesion itself but a rectangle around the opacity. It can contain normal tissue, and the opacity can extend beyond it.

## 7. Annotation process and quality

| Item | Description | Source |
|---|---|---|
| Readers | 18 radiologists from 16 institutions, 12 of them STR chest radiologists. Mean experience 10.6 years (3–35 years) | Official |
| Practice beforehand | All readers practiced on the same 50 images (without seeing the other readers' results) | Paper excerpt |
| Images read by one reader | Six RSNA readers read 5,000 images each | Paper excerpt |
| Images read by three readers | 4,527 images (2 STR readers + 1 RSNA reader). Images with disagreement were adjudicated by one of two chest specialists with more than 10 years of experience | Official (count), Paper excerpt, Secondary (adjudication) |
| Training vs. evaluation images | Training images were labelled by RSNA readers who were not chest specialists; evaluation images were labelled by a panel of STR chest specialists | Paper excerpt |
| Kaggle split | Of the images read by three readers, 3,000 went to test and about 1,500 to train | Secondary |
| Reader groups in the official distribution | `Team 1` (single read; six readers with about 5,000 images each), `Team 2` and `Team 2a` (additional readers), `Adjudication`, and `Calculated` (final labels) | Data |
| Number of multi-read images | 4,526 images were read by both Team 2 and Team 2a (nearly matching the 4,527 stated by RSNA) | Data |
| Images with adjudication records | 1,380 | Data |
| Agreement among the three readers | Fleiss' κ = 0.50 (positive or not). All three readers agreed on 64.5% of the images | Data |
| Relation to a majority vote | Among multi-read images, 158 have a positive final label even though only one reader read them as positive, and 241 have a negative final label even though two or more readers read them as positive | Data |

**Implications for this study**
- The way the labels were made differs between the training and evaluation images. Box size and quality also differ, so we record whether each image was read by one or three readers and evaluate the two groups separately (R-16).
- Single-read images may contain opacities that the reader did not box (R-07).

## 8. Distribution

### 8.1 Official RSNA distribution (as of 2026-11-12)

Distribution page: https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018

We checked the contents by actually downloading the files (2026-11-12, Data).

| Name on the distribution page | File name and size | Contents | Use in this study |
|---|---|---|---|
| Download images ... used in initial annotation | `pneumonia-challenge-dataset-original_2018.zip` (3.41 GB) | The 25,684 images of Kaggle stage 1 train (included in the 30,000 images below) | Not used |
| Download initial annotations | `pneumonia-challenge-annotations-original_2018.json` (19.6 MB) | Kaggle stage 1 train labels (25,684 images, 5,659 positive). Binary labels only; no reader information | Used only to mark which images were in Kaggle stage 1 train |
| Download images ... used in the Pneumonia Challenge | `pneumonia-challenge-dataset-adjudicated-kaggle_2018.zip` (3.98 GB) | 30,000 DICOM images | Images for **all analyses** |
| Download annotations used in the Pneumonia Challenge | `pneumonia-challenge-annotations-adjudicated-kaggle_2018.json` (52.0 MB) | Covers all 30,000 images. **Contains every reader's labels (with probability grades), the adjudication records and the final labels (`Calculated`)** | Final labels for the **main analysis**; Team 1 / 2 / 2a labels for the **per-reader and probability analyses** |
| Download mapping of RSNA image dataset to original NIH dataset | `pneumonia-challenge-dataset-mappings_2018.json` (17.6 MB) | For the 30,000 images: RSNA image ID, DICOM UIDs, NIH file name, NIH labels and selection group | Patient-level split (R-03) and analysis of the selection groups |

- The files are distributed under `https://s3.amazonaws.com/east1.public.rsna.org/AI/2018/`.
- At first we thought that the "initial annotations" contained the per-reader information (Q-05). In fact, the per-reader information is also in the "annotations used in the Pneumonia Challenge" (revision of R-15).
- Use `scripts/download_data.py` to download the files. It checks their size and SHA-256.

### 8.2 Kaggle version (for reference)

This study uses the official distribution. The Kaggle version is used only as a reference when comparing with previous studies. (All Secondary)

| Stage | train | test |
|---|---|---|
| stage 1 | 25,684 images | 1,000 images |
| stage 2 | 26,684 images (stage 1 train and test combined) | 3,000 images |

- The main files are:
  - `stage_2_train_labels.csv` (`patientId, x, y, width, height, Target`)
  - `stage_2_detailed_class_info.csv` (`patientId, class`)
  - DICOM images
- The number of distinct `patientId` values equals the number of images. In other words, **`patientId` is effectively a per-image ID** (Data: `subset_img_id` in the mapping file matches the DICOM PatientID, and all 30,000 are distinct). A patient-level split requires the NIH mapping (R-03).
- The Kaggle total of 29,684 images matches the number of images with a final label in the official distribution. The difference of 316 from 30,000 is the images without a final label (Data).
- **The Kaggle split is not patient-level.** 2,009 patients have images both in stage 1 train and elsewhere (Data).

## 9. Terms of use and attribution (Official)

- The data may be used for academic research and education, for both commercial and non-commercial purposes.
  - However, the Dataset Description says "Non-commercial purpose", which is inconsistent (R-20). Academic use is permitted either way.
- Do not attempt to identify or contact any individual in the data.
- When sharing or redistributing the data, the following attribution is required.
  - **For the NIH data**
    - A link to the download site: https://nihcc.app.box.com/v/ChestXray-NIHCC
    - A citation of the paper: Xiaosong Wang, Yifan Peng, Le Lu, Zhiyong Lu, Mohammadhadi Bagheri, Ronald Summers. ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases. IEEE CVPR, pp. 3462-3471, 2017.
    - An acknowledgement that the NIH Clinical Center is the data provider
  - **For the RSNA-STR data and annotations**
    - A link to the distribution page: https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018
    - A citation of the paper: George Shih, Carol C. Wu, Safwan S. Halabi, Marc D. Kohli, Luciano M. Prevedello, Tessa S. Cook, Arjun Sharma, Judith K. Amorosa, Veronica Arteaga, Maya Galperin-Aizenberg, Ritu R. Gill, Myrna C.B. Godoy, Stephen Hobbs, Jean Jeudy, Archana Laroia, Palmi N. Shah, Dharshan Vummidi, Kavitha Yaddanapudi, Anouk Stein. Augmenting the National Institutes of Health Chest Radiograph Dataset with Expert Annotations of Possible Pneumonia. Radiology: Artificial Intelligence, 2019. https://doi.org/10.1148/ryai.2019180041

## 10. Points that need particular care in this study

For details, see the corresponding numbers in `docs/revision_report.md` (in Japanese).

| Characteristic | What to watch for | Related |
|---|---|---|
| Negative images have no boxes | In Models A/C, "whether a mask is present" becomes a cue to the answer | R-01 |
| The labels have three classes | Not Normal can contain opacities other than pneumonia | R-02 |
| `patientId` is a per-image ID | A patient-level split requires the NIH mapping | R-03 |
| A patient can have several images (up to 75). The Kaggle split is not patient-level | We must re-split the data at the patient level ourselves | R-03 |
| The source data are NIH ChestX-ray14 | Pretrained weights trained on the NIH data can cause leakage | R-04 |
| AP is more common in severely ill patients (77% of positives are AP) | Shortcut through the view position. The view position alone gives an AUC of 0.71 | R-06 |
| PixelSpacing differs between images | Possible shortcut through differences in imaging devices | R-19 |
| Age has outliers (maximum 412) | Treat them as missing values in preprocessing | R-22 |
| Most images were read by one reader | Missed boxes and label variability | R-07, R-17 |
| Multi-read boxes are intersections and therefore small | Opacities are likely to extend beyond the box. Evaluate separately by read type | R-09, R-16 |
| Images were selected to include many suspected pneumonia cases | The positive rate and precision cannot be generalized directly to clinical practice | R-18 |
| Only three metadata items | Check visually for text markers burned into the images | R-19 |

## 11. Checks after obtaining the data

Checked on 2026-11-12. The detailed figures are in [`inspection_report_2026-11-12.md`](inspection_report_2026-11-12.md) (in Japanese).

- [x] Structure of the official JSON: MD.ai format. It has reader IDs, probability labels, reader groups (which can identify multi-read images) and final labels (Section 8.1)
- [x] Total and per-class counts: 29,684 of the 30,000 images have a final label (Section 5.2)
- [x] AP / PA ratio among positives and negatives: 77.3% of positives are AP (Section 4)
- [x] Number and size of boxes per image: multi-read boxes are smaller (Section 6)
- [x] NIH patient IDs: **12,274 patients** (matches the value in Section 2.1 of the progress report, R-21). Up to 75 images per patient. 7,464 patients have only one image
- [x] Image size and bit depth: 1024×1024, 8 bits, JPEG Baseline (Section 4)
- [x] Age outliers: six images with values over 100 (maximum 412)
- [ ] Text markers burned into images: seen in some images by visual check. The proportion has not been checked

## 12. References

- RSNA. RSNA Pneumonia Detection Challenge (2018). https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018
- RSNA. 2018 RSNA Pneumonia Detection Challenge Dataset Description, V1 02/07/2022. ("Dataset description" on the page above)
- RSNA. Pneumonia Detection Challenge Terms of Use and Attribution. ("Terms of use and acknowledgments" on the page above)
- Shih G, et al. Augmenting the National Institutes of Health Chest Radiograph Dataset with Expert Annotations of Possible Pneumonia. *Radiology: Artificial Intelligence*, 2019. https://doi.org/10.1148/ryai.2019180041 (full text not yet checked; search-result excerpts only)
- Wang X, et al. ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases. *IEEE CVPR*, pp. 3462-3471, 2017.
- Gabruseva T, et al. Deep Learning for Automatic Pneumonia Detection. *CVPR Workshops*, 2020. (counts in the Kaggle version)
- Pneumonia Detection in Chest Radiographs. arXiv:1811.08939. (breakdown of how the images were selected)
- Kaggle. RSNA Pneumonia Detection Challenge, Discussion 64723. https://www.kaggle.com/c/rsna-pneumonia-detection-challenge/discussion/64723 (how the multi-read images were split and the adjudication procedure)
