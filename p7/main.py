import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.compose import make_column_transformer






class UserPredictor:
#     def __init__(self):
#         self.xcols=list()
        

    def fit(self, train_users, train_logs,train_y):
        xcols=["past_purchase_amt", "age","/blender.html","/cleats.html","/keyboard.html","/laptop.html","/tablet.html","gold","silver","bronze"]

        model=LogisticRegression(fit_intercept=False,max_iter=1000) 
       

        oh = OneHotEncoder()
        data = oh.fit_transform(train_users[["badge"]])
        frame=pd.DataFrame(data.toarray(), columns=oh.get_feature_names_out())



        train_users["gold"]=frame["badge_gold"]
        train_users["bronze"]=frame["badge_bronze"]
        train_users["silver"]=frame["badge_silver"]


        merged_inner = pd.merge(left=train_users, right=train_y)


        train_logs_final=train_logs.pivot_table(index="user_id",columns="url", values="seconds",aggfunc='sum')
        train_logs_final.reset_index(level=0, inplace=True)

        merged_final=merged_inner.merge(train_logs_final, how="left")
        merged_final=merged_final.fillna(0)


        self.model= model.fit(merged_final[xcols], merged_final["y"])

        
    def predict(self,test_users, test_logs):
        oh = OneHotEncoder()
        data = oh.fit_transform(test_users[["badge"]])
        frame=pd.DataFrame(data.toarray(), columns=oh.get_feature_names_out())

        xcols=["past_purchase_amt", "age","/blender.html","/cleats.html","/keyboard.html","/laptop.html","/tablet.html","gold","silver","bronze"]

        test_users["gold"]=frame["badge_gold"]
        test_users["bronze"]=frame["badge_bronze"]
        test_users["silver"]=frame["badge_silver"]


        test_logs_final=test_logs.pivot_table(index="user_id",columns="url", values="seconds",aggfunc='sum')
        test_logs_final.reset_index(level=0, inplace=True)

        merged_final=test_users.merge(test_logs_final, how="left")
        merged_final=merged_final.fillna(0)
        
        
        merged_final["prediction"] = self.model.predict(merged_final[xcols])
        
        return merged_final["prediction"].to_numpy()
    
    
    

    



        


    


        

