import pandas as pd
# import dask as dd

# PCORnet PASC codeset, can be replaced  
pasc_definition = pd.read_csv("https://raw.githubusercontent.com/recoverEHRinformatics/data-analysis-pipeline/main/external%20data%20sources/pasc_definition.csv")

# please reference the correct column names in your spreadsheet if using a different one
pasc_definition = pasc_definition.rename(columns={
    'ICD-10-CM': 'dx_code',
    'CCSR CATEGORY 1 DESCRIPTION': 'pasc_category',
    'PASC Name Simple': 'pasc_name_simple',
    'Organ Domain': 'system'
})


def get_pasc_all(diagnosis:Union[pd.DataFrame, dd.DataFrame], PASC_definition:Union[pd.DataFrame, dd.DataFrame], patid_column='patid', category='pasc_category', **kwargs):
    '''get_pasc_all finds all instances of PASC subphenotypes among patients. A patient can have more than one PASC subphenotype.

    Args:
        diagnosis (pd.DataFrame): standard diagnosis table from PCORnet CDM containing all diagnoses for patients.
        PASC_definition (pd.DataFrame): a reference spreadsheet containing all ICD-10 codes and diagnosis categories of PASC-like symptoms.
        patid_column (str, optional): _description_. Defaults to 'patid'.
        category (str, optional): _description_. Defaults to 'pasc_category'.
        **kwargs: allows you to provide additional named arguments. To be used if the diagnosis table does not have an index_date columns

    Returns:
        pd.DataFrame: a dataframe with all PASC subphenotypes per patient per subphenotype
    '''
    # convert the diagnosis input variable to a dask dataframe if it's a pandas dataframe
    if isinstance(diagnosis, pd.DataFrame):
        pasc_diagnoses = dd.from_pandas(diagnosis, npartitions = 2 * multiprocessing.cpu_count()) 


    # create a smaller subset of the diagnosis table containing only the PASC like diagnoses
    pasc_diagnoses = dd.merge(
        pasc_diagnoses,
        PASC_definition[['dx_code', 'pasc_category']],
        left_on='dx',
        right_on='dx_code', 
        how='inner'
    )
    # dropping duplicated column
    pasc_diagnoses = pasc_diagnoses.drop(columns=(['dx_code']))

    # save the index argument if provided
    index = kwargs.get('index', None)

    # Check if the diagnosis table contains an index_date column
    if isinstance(index, pd.DataFrame) or isinstance(index, dd.DataFrame):
        if 'index_to_admit' not in diagnosis.columns:
            # merge with index table to get the first instance of index event
            pasc_diagnoses = dd.merge(
                pasc_diagnoses,
                index[[patid_column, 'index_date']],
                on=patid_column, how='inner'
            ).drop_duplicates()

            # calculate the difference in days between the diagnosis date and index event date
            # date_diff_from_index < 0 means the index event date was recorded before the diagnosis 
            # date_diff_from_index > 0 means the index event date was recorded after the diagnosis
            pasc_diagnoses = pasc_diagnoses.assign(index_to_admit = (pasc_diagnoses['index_date'] - pasc_diagnoses['admit_date']) / np.timedelta64(1, 'D'))

        else:
            error_msg = "You provided an index table, and your diagnosis table already has an index_date column \
                \nSuggested solutions: \
                \n\t- Drop the following columns in your diagnosis table: 'index_date' and 'index_to_admit' \
                \n\t- Or remove the index table from this function and keep the 'index_date' and 'index_to_admit' columns in the diagnosis table"
            return print(error_msg)
        
    else:
        if 'index_to_admit' not in diagnosis.columns:
            error_msg = "You must provide an index table with an index_date column"
            return print(error_msg)

    # for better readibility flip the number's sign of index_to_admit column and rename
    pasc_diagnoses = pasc_diagnoses.assign(days_from_index = -1 * pasc_diagnoses['index_to_admit'])
    pasc_diagnoses = pasc_diagnoses.drop(columns=['site', 'index_to_admit'])

    # throw away any diagnoses in the blackout period and
    # balckout period is defined as 7 days before and 30 days after the index date
    pasc_diagnoses = pasc_diagnoses[~(pasc_diagnoses['days_from_index'].between(-7, 30, inclusive='both'))]

    # throw away any diagnoses 180 days after the index date
    pasc_diagnoses = pasc_diagnoses[pasc_diagnoses['days_from_index'] <= 180]

    # select the necessary columns and drop the duplicates
    # by only including the PASC category column (i.e. pasc_category) and excluding the ICD-10 code column (i10_code)
    # we ensure that if there are several ICD-10 codes within the same category, we count them as the same
    pasc_diagnoses = pasc_diagnoses[[patid_column, 'days_from_index', category, 'admit_date']].drop_duplicates().reset_index(drop=True)

    # find the first time earliest incidence of pasc appeared per patient per category
    pasc_diagnoses = pasc_diagnoses.groupby([patid_column, category]).min()
    pasc_diagnoses = pasc_diagnoses.rename(columns={
        'admit_date': 'date_incidence', # indicating the earliest date of PASC evidence for determining incidence
        'days_from_index': 'days_incidence' # indicating how long after the index date earliest date of PASC evidence incidence appeared
        })

    # only keep the diagnoses that happened after the index date for the first time
    pasc_diagnoses = pasc_diagnoses[pasc_diagnoses.days_incidence >= 0]

    # get year and month of the pasc indcidence
    pasc_diagnoses = pasc_diagnoses.assign(year_incidence = pasc_diagnoses['date_incidence'].apply(lambda x: x.year, meta=('date_incidence', 'int8')))
    pasc_diagnoses = pasc_diagnoses.assign(month_incidence = pasc_diagnoses['date_incidence'].apply(lambda x: x.month, meta=('date_incidence', 'int8')))

    # keeping patid_column (i.e. patid) and category (i.e. pasc_category) columns as a column rather than an index
    pasc_diagnoses = pasc_diagnoses.reset_index()

    pasc_diagnoses = pasc_diagnoses.compute()

    return pasc_diagnoses
