#!/usr/bin/python
import sys
import pickle
import numpy
import pandas
import sklearn
import matplotlib 
from sklearn import metrics
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.cross_validation import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
from numpy import mean
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import *
from sklearn import cross_validation
from sklearn import datasets
### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".

poi_label = ['poi']

financial_features_list = [
    'salary', 
    'deferral_payments', 
    'total_payments', 
    'loan_advances', 
    'bonus', 
    'restricted_stock_deferred', 
    'deferred_income', 
    'total_stock_value', 
    'expenses', 
    'exercised_stock_options', 
    'other', 
    'long_term_incentive', 
    'restricted_stock', 
    'director_fees'
    ]

email_features_list = [
    'to_messages', 
    #'email_address', 
    'from_poi_to_this_person', 
    'from_messages', 
    'from_this_person_to_poi',
    'shared_receipt_with_poi'
    ]

features_list = poi_label + financial_features_list + email_features_list
# You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
data_dict.pop('TOTAL', 0)
'''Removed TOTAL as outlier'''
    

### Task 3: Create new feature(s)
def dict_to_list(key,normalizer):
    new_list=[]

    for i in data_dict:
        if data_dict[i][key]=="NaN" or data_dict[i][normalizer]=="NaN":
            new_list.append(0.)
        elif data_dict[i][key]>=0:
            new_list.append(float(data_dict[i][key])/float(data_dict[i][normalizer]))
    return new_list

### create two lists of new features
fraction_from_poi_email=dict_to_list("from_poi_to_this_person","to_messages")
fraction_to_poi_email=dict_to_list("from_this_person_to_poi","from_messages")
features_list.extend(['fraction_to_poi_email', 'fraction_from_poi_email'])
### insert new features into data_dict
count=0
for i in data_dict:
    data_dict[i]["fraction_from_poi_email"]=fraction_from_poi_email[count]
    data_dict[i]["fraction_to_poi_email"]=fraction_to_poi_email[count]
    count +=1
df = pandas.DataFrame.from_records(list(data_dict.values()))
persons = pandas.Series(list(data_dict.keys()))
print persons

df.replace(to_replace='NaN', value=numpy.nan, inplace=True)
print df.head()
print df.isnull().sum()
print df.shape


### Extract features and labels from dataset for local testing
data = featureFormat(data_dict, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)
features = MinMaxScaler().fit_transform(features)
features_train, features_test, labels_train, labels_test = train_test_split(features, labels, test_size=0.3)
'''Selecting best features using SelectKBest'''
from sklearn.feature_selection import SelectKBest
k_best = SelectKBest(k=10)
k_best.fit(features_train, labels_train)
scores = k_best.scores_
#combine features and scores, and sort in descending order
feature_score_pairs = list(sorted(zip(features_list[1:], scores), key=lambda x: x[1], reverse=True))
best_features = dict(feature_score_pairs[:10])
print best_features
features_list=['poi','exercised_stock_options','salary','bonus']
### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.

from sklearn.neighbors import KNeighborsClassifier
kn_clf = Pipeline(steps=[('classifier',  KNeighborsClassifier()
)])
from sklearn.ensemble import AdaBoostClassifier
ab_clf = Pipeline(steps=[('classifier',  AdaBoostClassifier(n_estimators=100))])
print "Result of KNeighbours Classifier"    
test_classifier(kn_clf,data_dict, features_list)
print "Result of AdaBoost Classifier"     
test_classifier(ab_clf,data_dict, features_list)
### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html
#choosing KNeighbours Classifier and tuning its parameters
from sklearn.grid_search import GridSearchCV
cv = StratifiedShuffleSplit(labels, 1000, random_state = 42)
metrics = ['minkowski', 'euclidean', 'manhattan'] 
weights = ['uniform', 'distance']
n_neighbors = [1,2,3,4,5,6,7,8,9,10]
param_grid_knc = dict(metric=metrics, weights=weights, n_neighbors=n_neighbors)
clf_knc = GridSearchCV(KNeighborsClassifier(), param_grid=param_grid_knc, cv=cv)
clf_knc.fit(features, labels)
print clf_knc.best_estimator_
print clf_knc.best_score_
#Tuning parameters of KNeighbours according to above results.
print "Final Result after tuning the parameters"
clf = Pipeline(steps=[('classifier',  KNeighborsClassifier(algorithm='auto', leaf_size=30, 
    metric='manhattan',metric_params=None, n_jobs=1, n_neighbors=5, p=2, weights='uniform')
)])
test_classifier(clf,data_dict, features_list)
### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.
# dump_classifier_and_data(clf, enron_data_sub, list_cols)
# test_classifier(clf, enron_data_sub, list_cols)
dump_classifier_and_data(clf, data_dict, features_list)

