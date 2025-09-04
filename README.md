# RECOVER PASC CP Implementation

## Quick run guide
- Download/copy code provided in python file pasc_cp.py ([https://github.com/Mikekoropsak/recover_pasc_implementation/blob/main/pasc_cp.py](url)) and load into your code editor
- Package requires 1 diagnosis dataframe that contains the following columns: patient identifier, ICD-10 diagnsoses, and covid index date. 

We used ICD-10 codes under categories outlined in the code set to identify patients who could be classified as having PASC. We followed the steps below to identify whether the diagnosis of interest is a PASC diagnosis or a comorbidity.
1.	Identify patient’s index date of COVID-19 infection. 
2.	Define a blackout period by excluding all recorded diagnoses 7 days prior to 30 days after the index date.
3.	Identify the earliest instance of a recorded diagnosis category within 180 days after the index event.
4.	Identify whether the diagnosis category is a comorbidity or a PASC diagnosis:
a.	If the earliest instance of a diagnosis category identified in step 3 is also present in the patients record prior to the index date, this is a comorbidity not a PASC diagnosis.
b.	If the earliest instance is a diagnosis category is after the index date only, this is a PASC diagnosis.
Patient’s PASC status is assigned by identifying patients who have at least one PASC diagnosis in their records.

Patient’s PASC subphenotype is defined by mapping the identified PASC diagnoses to affected organ system.
<img width="470" height="300" alt="image" src="https://github.com/user-attachments/assets/170aab4c-5d07-4815-966e-a7de06827eb2" />
