import pandas as pd
import numpy as np
import lightgbm as lgb
import pickle

def train_model(df_building, train_date, val_date, target, model_path):

    # Define masks for training, testing, and validation sets
    training_mask = df_building["date"] < train_date
    testing_mask = df_building["date"] >= train_date
    val_mask = df_building["date"] >= val_date

    training_data = df_building[training_mask]
    testing_data = df_building[testing_mask]
    val_data = df_building[val_mask]

    # Define features
    features = ["month", "year", "working_day", "temperature", "code_number"]
    X_train = training_data[features]
    y_train = training_data[target]

    X_test = testing_data[features]
    y_test = testing_data[target]

    # LightGBM parameters
    params = {
        "objective": "regression",
        "boosting_type": "rf",
        "learning_rate": 0.001,
        "metric": "rmse",
        "bagging_fraction": 0.8,
        "feature_fraction": 0.8,
        "min_data_in_bin": 60,
    }

    # Prepare datasets
    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

    # Training model
    num_round = 5
    bst = lgb.train(params, train_data, num_round, valid_sets=[test_data])

    pickle.dump(bst, open(model_path, 'wb'))
    
    return bst
