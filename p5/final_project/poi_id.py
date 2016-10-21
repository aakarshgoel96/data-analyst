#!/usr/bin/python
import sys
import pickle
import numpy
import pandas
import sklearn
import matplotlib 
from sklearn import metrics
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score
from numpy import mean
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
from sklearn import cross_validation
from sklearn import datasets
### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi','salary','to_messages','total_payments','exercised_stock_options','bonus',
'restricted_stock','shared_receipt_with_poi','restricted_stock_deferred','total_stock_value','expenses',
'loan_advances','from_messages','from_this_person_to_poi','poi','director_fees','deferred_income',
'from_poi_to_this_person']# You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)
df = pandas.DataFrame.from_records(list(data_dict.values()))
persons = pandas.Series(list(data_dict.keys()))


df.replace(to_replace='NaN', value=numpy.nan, inplace=True)
print df.head()
print df.isnull().sum()
print df.shape
### Task 2: Remove outliers
# Removing column from database if counter > 72

for column, series in df.iteritems():
    if series.isnull().sum() > 72:
        df.drop(column, axis=1, inplace=True)
# Drop email address column
if 'email_address' in list(df.columns.values):
    df.drop('email_address', axis=1, inplace=True)

### Task 3: Create new feature(s)
poi_ratio = (df['from_poi_to_this_person'] + df['from_this_person_to_poi']) / (df['from_messages'] + df['to_messages'])
fraction_to_poi = (df['from_this_person_to_poi']) / (df['from_messages'])
fraction_from_poi = (df['from_poi_to_this_person']) / (df['to_messages'])
scale = sklearn.preprocessing.MinMaxScaler(feature_range=(0, 100), copy=True)

df['poi_ratio'] = pandas.Series(poi_ratio) * 100
df['fraction_to_poi'] = pandas.Series(fraction_to_poi) * 100
df['fraction_from_poi'] = pandas.Series(fraction_from_poi) * 100

df.replace(to_replace='NaN', value=numpy.nan, inplace=True)
df= df.replace(to_replace=numpy.nan, value=0)
df = df.fillna(0).copy(deep=True)
df.columns = list(df.columns.values)
salary_scaled = scale.fit_transform(df['salary'])
print salary_scaled       
print df.isnull().sum()
print df.head()
print df.shape  
df.describe()    
### Store to my_dataset for easy export below.
my_dataset = data_dict
print df.to_dict(orient="index")
print df.keys()
labels = df['poi'].copy(deep=True).astype(int).as_matrix()
features = (df.drop('poi', axis=1)).fillna(0).copy(deep=True).as_matrix()

### Extract features and labels from dataset for local testing

features_train, features_test, labels_train, labels_test = cross_validation.train_test_split(features, labels, 
	test_size=0.3, random_state=42)
### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
from sklearn.cluster import KMeans
k_clf = Pipeline(steps=[
        ('scaler', StandardScaler()),
('classifier',  KMeans(n_clusters=2, tol=0.001))])

from sklearn.ensemble import AdaBoostClassifier
ab_clf = Pipeline(steps=[('scaler', StandardScaler()),
	('classifier',  AdaBoostClassifier(n_estimators=100))])

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html
def evaluate_clf(clf, features, labels, num_iters=1000, test_size=0.3):
    print clf
    accuracy = []
    precision = []
    recall = []
    first = True
    for trial in range(num_iters):
        features_train, features_test, labels_train, labels_test = cross_validation.train_test_split(features, labels, 
	test_size=0.3, random_state=42)  ### Extract features and labels from dataset for local testing
        clf.fit(features_train, labels_train)
        pred = clf.predict(features_test)
        accuracy.append(accuracy_score(labels_test, pred))
        precision.append(precision_score(labels_test, pred))
        recall.append(recall_score(labels_test, pred))
        if trial % 10 == 0:
            if first:
                sys.stdout.write('\nProcessing')
            sys.stdout.write('.')
            sys.stdout.flush()
            first = False

    print "done.\n"
    print "precision: {}".format(mean(precision))
    print "recall:    {}".format(mean(recall))
    print "accuracy:    {}".format(mean(accuracy))
    return mean(accuracy), mean(precision), mean(recall)
print "Result of KMeans Classifier"    
evaluate_clf(k_clf, features, labels) 
print "Result of AdaBoost Classifier"     
evaluate_clf(ab_clf, features, labels)    
### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.
clf = ab_clf
my_features_list=list(df.columns.values)
pickle.dump(clf, open("../data/my_classifier.pkl", "w"))
pickle.dump(my_dataset, open("../data/my_dataset.pkl", "w"))
pickle.dump(my_features_list, open("../data/my_feature_list.pkl", "w"))