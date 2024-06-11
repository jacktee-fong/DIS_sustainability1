import pandas as pd

def get_model_data(model):
    """
    get the predicted data from Excel file based on the selected prediction model.
    :param model: str = "LGBM" or "Chronos"
    :return: dict of the dataset 
    """
    # initialize an empty DataFrame to store the combined data
    df_full = pd.DataFrame()

    # load the original dataset from an Excel file
    df = pd.read_excel("store/predict/clean_data.xlsx")
    
    # check the model selected to retrieve the respective dataset 
    if model == "Chronos":
        df_predict = pd.read_excel("store/output/clean_data_chronos.xlsx")
    elif model == "LGBM":
        df_predict = pd.read_excel("store/output/clean_data_lgbm.xlsx")
    
    # get a list of unique codes from the predicted dataset
    unique_codes = list(set(df_predict.code.to_list()))

    # combine the original data with predicted data for each code 
    for code in unique_codes:
        # filter the original data for the current code
        df_code = df[df["code"] == code]
        # filter the predicted data (df_predict) for the current code
        df_pred = df_predict[df_predict["code"] == code]
        # combine the row from both datasets. ignore index to avoid duplicate indices
        df_combine= pd.concat([df_code, df_pred],ignore_index=True)
        # Append the combined data to df_full. ignore index to avoid duplicate indices
        df_full = pd.concat([df_full, df_combine], ignore_index=True)
    
    return df_full.to_dict(orient='records')