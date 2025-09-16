# RECOVER PASC CP Implementation

## Quick run guide
- Download/copy code provided in python file pasc_cp.py [https://github.com/recoverEHRinformatics/recover_pasc_implementation/blob/main/pasc_cp.py](https://github.com/recoverEHRinformatics/recover_pasc_implementation/blob/main/pasc_cp.py) and load into your code editor
- Package requires 1 dataframe with the following columns:
  - patid (patient identifier)
  - dx_code (icd-10 diagnosis code)
  - index_date (covid index date, 1 per patient)

## Overview of Function 
1.	Identify patient’s index date of COVID-19 infection. 
2.	Define a blackout period by excluding all recorded diagnoses 7 days prior to 30 days after the index date.
3.	Identify the earliest instance of a recorded diagnosis category within 180 days after the index event.
4.	Identify whether the diagnosis category is a comorbidity or a PASC diagnosis:
a.	If the earliest instance of a diagnosis category identified in step 3 is also present in the patients record prior to the index date, this is a comorbidity not a PASC diagnosis.
b.	If the earliest instance is a diagnosis category is after the index date only, this is a PASC diagnosis.
Patient’s PASC status is assigned by identifying patients who have at least one PASC diagnosis in their records.

<img width="800" height="176" alt="image" src="https://github.com/user-attachments/assets/c3198488-3deb-4fd9-98f5-4b28d898f54f" />
