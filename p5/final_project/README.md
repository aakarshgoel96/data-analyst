
# Intro to Machine Learning Final Project

## Identifying Fraud from Enron Emails 

In 2000, Enron was one of the largest companies in the United States. By 2002, it had collapsed into bankruptcy due to widespread corporate fraud. In the resulting Federal investigation, a significant amount of typically confidential information entered into the public record, including tens of thousands of emails and detailed financial data for top executives.

In this project, I used python's scikit-learn library that consists of various machine learning algorithms to build person of interest identifier based on financial and email data made public as a result of the Enron scandal. This data has been combined with a hand-generated list of persons of interest (POI) in the fraud case, which means individuals who were indicted, reached a settlement or plea deal with the government, or testified in exchange for prosecution immunity.

Run poi_id.py to view the selected and tuned feature selections, and the machine learning algorithms' performances. Run tester.py to view the performance of the chosen algorithm, K-nearest neighbors classifier. The following is a snippet of the scores returned from tester.py


```python
aakarsh@aakarsh-HP-Pavilion-15-Notebook-PC:/media/aakarsh/New Volume/udacity/data-analyst/p5/final_project$ python tester.py
[0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0]
Pipeline(steps=[('scaler', StandardScaler(copy=True, with_mean=True, with_std=True)), ('classifier', KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
           metric_params=None, n_jobs=1, n_neighbors=3, p=2,
           weights='uniform'))])
	Accuracy: 0.82967	Precision: 0.30814	Recall: 0.42800	F1: 0.35831	F2: 0.39711
	Total predictions: 9000	True positives:  428	False positives:  961	False negatives:  572	True negatives: 7039


```

I have chosen KNeighboursClassifier although AdaBoost give slightly better result because time taken in KNeighbours is very less compared to adaboost.  

## Enron Submission Free-Response Questions

** Q1 Summarize for us the goal of this project and how machine learning is useful in trying to accomplish it. As part of your answer, give some background on the dataset and how it can be used to answer the project question. Were there any outliers in the data when you got it, and how did you handle those? **

The goal of this project is to choose a combination of features, financial and email, of former Enron employees and choose an appropriate machine learning algorithm to predict whether that person is considered a person of interest (POI) or not. It should be noted that this dataset contained labeled data where POIs were flagged and as such the purpose of this project is to build a supervised classification model that could be used on other unlabeled datasets.

The Enron dataset contained 146 records with 14 financial features, 6 email features, and 1 labeled feature for POI. Out of the latter dataset, 18 people were labeled as persons of interest (POI). Interestingly, I had to omit email_address from the email features list due to it being a string while all the other features were integer values; it was hard to justify keeping unique email addresses as a POI identifier for fraud. Furthermore, I visualize the dataset's feature to conduct some basic exploratory data analysis. 

Removed all the columns in the dataset whose half of the values are NaN type i.e >72. TOTAL field is removed as it has no relation with the model. Handled remaining NaN values using numpynan.

Employees with very high salary were outliers so 'salary' is scaled using MinMaxScaler.

** Q2 What features did you end up using in your POI identifier, and what selection process did you use to pick them? Did you have to do any scaling? Why or why not? As part of the assignment, you should attempt to engineer your own feature that does not come ready-made in the dataset -- explain what feature you tried to make, and the rationale behind it. (You do not necessarily have to use it in the final analysis, only engineer and test it.) In your feature selection step, if you used an algorithm like a decision tree, please also give the feature importances of the features that you use, and if you used an automated feature selection function like SelectKBest, please report the feature scores and reasons for your choice of parameter values.**

I have used two existing features 'poi' & 'shared_receipt_with_poi' also generated two new features from existing features i.e 'fraction_to_poi' & 'fraction_from_poi' these were the fractions of messages sent and recieved by poi's.
These new features are made because they depict features in more proper and required form suitable to find the results.
I chose these features by analyzing the dataset manually and from lectures in the course and selected them randomly which gives best result.

I used a min-max scaler, StandardScaler. The scaler was very important to normalize the data as features had different units and varied widely by several orders of magnitude in some cases. Standardization of a dataset is a common requirement for many machine learning estimators: they might behave badly if the individual feature do not more or less look like standard normally distributed data (e.g. Gaussian with 0 mean and unit variance).


**Q3 What algorithm did you end up using? What other one(s) did you try? How did model performance differ between algorithms?**

The algorithm I end up using was the K-nearest neighbors classifier. I selected it purely based on its performace in accuracy, precision and recall, as well as it's simplicity to use. I tried using the following models as well: "Decision Tree", "Random Forest", "AdaBoost", "Naive Bayes".

Different algoritms classify the data in different manners every algoritms and its parameters work differently for different datasets like AdaBoost is a kind of ensemble algorithm, where multiple learners are trained to solve the same problem. In contrast to ordinary machine learning approaches which try to learn one hypothesis from training data, ensemble methods try to construct a set of hypotheses and combine them to use.

** Q4 What does it mean to tune the parameters of an algorithm, and what can happen if you don’t do this well?  How did you tune the parameters of your particular algorithm? (Some algorithms do not have parameters that you need to tune -- if this is the case for the one you picked, identify and briefly explain how you would have done it for the model that was not your final choice or a different model that does utilize parameter tuning. **

Machine learning mostly employs a gradient based method of optimizing a large array of parameters. These parameters when well set can result in a system working properly.

If it is not done well then it can make result worse most of the score part is dependent upon parameters tuning .

The KNeighborsClassifier with n_neighbors of 3 gave the best results - more so than KMeans - and was thus selected.
For any other value of n_neighbors parameter precision and recall drops down to an unconsiderable value.

** Q5 What is validation, and what’s a classic mistake you can make if you do it wrong? How did you validate your analysis? **

Validation is performed in order to estimate how well model has been trained and to estimate model properties (mean error for numeric predictors, classification errors for classifiers, recall and precision for IR-models etc.)

Classic mistake during validations is overfitting which tunes your model be able to predict your training data very well , but then having it perform poorly on unseen out-of-sample testing data.
I have used cross validations to avoid overfitting, which randomly split the data into training and testing data. Then the model can train on the training data, and be validated on the testing data.

** Q6 Give at least 2 evaluation metrics and your average performance for each of them.  Explain an interpretation of your metrics that says something human-understandable about your algorithm’s performance. **

I have used 3 evaluation metrices i.e 'Precision', 'Recall' and 'Accuracy'.

Accuracy is the ratio of correct predictions out of its total.

Precision can be thought of as the ratio of how often your model is actually correct in identifying a positive label to the total times it guesses a positive label. A higher precision score would mean less false positives.

Recall can be thought of as the ratio of how often your model correctly identifies a label as positive to how many total positive labels there actually are. A higher recall score would mean less false negatives. 


```python
Result of KMeans Classifier
Pipeline(steps=[('scaler', StandardScaler(copy=True, with_mean=True, with_std=True)), ('classifier', KMeans(copy_x=True, init='k-means++', max_iter=300, n_clusters=2, n_init=10,
    n_jobs=1, precompute_distances='auto', random_state=None, tol=0.001,
    verbose=0))])

Processing....................................................................................................done.

precision: 0.236654006281
recall:    0.5104
accuracy:    0.546977272727


Result of KNeighbours Classifier
Pipeline(steps=[('scaler', StandardScaler(copy=True, with_mean=True, with_std=True)), ('classifier', KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
           metric_params=None, n_jobs=1, n_neighbors=3, p=2,
           weights='uniform'))])

Processing....................................................................................................done.

precision: 0.5
recall:    0.4
accuracy:    0.886363636364

```

This shows that mean precision and recall is quite high compared to others in KNeighbours classifier and also accuracy is quite good.
Precision :if we were using the model to judge whether or not to investigate someone as a possible person of interest, it would be how often the people we chose to investigate turned out to really be persons of interest.
Recall: if we were use the model to decide whether or not to investigate someone as a possible person of interest, it would be how many persons of interest did we identify out of the total amount of persons of interest that there were.
Accuracy: Whether predicted results really match original results.
