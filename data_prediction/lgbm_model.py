import pandas as pd
import numpy as np
import lightgbm as lgb
import pickle

def train_model(df_building, train_date, val_date, target, model_path):
    """
    train a LightGBM regression model using the provided DataFrame.
    :param df_building: dataframe that contains target variable and features for training.
    :param train_date str: cutoff date for separating the training and testing data.
    :param val_date str: cutoff date for separating the validation data.
    :param target str: target variable name for training.
    :param model_path str: path where the trained model will be saved.
    Return: bst: trained LightGBM model.
    """

    # define masks for training, testing, and validation sets
    # rows with dates before 'train_date' will be included in the training set
    # rows with dates on or after 'train_date' will be included in the testing set
    training_mask = df_building["date"] < train_date
    testing_mask = df_building["date"] >= train_date
    val_mask = df_building["date"] >= val_date

    # separate the DataFrame into training, testing, and validation sets
    training_data = df_building[training_mask]
    testing_data = df_building[testing_mask]
    val_data = df_building[val_mask]

    # define the feature columns for the model
    # the columns in the dataset that will be used as input features for the model
    features = ["month", "year", "working_day", "temperature", "code_number"]

    # extract the input features and the target variable for the training set
    X_train = training_data[features]
    y_train = training_data[target]

    # extract the input features and the target variable for the testing set
    X_test = testing_data[features]
    y_test = testing_data[target]

    # LightGBM parameters for training the model
    params = {
        "objective": "regression",
        "boosting_type": "rf",
        "learning_rate": 0.001,
        "metric": "rmse",
        "bagging_fraction": 0.8,
        "feature_fraction": 0.8,
        "min_data_in_bin": 60,
    }

    # prepare datasets for training and testing
    # convert the training data into a LightGBM dataset
    train_data = lgb.Dataset(X_train, label=y_train)

    # convert the testing data into a LightGBM dataset, using the training data as a reference
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

    # training the model
    # set the number of rounds for training
    num_round = 5

    # train the model using the specified parameters, training data, and number of rounds
    bst = lgb.train(params, train_data, num_round, valid_sets=[test_data])

    # save the trained model to the specified path
    # use pickle to save the trained model object to a file
    pickle.dump(bst, open(model_path, 'wb'))
    
    return bst
