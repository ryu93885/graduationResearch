**GRADUATION RESEARCH**

**PROGRESS REPORT**

Research Concept, Dataset Selection, and Experimental Plan

**Investigating Pneumonia Detection Using  
Features Outside Physician-Annotated Regions  
in Chest Radiographs**

*— A Comparison of Region-Focused, Full-Image, and Region-Excluded Models  
with XAI-Based Analysis of Decision Evidence —*

**Prepared: 5 November 2026**

Status: Research planning stage — implementation and experiments not yet started

*This report summarizes the current research plan and progress. It is not a final thesis and does not present experimental results.*

# Document Information

| **Item**        | **Description**                                                                            |
|-----------------|--------------------------------------------------------------------------------------------|
| Document type   | Graduation research progress report (research-planning stage)                              |
| Date prepared   | 5 November 2026                                                                            |
| Primary dataset | RSNA Pneumonia Detection Challenge 2018                                                    |
| Current status  | Research topic, hypotheses, and candidate dataset selected; implementation not yet started |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Central research question</strong></p>
<p>Do chest radiographs contain pneumonia-related information outside the regions marked by physicians as suspicious opacities? Can Explainable AI (XAI) identify and present such regions in an interpretable way?</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# Abstract

This study aims to investigate how information within physician-annotated regions and information outside those regions contribute to the classification of chest radiographs. The planned dataset is the RSNA Pneumonia Detection Challenge 2018. Three image-classification models will be developed: (A) a model that primarily receives physician-annotated regions, (B) a model that receives the entire image, and (C) a model that receives images in which the annotated regions have been masked.

The classification performance of the models will be compared using metrics such as Accuracy, Precision, Recall (Sensitivity), Specificity, F1-score, and ROC-AUC. XAI methods such as Grad-CAM will also be applied to visualize image regions that appear to contribute to each model’s predictions. The study will focus on whether information outside physician-annotated regions may be useful for classification and whether XAI explanations reflect the models’ actual predictive behavior.

At the current stage, the research topic, main hypotheses, basic design of the three models, and the decision to prioritize the official RSNA distribution have been established. Data acquisition, preprocessing, model development, and experiments have not yet begun. The next step is to inspect the dataset structure and label definitions before finalizing the experimental specifications.

# Contents

| **Section** | **Title**                                            |
|-------------|------------------------------------------------------|
| Chapter 1   | Research Background, Purpose, and Research Questions |
| Chapter 2   | Dataset and Conditions of Use                        |
| Chapter 3   | Research Method and Design of the Three Models       |
| Chapter 4   | Evaluation Methods and Verification Plan             |
| Chapter 5   | Experimental Results and Research Progress           |
| Chapter 6   | Discussion, Limitations, and Mitigation Strategies   |
| Chapter 7   | Conclusion and Future Research Plan                  |
| References  | Official resources and related literature            |

# Chapter 1. Research Background, Purpose, and Research Questions

## 1.1 Research Background

Deep-learning models for medical images can learn features from entire images and classify the presence of disease or image findings. However, classification accuracy alone does not reveal which image regions or features the model used as evidence for its prediction. A model may rely on factors that are not directly related to the lesion, such as imaging conditions, image composition, or incidental information. Its predictive performance and the basis of its decisions therefore need to be examined together.

In this study, a region marked by physicians as an opacity suspicious for pneumonia is referred to as a “physician-annotated region.” This region is not treated as identical to the complete outline of a lesion. The Bounding Boxes in the RSNA dataset are rectangles surrounding pulmonary opacities; they are not precise pixel-level lesion contours. Accordingly, this study does not compare AI with the full diagnostic process of physicians. Instead, it compares model inputs that use physician-annotated local regions, the full image, or images with the annotated regions excluded.

## 1.2 Research Purpose

The purpose of this study is to compare the contributions of information contained within physician-annotated regions and information outside those regions to chest-radiograph classification, and to investigate whether features outside the annotated regions may be used for classification. In addition, XAI will be used to visualize image regions that contribute to each model’s predictions, and the validity, faithfulness, and stability of the explanations will be evaluated.

## 1.3 Research Questions

- RQ1: How do classification performance and decision evidence differ between a model trained primarily on physician-annotated regions and a model trained on entire images?

- RQ2: Can images from which physician-annotated regions have been excluded still be classified to some extent as having findings suggestive of pneumonia?

- RQ3: How are important regions visualized by XAI related to physician-annotated regions, and to what extent do the explanations faithfully reflect the predictions?

## 1.4 Hypotheses

| **Hypothesis**                            | **Description**                                                                                                        | **Main verification method**                                                                              |
|-------------------------------------------|------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| H1: Information outside annotated regions | Information used for classification may also exist outside physician-annotated regions.                                | Measure the classification performance of region-excluded Model C and compare it with control conditions. |
| H2: Discovery through XAI                 | XAI may visualize locations or features outside the annotated regions to which the full-image model responds strongly. | Compare Grad-CAM visualizations with annotations and masking experiments.                                 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Important interpretation note</strong></p>
<p>A response outside the annotated regions alone is not sufficient to conclude that a new, medically useful finding has been discovered. The model may be using imaging conditions or dataset-specific biases (shortcut learning); these possibilities must be examined separately.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# Chapter 2. Dataset and Conditions of Use

## 2.1 Selected Dataset

The first-choice dataset is the chest-radiograph collection and annotations released for the RSNA Pneumonia Detection Challenge 2018. RSNA worked with the Society of Thoracic Radiology (STR), MD.ai, and other collaborators to prepare a dataset based on NIH ChestX-ray data for detecting and localizing opacities suspicious for pneumonia \[1\]\[4\].

| **Item**            | **Description**                                                                                                                                 |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| Image modality      | Chest radiographs (frontal views)                                                                                                               |
| Number of images    | Approximately 30,000 images                                                                                                                     |
| Source data         | NIH ChestX-ray8 (a public dataset containing approximately 112,000 images)                                                                      |
| Image format        | DICOM. The source PNG images are described as having been converted to DICOM, with tags such as sex, age, and view position added \[3\].        |
| Annotations         | Image-level labels and Bounding Boxes (2D ROIs) indicating pulmonary opacities                                                                  |
| Patient information | 12,274 individuals for 30,000 examinations; some patients have multiple examinations \[4\].                                                     |
| Reading process     | 18 radiologists from 16 institutions participated. Not all cases were read by three readers; 4,527 cases were read by three readers \[3\]\[4\]. |

## 2.2 Labels and Target Task

The dataset contains labels indicating the presence or absence of opacities suspicious for pneumonia, as well as image-finding annotations. The exact field names and representations may differ depending on the released package and annotation file version. After downloading the data, the CSV/JSON structure and label definitions will be checked before the classification task is finalized.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Tentative primary task</strong></p>
<p>The primary task is to classify the presence or absence of an opacity suspicious for pneumonia (pneumonia-like opacity). If the negative group contains both normal images and images with abnormalities other than pneumonia, a three-class task or sensitivity analyses using different definitions of the negative group will be considered.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 2.3 Conditions of Use and Collaborative Research

Under the conditions stated on the official RSNA distribution page, the de-identified images and annotations may be used for academic research and education, as well as other commercial or non-commercial purposes. Users must not attempt to re-identify or contact individuals represented in the data. Sharing or redistribution requires the specified attribution \[1\]\[2\]. Therefore, if collaborative research becomes necessary, the data will be managed and shared in accordance with the conditions attached to the official RSNA distribution.

When sharing or redistributing the data, the RSNA official distribution page and the citation to Shih et al. (2019) must be provided. For the underlying NIH data, the NIH download page, the citation to Wang et al. (CVPR 2017), and the attribution to the NIH Clinical Center must also be included \[2\].

No attempt will be made to re-identify or contact individuals. The actual scope of sharing, the use of images in the thesis or presentation materials, and the methods by which collaborators may use the data will be confirmed with the academic supervisor and the university offices responsible for research ethics and information management.

## 2.4 Python-Based Data Acquisition Plan

The RSNA official page provides direct download links for the image archive (ZIP), annotations, and mapping information for the NIH images \[1\]. The distributed files are hosted on AWS S3 and can be downloaded over HTTP using Python libraries such as requests. After acquisition, the ZIP archive will be extracted using zipfile; DICOM images will be read using pydicom; and labels and Bounding Box information will be loaded using pandas and/or json.

### Planned acquisition and preprocessing workflow

1.  Download the files using the distribution links listed on the official RSNA page; save large files using streaming downloads.

2.  Extract the ZIP archive and check file counts, file sizes, and possible corruption.

3.  Read DICOM images with pydicom and match image IDs with labels and Bounding Box information in CSV/JSON files.

4.  Examine patient/examination mapping information and check for duplicate records or data leakage between splits.

5.  Use the official RSNA website rather than the Kaggle competition distribution because the official route provides a clearer basis for collaborative sharing. Kaggle has separate competition rules, which should not be confused with the official RSNA terms \[5\].

The feasibility of Python-based acquisition has been confirmed from the availability of official download links. However, actual downloading, extraction, and loading tests have not yet been performed. Retry handling, resuming interrupted downloads, checksum verification, and a secure storage location will be addressed during implementation.

### Post-download checks

| **Check**                       | **What will be verified**                                                                                             |
|---------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| File integrity                  | File sizes, extracted file counts, and possible corruption.                                                           |
| Image–annotation correspondence | Missing or duplicate correspondences among image IDs, image-level labels, and Bounding Boxes.                         |
| Label distribution              | Counts of positive and negative cases, and whether they are broadly consistent with the official dataset description. |
| Reproducibility records         | Acquisition date, distribution-page URL, filenames, and Python/library versions.                                      |

# Chapter 3. Research Method and Design of the Three Models

## 3.1 Overall Research Workflow

Training, validation, and test data will be prepared from the same dataset. Three models will be developed using the same basic classifier while varying only the image regions supplied as input. Differences in classification performance and decision evidence will be compared to examine the usefulness of information outside annotated regions and the explanatory performance of XAI.

| **Stage 1**                    | **Stage 2**           | **Stage 3**                | **Stage 4**                           | **Stage 5**                             |
|--------------------------------|-----------------------|----------------------------|---------------------------------------|-----------------------------------------|
| Acquire RSNA images and labels | Split data by patient | Generate three input types | Train models and evaluate performance | Visualize and evaluate XAI explanations |

## 3.2 Three Models for Comparison

| **Model**                | **Input and training method**                                                                                                                                                                                                    | **Research question addressed**                                                                                                                  |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| A: Region-focused model  | Crop the region inside a physician-annotated Bounding Box or provide an image in which the region is emphasized. The handling of multiple Bounding Boxes and patch aggregation will be decided after inspecting the actual data. | Examine classification performance when the model focuses on localized pulmonary opacities, and analyze the features of important local regions. |
| B: Full-image model      | Provide the entire unmodified chest radiograph. This is the reference model for comparison.                                                                                                                                      | Classify from the entire image and use XAI to visualize regions that contribute to the prediction.                                               |
| C: Region-excluded model | Mask the Bounding Box regions and provide the remaining image, thereby retaining information primarily outside the annotated regions.                                                                                            | Determine whether information usable for classification remains after physician-annotated regions are excluded.                                  |

## 3.3 Preprocessing and Experimental Conditions

- Standardize and document DICOM pixel-value transformations, image orientation, grayscale representation, image size, and normalization.

- Use patient-level splitting as the basic approach for training, validation, and testing. Check examination mappings to prevent multiple examinations from the same patient from appearing in different splits.

- Use the same network architecture, training conditions, data split, and random seed across the three models as far as possible, making the input region the principal comparison factor.

- Check class imbalance and consider class weighting or resampling if necessary. Do not use the test set for training or threshold adjustment before final evaluation.

## 3.4 Control Experiments for Masking

If the Bounding Box regions in Model C are simply filled with black pixels, the black rectangles or their boundaries may themselves become cues for the model. Therefore, several masking methods will be considered, including replacement with the mean value, interpolation from surrounding pixels, and blurring. A control experiment that masks random regions with the same area and shape will also be considered.

A Bounding Box is a rectangle surrounding an opacity, not a precise outline of a lesion. Models A and C will therefore be described as experiments using “physician-annotated regions.” The report will not claim that the experiments perfectly isolate “the lesion alone” or “everything except the lesion.”

# Chapter 4. Evaluation Methods and Verification Plan

## 4.1 Classification Performance Evaluation

| **Metric**           | **Meaning and point to examine in this study**                                                                                  |
|----------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Accuracy             | Overall proportion of correct predictions. It will not be used as the sole measure because it is affected by class composition. |
| Precision            | Proportion of images predicted as positive that actually have a positive label.                                                 |
| Recall (Sensitivity) | Proportion of truly positive images detected by the model; examined from the perspective of missed cases.                       |
| Specificity          | Proportion of truly negative images correctly classified as negative.                                                           |
| F1-score             | Harmonic mean of Precision and Recall.                                                                                          |
| ROC-AUC / PR-AUC     | Discrimination performance across thresholds. PR-AUC will also be reported in light of the positive-class prevalence.           |

All metrics will be calculated on the same test set, and confidence intervals will be reported where possible. Differences between models will be examined not only through mean values but also through reproducibility across multiple random seeds and, where feasible, patient-level bootstrapping. Positive/negative label definitions and threshold-selection procedures will be fixed before the experiments.

## 4.2 Visualization of Decision Evidence Using XAI

Grad-CAM will primarily be applied to full-image Model B to visualize, as heatmaps, regions estimated to contribute to classification. The same method may also be applied to Models A and C to examine how explanation maps change with the input region. Grad-CAM uses feature maps and gradients from CNNs and related architectures to visualize image regions important to a prediction \[6\].

## 4.3 XAI Evaluation Criteria

| **Criterion**                       | **Evaluation method / points to check**                                                                                                                                                                             |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Regional validity                   | Visualize and quantify the overlap between high-activation regions in the heatmap and physician-annotated Bounding Boxes. Agreement with a Bounding Box does not imply perfect agreement with medical ground truth. |
| Faithfulness                        | Measure how prediction probabilities change when highly ranked heatmap regions are hidden or retained (e.g., Deletion / Insertion).                                                                                 |
| Stability                           | Examine how much explanation regions change when small perturbations are applied to inputs or training seeds are changed.                                                                                           |
| Responses outside annotated regions | Identify highly activated areas outside the annotations and compare them with masking and control-experiment results.                                                                                               |

## 4.4 Relationship to the Research Hypotheses

| **Hypothesis**                                        | **Planned verification**                                                                                                                                                                        |
|-------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| H1: Information exists outside annotated regions      | Compare the test performance of Model C with control conditions such as random masking, and examine consistency across masking methods.                                                         |
| H2: XAI visualizes features outside annotated regions | Compare Grad-CAM with Bounding Box locations and methods such as Deletion / Insertion. Visualization alone will not be used to claim discovery of a new medical finding or clinical usefulness. |

# Chapter 5. Experimental Results and Research Progress

As of 5 November 2026, data acquisition, model development, and training experiments have not yet begun. Therefore, no numerical classification results or XAI visualizations are currently available. This chapter provides sections corresponding to the results chapter of the final thesis and explicitly records the current experimental and overall research status.

## 5.1 Current Status of Experimental Results

The table below is intended to record future experimental results. All items are currently unmeasured; no values have been estimated or entered.

| **Target** | **Experiment**                                                          | **Current status**            |
|------------|-------------------------------------------------------------------------|-------------------------------|
| Model A    | Classification performance using physician-annotated regions            | Not conducted / not measured  |
| Model B    | Classification performance using the entire image                       | Not conducted / not measured  |
| Model C    | Classification performance after excluding annotated regions            | Not conducted / not measured  |
| XAI        | Visualization of decision evidence and evaluation of faithfulness, etc. | Not conducted / not evaluated |

## 5.2 Progress Summary

| **Item**                                  | **Current status**                                                                                                                              | **Progress**                    |
|-------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| Research direction                        | The plan focuses on differences between human visual assessment and AI decision evidence, particularly information outside annotated regions.   | Decided                         |
| Research purpose and hypotheses           | Two hypotheses have been defined around the possibility of information outside the regions and visualization through XAI.                       | Draft finalized                 |
| Three-model design                        | Region-focused, full-image, and region-excluded models have been designed. Detailed preprocessing remains undecided.                            | Basic design decided            |
| Dataset selection                         | RSNA Pneumonia Detection Challenge 2018 has been selected as the first-choice dataset.                                                          | Decided                         |
| Conditions of use                         | The official RSNA page and terms have been reviewed; attribution, prohibition of re-identification, and sharing conditions have been organized. | Public conditions reviewed      |
| University and collaboration requirements | University research-ethics procedures, scope of sharing with collaborators, and image use in thesis/presentation materials must be confirmed.   | Confirmation required           |
| Python acquisition method                 | Direct download links are available from the official RSNA page; acquisition using requests and similar tools is feasible.                      | Method confirmed / not executed |
| Data acquisition and structure inspection | Download images and annotations; test reading of DICOM and CSV/JSON files.                                                                      | Not started                     |
| Preprocessing and data splitting          | Finalize label definitions, patient-level splits, Bounding Box handling, Model C masking, and control conditions.                               | Not started                     |
| Model development and training            | Implement and train Models A, B, and C.                                                                                                         | Not started                     |
| XAI and performance evaluation            | Implement Grad-CAM and calculate classification and explanation metrics.                                                                        | Not started                     |
| Results, discussion, and thesis writing   | Analyze experimental results and complete the graduation thesis.                                                                                | Not started                     |

# Chapter 6. Discussion, Limitations, and Mitigation Strategies

## 6.1 Current Discussion Policy

If Model C shows a certain level of classification performance, this would indicate that the model was able to use information associated with the label even after physician-annotated regions were excluded. However, it would not necessarily mean that the information has medical significance. The study must examine whether correlations arising from imaging conditions or the data-collection process can be ruled out. Medical interpretations will be made cautiously and, where appropriate, with advice from the academic supervisor or specialists.

| **Issue / limitation**                          | **Potential impact on the study**                                                                        | **Mitigation strategy**                                                                                                |
|-------------------------------------------------|----------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Bounding Boxes are not complete lesion outlines | Normal tissue may be included inside a rectangle, and opacities may extend outside it.                   | Use the term “physician-annotated region” rather than “the lesion itself,” and clearly state the limitation.           |
| Uncertainty in labels                           | A label for an opacity suspicious for pneumonia is not equivalent to a confirmed clinical diagnosis.     | Define the task as classification of image findings and do not present it as a substitute for clinical diagnosis.      |
| Multiple examinations and repeated patients     | If images from the same patient appear in both training and test sets, performance may be overestimated. | Inspect patient mapping and split data by patient where possible.                                                      |
| Artificial features at mask boundaries          | The boundary created by black filling or other masking may become a cue for the model.                   | Compare multiple masking methods and conduct controls such as random-region masking.                                   |
| Dataset-specific bias                           | Differences in view position, age, sex, equipment, or institution may affect predictions.                | Inspect metadata distributions and conduct stratified evaluations and additional confounding checks.                   |
| Limits of XAI interpretation                    | A heatmap does not provide a complete explanation of the model’s internal decision process.              | Evaluate faithfulness and stability; do not make causal claims based solely on visualization.                          |
| Data sharing and publication of results         | Attribution requirements and university rules must be followed.                                          | Use the official RSNA distribution route and confirm sharing methods in advance with collaborators and the supervisor. |

# Chapter 7. Conclusion and Future Research Plan

## 7.1 Next Tasks

| **Order** | **Task**                                                                                                                                       | **Completion criteria**                                                                |
|-----------|------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| 1         | Confirm the research purpose, conditions for using official RSNA data, and university research-ethics procedures with the academic supervisor. | The methods of use and sharing, including possible collaboration, have been confirmed. |
| 2         | Acquire images, annotations, and mapping information from the official RSNA page using Python.                                                 | Required files have been acquired and their sizes and integrity checked.               |
| 3         | Read DICOM images and CSV/JSON annotations.                                                                                                    | Image IDs correspond correctly to labels and Bounding Boxes.                           |
| 4         | Determine label definitions, target cases, and patient-level data splits.                                                                      | A dataset specification and split list have been created.                              |
| 5         | Implement image preprocessing and input-generation procedures for Models A, B, and C.                                                          | Three input types can be reproducibly generated from the same image.                   |
| 6         | Check the operation of all three models on a small dataset.                                                                                    | Training, inference, and evaluation can be executed end to end.                        |
| 7         | Conduct the main experiments, XAI evaluation, and additional control experiments.                                                              | Results, figures, tables, and reproducibility settings have been organized.            |
| 8         | Analyze the results and complete the thesis with discussion and conclusions.                                                                   | Conclusions are written in relation to the research purpose and hypotheses.            |

## 7.2 Items to Finalize Before Experiments

- Label definition for the classification task (binary or three-class classification, and handling of excluded cases).

- Patient-level training/validation/test split method and a fixed test set.

- Treatment of multiple Bounding Boxes in Model A and the masking method for Model C.

- Common model architecture, training conditions, evaluation thresholds, and use of multiple random seeds.

- XAI target models, quantitative evaluation methods for heatmaps, and control experiments.

## 7.3 Preliminary Conclusion

This study has been planned to compare the roles of regions annotated by physicians as opacities suspicious for pneumonia and other image information in chest radiographs, using three types of models and XAI-based analysis of decision evidence. The RSNA Pneumonia Detection Challenge 2018 official distribution has been selected as the first-choice dataset, taking into account the conditions for sharing data in potential collaborative research.

The next step is to acquire the data and inspect its structure, then finalize label definitions, patient-level splitting, and masking methods. After that, classification performance of the three models and the explanatory performance of XAI will be evaluated separately. The possibility that features outside annotated regions may be useful will be examined alongside the possibility that models may exploit inappropriate shortcut-learning signals.

# References and Official Resources

\[1\] Radiological Society of North America (RSNA). “RSNA Pneumonia Detection Challenge (2018).” Official dataset distribution page. [<u>Link</u>](https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018)

\[2\] RSNA. “Pneumonia Detection Challenge Terms of Use and Attribution.” [<u>Link</u>](https://www.rsna.org/-/media/files/rsna/education/ai-resources-and-training/ai-image-challenge/pneumonia-detection-challenge-terms-of-use-and-attribution.pdf)

\[3\] RSNA. “2018 RSNA Pneumonia Detection Challenge Dataset Description.” [<u>Link</u>](https://www.rsna.org/-/media/Files/RSNA/Education/AI%20resources%20and%20training/AI%20image%20challenge/RSNA-2018-Pneumonia-Detection-Challenge-Dataset-Description.ashx?hash=8331DDFA52AA5EE9C3C99B5983BB680D7BD2ABBF&la=en)

\[4\] Shih G, Wu CC, Halabi SS, et al. “Augmenting the National Institutes of Health Chest Radiograph Dataset with Expert Annotations of Possible Pneumonia.” Radiology: Artificial Intelligence. 2019. [<u>Link</u>](https://doi.org/10.1148/ryai.2019180041)

\[5\] Kaggle. “RSNA Pneumonia Detection Challenge — Competition Rules.” For reference to rules distinct from the official RSNA distribution route. [<u>Link</u>](https://www.kaggle.com/c/rsna-pneumonia-detection-challenge/rules)

\[6\] Selvaraju RR, Cogswell M, Das A, et al. “Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization.” ICCV 2017. [<u>Link</u>](https://doi.org/10.1109/ICCV.2017.74)

\[7\] National Institutes of Health (NIH) Clinical Center. “ChestX-ray Dataset.” [<u>Link</u>](https://nihcc.app.box.com/v/ChestXray-NIHCC)

## Document Note

This report is a progress document based on the research concept and publicly available information as of 5 November 2026. After the data have been acquired, the actual file structure, label definitions, annotation specifications, and available patient-mapping information will be checked. The research plan and evaluation methods will be revised as necessary. Until experimental results are obtained, the hypotheses must not be treated as verified facts.
