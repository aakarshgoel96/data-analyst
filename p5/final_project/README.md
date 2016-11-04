
# Intro to Machine Learning Final Project

## Identifying Fraud from Enron Emails 

In 2000, Enron was one of the largest companies in the United States. By 2002, it had collapsed into bankruptcy due to widespread corporate fraud. In the resulting Federal investigation, a significant amount of typically confidential information entered into the public record, including tens of thousands of emails and detailed financial data for top executives.

In this project, I used python's scikit-learn library that consists of various machine learning algorithms to build person of interest identifier based on financial and email data made public as a result of the Enron scandal. This data has been combined with a hand-generated list of persons of interest (POI) in the fraud case, which means individuals who were indicted, reached a settlement or plea deal with the government, or testified in exchange for prosecution immunity.

Run poi_id.py to view the selected and tuned feature selections, and the machine learning algorithms' performances. Run tester.py to view the performance of the chosen algorithm, K-nearest neighbors classifier. The following is a snippet of the scores returned from tester.py


```python
Pipeline(steps=[('classifier', KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='manhattan',
           metric_params=None, n_jobs=1, n_neighbors=5, p=2,
           weights='uniform'))])
	Accuracy: 0.88554	Precision: 0.74951	Recall: 0.38450	F1: 0.50826	F2: 0.42599
	Total predictions: 13000	True positives:  769	False positives:  257	False negatives: 1231	True negatives: 10743


```

I have chosen KNeighboursClassifier as it gives very acuurate results. Time taken in KNeighbours is very less compared to any other algorithm.  

## Enron Submission Free-Response Questions

** Q1 Summarize for us the goal of this project and how machine learning is useful in trying to accomplish it. As part of your answer, give some background on the dataset and how it can be used to answer the project question. Were there any outliers in the data when you got it, and how did you handle those? **

The goal of this project is to choose a combination of features, financial and email, of former Enron employees and choose an appropriate machine learning algorithm to predict whether that person is considered a person of interest (POI) or not. It should be noted that this dataset contained labeled data where POIs were flagged and as such the purpose of this project is to build a supervised classification model that could be used on other unlabeled datasets.

The Enron dataset contained 146 records with 14 financial features, 6 email features, and 1 labeled feature for POI. Out of the latter dataset, 18 people were labeled as persons of interest (POI). Interestingly, I had to omit email_address from the email features list due to it being a string while all the other features were integer values; it was hard to justify keeping unique email addresses as a POI identifier for fraud. Furthermore, I visualize the dataset's feature to conduct some basic exploratory data analysis. 

Removed all the columns in the dataset whose half of the values are NaN type i.e >72. TOTAL field is removed as it has no relation with the model.

Employees with very high salary were outliers so 'salary' is scaled using MinMaxScaler.

** Q2 What features did you end up using in your POI identifier, and what selection process did you use to pick them? Did you have to do any scaling? Why or why not? As part of the assignment, you should attempt to engineer your own feature that does not come ready-made in the dataset -- explain what feature you tried to make, and the rationale behind it. (You do not necessarily have to use it in the final analysis, only engineer and test it.) In your feature selection step, if you used an algorithm like a decision tree, please also give the feature importances of the features that you use, and if you used an automated feature selection function like SelectKBest, please report the feature scores and reasons for your choice of parameter values.**

I have used SelectKBest method to find out top features from which I selected three features except poi i.e
salary, bonus, exercised_stock_options. Out of ten features these features together gave best results.

{'salary': 18.575703268041785, 'total_payments': 8.8667215371077717, 'bonus': 21.060001707536571, 'total_stock_value': 24.467654047526398, 'shared_receipt_with_poi': 8.7464855321290802, 'exercised_stock_options': 25.097541528735491, 'fraction_to_poi_email': 16.641707070468989, 'deferred_income': 11.595547659730601, 'restricted_stock': 9.3467007910514877, 'long_term_incentive': 10.072454529369441}

I tried to make two new features i.e 
fraction_to_poi_email: the fraction of all emails to a person that were sent from a person of interest
fraction_from_poi_email: the fraction of all emails that a person sent that were addressed to persons of interest

The hypothesis behind these features was that there might be stronger email connections between POIs than between POIs and non-POIs.

I used a min-max scaler. The scaler was very important to normalize the data as features had different units and varied widely by several orders of magnitude in some cases. Standardization of a dataset is a common requirement for many machine learning estimators: they might behave badly if the individual feature do not more or less look like standard normally distributed data (e.g. Gaussian with 0 mean and unit variance).


**Q3 What algorithm did you end up using? What other one(s) did you try? How did model performance differ between algorithms?**

The algorithm I end up using was the K-nearest neighbors classifier. I selected it purely based on its performace in accuracy, precision and recall, as well as it's simplicity to use. I tried using the following models as well: "Decision Tree", "Random Forest", "AdaBoost", "Naive Bayes".

Different algoritms classify the data in different manners every algoritms and its parameters work differently for different datasets like AdaBoost is a kind of ensemble algorithm, where multiple learners are trained to solve the same problem. In contrast to ordinary machine learning approaches which try to learn one hypothesis from training data, ensemble methods try to construct a set of hypotheses and combine them to use.

** Q4 What does it mean to tune the parameters of an algorithm, and what can happen if you don’t do this well?  How did you tune the parameters of your particular algorithm? (Some algorithms do not have parameters that you need to tune -- if this is the case for the one you picked, identify and briefly explain how you would have done it for the model that was not your final choice or a different model that does utilize parameter tuning. **

Machine learning mostly employs a gradient based method of optimizing a large array of parameters. These parameters when well set can result in a system working properly.

If it is not done well then it can make result worse most of the score part is dependent upon parameters tuning .

The KNeighborsClassifier with n_neighbors of 5 gave the best results - more so than KMeans - and was thus selected.
For any other value of n_neighbors parameter precision and recall drops down to an unconsiderable value.

I have used GridSearchCV for tuning in the following parameters and using a stratified shuffle split on a thousand fold on KNeighborsClassifier:
metric, weights, and n_neighbors

** Q5 What is validation, and what’s a classic mistake you can make if you do it wrong? How did you validate your analysis? **

Validation is performed in order to estimate how well model has been trained and to estimate model properties (mean error for numeric predictors, classification errors for classifiers, recall and precision for IR-models etc.)

Classic mistake during validations is overfitting which tunes your model be able to predict your training data very well , but then having it perform poorly on unseen out-of-sample testing data.
Overfitting happens when we use all of the data for training purpose, so data should be divided adequately b/w training and testing.

I have used cross validations to avoid overfitting, which randomly split the data into training and testing data. Then the model can train on the training data, and be validated on the testing data.
We set test_size=0.3 i.e 30% testing and 70% training data.

** Q6 Give at least 2 evaluation metrics and your average performance for each of them.  Explain an interpretation of your metrics that says something human-understandable about your algorithm’s performance. **

I have used 3 evaluation metrices i.e 'Precision', 'Recall' and 'Accuracy'.

Accuracy is the ratio of correct predictions out of its total, Here it means out of total persons of interest predicted how much are true.

Precision can be thought of as the ratio of how often your model is actually correct in identifying a positive label to the total times it guesses a positive label. A higher precision score would mean less false positives.
Here we were using the model to judge whether or not to investigate someone as a possible person of interest, it would be how often the people we chose to investigate turned out to really be persons of interest.

Recall can be thought of as the ratio of how often your model correctly identifies a label as positive to how many total positive labels there actually are. A higher recall score would mean less false negatives. 
Here we were using the model to decide whether or not to investigate someone as a possible person of interest, it would be how many persons of interest did we identify out of the total amount of persons of interest that there were.

Result of KNeighbours Classifier
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
Pipeline(steps=[('classifier', KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
           metric_params=None, n_jobs=1, n_neighbors=5, p=2,
           weights='uniform'))])
	Accuracy: 0.87931	Precision: 0.72950	Recall: 0.34250	F1: 0.46614	F2: 0.38315
	Total predictions: 13000	True positives:  685	False positives:  254	False negatives: 1315	True negatives: 10746

Result of AdaBoost Classifier
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
Pipeline(steps=[('classifier', AdaBoostClassifier(algorithm='SAMME.R', base_estimator=None,
          learning_rate=1.0, n_estimators=100, random_state=None))])
	Accuracy: 0.78600	Precision: 0.30193	Recall: 0.29800	F1: 0.29995	F2: 0.29878
	Total predictions: 13000	True positives:  596	False positives: 1378	False negatives: 1404	True negatives: 9622

'''Using GridsearchCV for tuning parameters'''                        
KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='manhattan',
           metric_params=None, n_jobs=1, n_neighbors=6, p=2,
           weights='distance')
0.870923076923
Final Result after tuning the parameters
[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
Pipeline(steps=[('classifier', KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='manhattan',
           metric_params=None, n_jobs=1, n_neighbors=5, p=2,
           weights='uniform'))])
	Accuracy: 0.88554	Precision: 0.74951	Recall: 0.38450	F1: 0.50826	F2: 0.42599
	Total predictions: 13000	True positives:  769	False positives:  257	False negatives: 1231	True negatives: 10743



This shows that mean precision and recall is quite high compared to others in KNeighbours classifier and also accuracy is quite good.


```python

```
