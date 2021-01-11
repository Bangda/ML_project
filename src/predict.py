import os
import pandas as pd
import numpy as np
from sklearn import ensemble
from sklearn import preprocessing
from sklearn import metrics
import joblib 

from . import dispatcher

TEST_DATA = os.environ.get("TEST_DATA")
MODEL = os.environ.get('MODEL')

def predict(test_data):
    df = pd.read_csv(test_data)
    test_idx = df['id'].values
    predictions = None

    for FOLD in range(5):
        df = pd.read_csv(test_data)
        encoders = joblib.load(os.path.join("models", f"{MODEL}_{FOLD}_label_encoder.pkl"))
        cols = joblib.load(os.path.join("models", f"{MODEL}_{FOLD}_columns.pkl"))
        for c in encoders:
            lbl = encoders[c]
            # df.loc[:, c] = df.loc[:, c].astype(str).fillna("NONE")
            df.loc[:, c] = lbl.transform(df[c].values.tolist())


        # predicting
        clf = joblib.load(os.path.join("models", f"{MODEL}_{FOLD}.pkl"))

        df = df[cols]

        preds = clf.predict_proba(df)[:, 1]

        if FOLD == 0:
            predictions = preds

        else:
            predictions += preds
    
    predictions /= 5 
    sub = pd.DataFrame(np.column_stack((test_idx, predictions)), columns=["id", "target"])
    return sub

if __name__ == "__main__":
    
    submission = predict(test_data=TEST_DATA)
    submission.loc[:, "id"] = submission.loc[:, "id"].astype(int)
    submission.to_csv(f"models/rf_submission.csv", index=False)