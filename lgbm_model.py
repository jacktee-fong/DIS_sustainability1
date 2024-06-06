import pandas as pd
import numpy as np
import lightgbm as lgb
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
import pickle

df_building = pd.read_excel("store/clean_data2.xlsx")
df_SGXC1 = df_building[df_building['codes'] == 'SGX C1 Energy & Water']

# rename the month column to date
df_SGXC1["date"] = df_SGXC1["month"]

# extract the month and year from the date column
df_SGXC1["month"] = df_SGXC1["date"].dt.month
df_SGXC1["year"] = df_SGXC1["date"].dt.year

# Define training and testing data
training_mask = df_SGXC1["date"] < "2022-01-01"
testing_mask = df_SGXC1["date"] >= "2022-01-01"

training_data = df_SGXC1.loc[training_mask]
testing_data = df_SGXC1.loc[testing_mask]

# Define features and labels
X_train = training_data[["month", "year", "working_day", "temperature"]]
y_train = training_data["energy"]

X_test = testing_data[["month", "year", "working_day", "temperature"]]
y_test = testing_data["energy"]

best_params = None
best_score = float('inf')
num_round = 0

# number of runs to perform using randomly selected hyperparameters
iterations = 50
for i in range(iterations):
    print('iteration number', i+1)

    params = {
        'learning_rate': np.random.uniform(0.01, 0.3),  
        'boosting_type': np.random.choice(['gbdt', 'dart', 'rf']),
        'objective': 'regression',
        'metric': 'mae',
        'feature_fraction': np.random.uniform(0.5, 0.8),  
        'num_leaves': np.random.randint(5, 16),  
        'min_data_in_leaf': np.random.randint(10, 30),  
        'max_depth': np.random.randint(3, 8),  
        'bagging_fraction': np.random.uniform(0.7, 0.9),
        # to prevent overfitting by stopping training when further improvement on the validation set is unlikely
        'early_stopping_rounds' : 10 ,
        'feature_pre_filter': False,
    }

    train_data = lgb.Dataset(X_train, label=y_train) #Load in data
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

    round = np.random.randint(100, 1000)

    #Train using selected parameters
    model = lgb.train(params, train_data, round, valid_sets=[ test_data])

    y_pred = model.predict(X_test)
    mae=mean_absolute_error(y_pred,y_test)
    print(f"Parameters: {params}, MAE: {mae}, iterations: {num_round}")
    
    # Update best parameters if current MAE is lower
    # the lower the MAE value the better the model performance
    if mae < best_score:
        best_score = mae
        best_params = params
        num_round = round

print(f"\nBest parameters: {best_params}")
print(f"Best MAE: {best_score}")
print(f"Number of round: {num_round}")

if best_params is not None:
    # retrain the model with the best parameters 
    best_model = lgb.train(best_params, train_data,num_round, valid_sets=[test_data])

    with open('model/lgbm_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)

