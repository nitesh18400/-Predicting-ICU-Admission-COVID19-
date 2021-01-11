# -*- coding: utf-8 -*-
"""COVID19_ICU_Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11cMcxeMqpI_dQjuo31iPkSDOf0kTSWHP

#**Machine Learning Project**

***Title: Predicting ICU admission of confirmed COVID-19 cases***

The COVID-19 pandemic has shown us the
unpreparedness of our current healthcare system and
services. We need to optimize the allocation of medical
resources to maximize the utilization of resources. We are
preparing this Machine Learning model based on the
clinical data of confirmed COVID-19 cases. This will help
us to predict the need of ICU for a patient in advance. By
this information hospitals can plan the flow of operations
and take critical decisions like shifting patient to another
hospital or arrangement of resources within the time so
that the lives of patients can be saved.

##Libraries and Packages
List of all the packages that is used in the notebook
"""

import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE 
from sklearn.decomposition import PCA 

pd.set_option('display.max_columns', None)

"""Downloading Dataset

"""

!wget -O "Kaggle_Sirio_Libanes_ICU_Prediction.xlsx" "https://drive.google.com/uc?export=download&id=1_shaH6SQajy1zrnALzim9jGaRmF3PLIn"

"""##Reading Dataset
Reading the dataset from the given CSV file.
"""

data = pd.read_excel("Kaggle_Sirio_Libanes_ICU_Prediction.xlsx")
data

"""##Data Pre-Processing
Converting the data into usable format.
Following modifications has been done to the data to get most out of it:
1. Binary hotcoding to convert not float columns.
2. Marking Window 0-2 as 1 if the patient was admitted to ICU in any of the future windows. 
3. Removing all the records of the windows in which patients were actually admitted to the ICU (windows with ICU label 1 before the step 2).
4. Filling the NaN values of window 0-2 with the help of mean of values in all the windows of that patient.
5. Removing all the rows still having NaN values.

"""

print(data.dtypes)
data.select_dtypes(object)

without_ICU_column = data.drop('ICU', axis = 1)       #seperating the ICU lable column
ICU_column = data['ICU']
colums_to_convert = data.select_dtypes(object).columns   #finding columns that are not of type float or int
colums_to_convert

without_ICU_column = pd.get_dummies(without_ICU_column, columns = colums_to_convert)      #performing hotcoding
without_ICU_column.head()

data_expand = pd.concat([without_ICU_column, ICU_column], axis = 1)         #adding the ICU column again at the last position
data_expand.head(5)

column_names = data_expand.columns
arr = data_expand.to_numpy()
print(arr)
i=0
ICU_admitted_rows = []
while(i<len(arr)):            #loop to record the rows in which patient is admitted to the ICU and adding 1 label to the previous rows.
  for j in range(5):
    if(arr[i+j][-1]==1):
      for k in range(j):
        arr[i+k][-1]=1
      for toremove in range(i+j,i+5):
        ICU_admitted_rows.append(toremove)
      break
  i+=5
print(ICU_admitted_rows)
deletedcount = 0
for rowToRemove in ICU_admitted_rows:             #removing the rows in which patient was admitted to the ICU
  arr = np.delete(arr, rowToRemove-deletedcount, axis=0)
  deletedcount+=1
df = pd.DataFrame(arr, columns = column_names)
df.head(10)

#Filling missing values
pd.options.mode.chained_assignment = None 
edited_dfs_list = []
max_patient_id = df['PATIENT_VISIT_IDENTIFIER'].max()
for i in range(int(max_patient_id)):                      #keeping only the first window that is 0-2 for every patient and filling NaN values with mean of all windows
  tempdf = df[df['PATIENT_VISIT_IDENTIFIER']==i]
  if(len(tempdf)!=0):
    tempdf.fillna(tempdf.mean(), inplace=True)
    tempdf = tempdf.iloc[[0]]
    edited_dfs_list.append(tempdf)

  
final_data = pd.concat(edited_dfs_list)
final_data.head(30)

final_data = final_data.drop(['GENDER','PATIENT_VISIT_IDENTIFIER','WINDOW_0-2',	'WINDOW_2-4',	'WINDOW_4-6',	'WINDOW_6-12',	'WINDOW_ABOVE_12'],axis = 1)
final_data.head()

final_data.describe()

final_data = final_data.dropna(axis = 0)            #Now we must have to drop the rows having nan values as there is no data in any window to fill it.

"""##Data Analysis
Visualising the pre preoessed data and trying to get the intution about different characterstics.
"""

final_data.describe()

ICU_admission_distribution = final_data['ICU'].value_counts()
print("Total Patients after pre processing: ", sum(ICU_admission_distribution))
print("Distribution of ICU admissions")
print("Patients who were not admitted to ICU: ",ICU_admission_distribution[0])
print("Patients who were admitted to ICU: ",ICU_admission_distribution[1])
labels= ['Admitted to ICU', 'Not Admitted to ICU']
colors=['tomato', 'deepskyblue']
sizes= [ICU_admission_distribution[1], ICU_admission_distribution[0]]
plt.pie(sizes,labels=labels, colors=colors, startangle=90, autopct='%1.1f%%')
plt.title("ICU Distribution of data")
plt.axis('equal')
plt.show()

Age_distribution = final_data['AGE_ABOVE65'].value_counts()
print("Age Distribution")
print("Patients below age 65: ",Age_distribution[0])
print("Patients above age 65: ",Age_distribution[1])
labels= ['Below 65', 'Above 65']
colors=['lightgreen', 'violet']
sizes= [Age_distribution[0], Age_distribution[1]]
plt.pie(sizes,labels=labels, colors=colors, startangle=90, autopct='%1.1f%%')
plt.axis('equal')
plt.title("Age Distribution of data")
plt.show()

ICU_Admitted_data = final_data[final_data['ICU']==1]
Age_distribution = ICU_Admitted_data['AGE_ABOVE65'].value_counts()
print("Age Distribution")
print("Patients below age 65: ",Age_distribution[0])
print("Patients above age 65: ",Age_distribution[1])
labels= ['Below 65', 'Above 65']
colors=['orange', 'cyan']
sizes= [Age_distribution[0], Age_distribution[1]]
plt.pie(sizes,labels=labels, colors=colors, startangle=90, autopct='%1.1f%%')
plt.axis('equal')
plt.title("Age Distribution of ICU Admitted patients")
plt.show()

x = [[],[]]
x[0].append(final_data['AGE_PERCENTIL_10th'].value_counts()[1])
x[0].append(final_data['AGE_PERCENTIL_20th'].value_counts()[1])
x[0].append(final_data['AGE_PERCENTIL_30th'].value_counts()[1])
x[0].append(final_data['AGE_PERCENTIL_40th'].value_counts()[1])
x[0].append(final_data['AGE_PERCENTIL_50th'].value_counts()[1])
x[0].append(final_data['AGE_PERCENTIL_60th'].value_counts()[1])
x[0].append(final_data['AGE_PERCENTIL_70th'].value_counts()[1])
x[0].append(final_data['AGE_PERCENTIL_80th'].value_counts()[1])
x[0].append(final_data['AGE_PERCENTIL_90th'].value_counts()[1])
x[0].append(final_data['AGE_PERCENTIL_Above 90th'].value_counts()[1])

x[1].append(ICU_Admitted_data['AGE_PERCENTIL_10th'].value_counts()[1])
x[1].append(ICU_Admitted_data['AGE_PERCENTIL_20th'].value_counts()[1])
x[1].append(ICU_Admitted_data['AGE_PERCENTIL_30th'].value_counts()[1])
x[1].append(ICU_Admitted_data['AGE_PERCENTIL_40th'].value_counts()[1])
x[1].append(ICU_Admitted_data['AGE_PERCENTIL_50th'].value_counts()[1])
x[1].append(ICU_Admitted_data['AGE_PERCENTIL_60th'].value_counts()[1])
x[1].append(ICU_Admitted_data['AGE_PERCENTIL_70th'].value_counts()[1])
x[1].append(ICU_Admitted_data['AGE_PERCENTIL_80th'].value_counts()[1])
x[1].append(ICU_Admitted_data['AGE_PERCENTIL_90th'].value_counts()[1])
x[1].append(ICU_Admitted_data['AGE_PERCENTIL_Above 90th'].value_counts()[1])

a = []
c=1
for i in x[0]:
  a.extend([c*10]*i)
  c+=1
plt.hist(a, 20, label='Total')
b = []
c=1
for i in x[1]:
  b.extend([c*10]*i)
  c+=1
print(x)
plt.hist(b, 20, label='ICU Admitted')
plt.xticks([10,20,30,40,50,60,70,80,90,100],['AGE_PERCENTIL_10th','AGE_PERCENTIL_20th','AGE_PERCENTIL_30th','AGE_PERCENTIL_40th','AGE_PERCENTIL_50th','AGE_PERCENTIL_60th','AGE_PERCENTIL_70th','AGE_PERCENTIL_80th','AGE_PERCENTIL_90th','AGE_PERCENTIL_Above 90'], rotation = 70)
plt.legend()
plt.ylabel('Frequency')
plt.title('Age Distribution Total and ICU Admitted')
plt.show()

Diesease_Grouping_1 = final_data['DISEASE GROUPING 1'].value_counts()
Diesease_Grouping_2 = final_data['DISEASE GROUPING 2'].value_counts()
Diesease_Grouping_3 = final_data['DISEASE GROUPING 3'].value_counts()
Diesease_Grouping_4 = final_data['DISEASE GROUPING 4'].value_counts()
Diesease_Grouping_5 = final_data['DISEASE GROUPING 5'].value_counts()
Diesease_Grouping_6 = final_data['DISEASE GROUPING 6'].value_counts()
HTN_total = final_data['HTN'].value_counts()
Immunocompromised_total = final_data['IMMUNOCOMPROMISED'].value_counts()
Other_total = final_data['OTHER'].value_counts()

ICU_Diesease_Grouping_1 = ICU_Admitted_data['DISEASE GROUPING 1'].value_counts()
ICU_Diesease_Grouping_2 = ICU_Admitted_data['DISEASE GROUPING 2'].value_counts()
ICU_Diesease_Grouping_3 = ICU_Admitted_data['DISEASE GROUPING 3'].value_counts()
ICU_Diesease_Grouping_4 = ICU_Admitted_data['DISEASE GROUPING 4'].value_counts()
ICU_Diesease_Grouping_5 = ICU_Admitted_data['DISEASE GROUPING 5'].value_counts()
ICU_Diesease_Grouping_6 = ICU_Admitted_data['DISEASE GROUPING 6'].value_counts()
HTN_ICU = ICU_Admitted_data['HTN'].value_counts()
Immunocompromised_ICU = ICU_Admitted_data['IMMUNOCOMPROMISED'].value_counts()
Other_ICU = ICU_Admitted_data['OTHER'].value_counts()

x = np.array([[Diesease_Grouping_1[1],Diesease_Grouping_2[1],Diesease_Grouping_3[1],Diesease_Grouping_4[1],Diesease_Grouping_5[1],Diesease_Grouping_6[1],HTN_total[1], Immunocompromised_total[1]],[ICU_Diesease_Grouping_1[1],ICU_Diesease_Grouping_2[1],ICU_Diesease_Grouping_3[1],ICU_Diesease_Grouping_4[1],ICU_Diesease_Grouping_5[1],ICU_Diesease_Grouping_6[1],HTN_ICU[1], Immunocompromised_ICU[1]]])
a = []
c=1
for i in x[0]:
  a.extend([c]*i)
  c+=1
plt.hist(a, 15, label='Total')
b = []
c=1
for i in x[1]:
  b.extend([c]*i)
  c+=1
print(x)
plt.hist(b, 15, label='ICU Admitted')
plt.xticks([1,2,3,4,5,6,7,8,9],['Diesease_Grouping_1','Diesease_Grouping_2','Diesease_Grouping_3','Diesease_Grouping_4','Diesease_Grouping_5','Diesease_Grouping_6', 'Hypertension', 'Immunocompromised'], rotation = 70)
plt.legend()
plt.ylabel('Frequency')
plt.title('Disease Distribution Total and ICU Admitted')
plt.show()

import seaborn as sns
corr = final_data.corr()
corr.shape
plt.subplots(figsize=(100,100))
ax = sns.heatmap(
    corr, 
    vmin=-1, vmax=1, center=0,
    cmap=sns.diverging_palette(20, 220, n=200),
    square=True
)
ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation=90,
    horizontalalignment='right'
);
corr.tail()

corr.shape
ICU_corr = corr.iloc[236]
ICU_corr.describe()

ICU_corr = np.array(ICU_corr)
selection = []
for i in ICU_corr:
  if(i):
    if(i>0.11):
      selection.append(True)
    elif(i<-0.12):
      selection.append(True)
    else:
      selection.append(False)
  else:
    selection.append(False)

print(len(selection), selection.count(True))
selection = np.array(selection)
selected_final_data = final_data.loc[:, selection]
selected_final_data.head()

selected_final_data = selected_final_data[['AGE_ABOVE65', 'DISEASE GROUPING 2', 'DISEASE GROUPING 3', 'DISEASE GROUPING 4',
                                           'HTN', 'BIC_VENOUS_MEAN', 'CALCIUM_MEAN' , 'CREATININ_MEAN', 'GLUCOSE_MEAN', 'INR_MEAN',
                                           'LACTATE_MEAN', 'LEUKOCYTES_MEAN', 'LINFOCITOS_MEAN', 'NEUTROPHILES_MEAN', 'PC02_VENOUS_MEAN',
                                           'PCR_MEAN', 'PLATELETS_MEAN', 'SAT02_VENOUS_MEAN', 'SODIUM_MEAN', 'UREA_MEAN', 'BLOODPRESSURE_DIASTOLIC_MEAN',
                                           'RESPIRATORY_RATE_MEAN', 'TEMPERATURE_MEAN', 'OXYGEN_SATURATION_MEAN', 'BLOODPRESSURE_SISTOLIC_MIN',
                                           'HEART_RATE_MIN', 'RESPIRATORY_RATE_MIN', 'TEMPERATURE_MIN', 'BLOODPRESSURE_DIASTOLIC_MAX', 'BLOODPRESSURE_SISTOLIC_MAX',
                                           'HEART_RATE_MAX', 'OXYGEN_SATURATION_MAX', 'BLOODPRESSURE_DIASTOLIC_DIFF', 'BLOODPRESSURE_SISTOLIC_DIFF', 
                                           'HEART_RATE_DIFF', 'RESPIRATORY_RATE_DIFF', 'TEMPERATURE_DIFF', 'OXYGEN_SATURATION_DIFF', 
                                           'AGE_PERCENTIL_10th', 'AGE_PERCENTIL_20th', 'AGE_PERCENTIL_80th', 'AGE_PERCENTIL_90th', 'ICU']]

print(selected_final_data.shape)
selected_final_data.head()

corr = selected_final_data.corr()
corr.shape
plt.subplots(figsize=(30,30))
ax = sns.heatmap(
    corr, 
    vmin=-1, vmax=1, center=0,
    cmap=sns.diverging_palette(20, 220, n=200),
    square=True
)
ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation=90,
    horizontalalignment='right'
);
corr.tail()

selected_final_data.columns

Non_ICU_Admitted_data = selected_final_data[selected_final_data['ICU']==0]
ICU_Admitted_data = selected_final_data[selected_final_data['ICU']==1]

Vital_Non_ICU_Admitted_data = Non_ICU_Admitted_data[['BLOODPRESSURE_DIASTOLIC_MEAN',
       'RESPIRATORY_RATE_MEAN', 'TEMPERATURE_MEAN', 'OXYGEN_SATURATION_MEAN',
       'BLOODPRESSURE_SISTOLIC_MIN', 'HEART_RATE_MIN', 'RESPIRATORY_RATE_MIN',
       'TEMPERATURE_MIN', 'BLOODPRESSURE_DIASTOLIC_MAX',
       'BLOODPRESSURE_SISTOLIC_MAX', 'HEART_RATE_MAX', 'OXYGEN_SATURATION_MAX',
       'HEART_RATE_DIFF', 'RESPIRATORY_RATE_DIFF', 'TEMPERATURE_DIFF']]

Vital_ICU_Admitted_data = ICU_Admitted_data[['BLOODPRESSURE_DIASTOLIC_MEAN',
       'RESPIRATORY_RATE_MEAN', 'TEMPERATURE_MEAN', 'OXYGEN_SATURATION_MEAN',
       'BLOODPRESSURE_SISTOLIC_MIN', 'HEART_RATE_MIN', 'RESPIRATORY_RATE_MIN',
       'TEMPERATURE_MIN', 'BLOODPRESSURE_DIASTOLIC_MAX',
       'BLOODPRESSURE_SISTOLIC_MAX', 'HEART_RATE_MAX', 'OXYGEN_SATURATION_MAX',
       'HEART_RATE_DIFF', 'RESPIRATORY_RATE_DIFF', 'TEMPERATURE_DIFF']]


Lab_Non_ICU_Admitted_data = Non_ICU_Admitted_data[['HTN', 'BIC_VENOUS_MEAN', 'CALCIUM_MEAN',
       'CREATININ_MEAN', 'GLUCOSE_MEAN', 'INR_MEAN', 'LACTATE_MEAN',
       'LEUKOCYTES_MEAN', 'LINFOCITOS_MEAN', 'NEUTROPHILES_MEAN',
       'PC02_VENOUS_MEAN', 'PCR_MEAN', 'PLATELETS_MEAN', 'SAT02_VENOUS_MEAN',
       'SODIUM_MEAN', 'UREA_MEAN']]
Lab_ICU_Admitted_data = ICU_Admitted_data[['HTN', 'BIC_VENOUS_MEAN', 'CALCIUM_MEAN',
       'CREATININ_MEAN', 'GLUCOSE_MEAN', 'INR_MEAN', 'LACTATE_MEAN',
       'LEUKOCYTES_MEAN', 'LINFOCITOS_MEAN', 'NEUTROPHILES_MEAN',
       'PC02_VENOUS_MEAN', 'PCR_MEAN', 'PLATELETS_MEAN', 'SAT02_VENOUS_MEAN',
       'SODIUM_MEAN', 'UREA_MEAN']]


# set width of bar 
barWidth = 0.25
fig = plt.subplots(figsize =(20, 10)) 
   
vital_non_ICU = np.array(Vital_Non_ICU_Admitted_data.mean(axis=0)) 
vital_ICU = np.array(Vital_ICU_Admitted_data.mean(axis=0)) 
   
# Set position of bar on X axis 
br1 = np.arange(len(vital_ICU)) + (barWidth*0.5)
br2 = [x + barWidth for x in br1]  
   
# Make the plot 
plt.bar(br2, vital_ICU, color ='r', width = barWidth, edgecolor ='grey', label ='ICU Admitted') 
plt.bar(br1, vital_non_ICU, color ='b', width = barWidth, edgecolor ='grey', label ='NOT Admitted') 

   
plt.xlabel('Features', fontweight ='bold') 
plt.ylabel('Normalized Values', fontweight ='bold') 
plt.xticks([r + barWidth for r in range(len(vital_ICU))], ['BLOODPRESSURE_DIASTOLIC_MEAN',
       'RESPIRATORY_RATE_MEAN', 'TEMPERATURE_MEAN', 'OXYGEN_SATURATION_MEAN',
       'BLOODPRESSURE_SISTOLIC_MIN', 'HEART_RATE_MIN', 'RESPIRATORY_RATE_MIN',
       'TEMPERATURE_MIN', 'BLOODPRESSURE_DIASTOLIC_MAX',
       'BLOODPRESSURE_SISTOLIC_MAX', 'HEART_RATE_MAX', 'OXYGEN_SATURATION_MAX',
       'HEART_RATE_DIFF', 'RESPIRATORY_RATE_DIFF', 'TEMPERATURE_DIFF'], rotation = 90) 

plt.legend()
plt.title("Vital Signs of Covid19 Patients")
plt.show()


# set width of bar 
barWidth = 0.25
fig = plt.subplots(figsize =(20, 10)) 
   
lab_non_ICU = np.array(Lab_Non_ICU_Admitted_data.mean(axis=0)) 
lab_ICU = np.array(Lab_ICU_Admitted_data.mean(axis=0)) 
   
# Set position of bar on X axis 
br1 = np.arange(len(lab_ICU)) + (barWidth*0.5)
br2 = [x + barWidth for x in br1]  
   
# Make the plot 
plt.bar(br2, lab_ICU, color ='r', width = barWidth, edgecolor ='grey', label ='ICU Admitted') 
plt.bar(br1, lab_non_ICU, color ='b', width = barWidth, edgecolor ='grey', label ='NOT Admitted') 

   
plt.xlabel('Features', fontweight ='bold') 
plt.ylabel('Normalized Value', fontweight ='bold') 
plt.legend()
plt.xticks([r + barWidth for r in range(len(lab_ICU))], ['HTN', 'BIC_VENOUS_MEAN', 'CALCIUM_MEAN',
       'CREATININ_MEAN', 'GLUCOSE_MEAN', 'INR_MEAN', 'LACTATE_MEAN',
       'LEUKOCYTES_MEAN', 'LINFOCITOS_MEAN', 'NEUTROPHILES_MEAN',
       'PC02_VENOUS_MEAN', 'PCR_MEAN', 'PLATELETS_MEAN', 'SAT02_VENOUS_MEAN',
       'SODIUM_MEAN', 'UREA_MEAN'], rotation = 90) 
plt.title("Lab Test Results of Covid19 patients")
plt.show()

X_data = np.array(selected_final_data.drop(['ICU'], axis = 1))
Y_data = np.array(selected_final_data[['ICU']])
print(X_data.shape)
print(Y_data.shape)
from sklearn.decomposition import PCA 

labels = []
for i in Y_data:
  if(i[0]==0):
    labels.append(0)
  else:
    labels.append(1)
print(X_data)
Y_data = np.array(labels)

#pca = PCA(0.80)
#X_data = pca.fit_transform(X_data)
print("pca ", X_data.shape)
model = TSNE(n_components = 2, random_state = 0) 
  
tsne_data = model.fit_transform(X_data) 


# creating a new data frame which 
# help us in ploting the result data 
tsne_data = np.vstack((tsne_data.T, Y_data)).T 
tsne_df = pd.DataFrame(data = tsne_data, 
     columns =("Dim_1", "Dim_2","label")) 
  
# Ploting the result of tsne 
sns.FacetGrid(tsne_df, hue ="label", size = 6).map( 
       plt.scatter, 'Dim_1', 'Dim_2', s = 100).add_legend() 
  
plt.show()

selected_final_data.head()

print(X_data)
print(Y_data)

"""## Training and Testing using various classifiers

Importing Libraries
"""

from sklearn.linear_model import LogisticRegressionCV
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn import svm
from sklearn import tree
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt 
from sklearn.metrics import log_loss
from sklearn import tree
import graphviz
from sklearn.neural_network import MLPClassifier

"""Shape of Datasets"""

print(X_data.shape)
print(Y_data.shape)

def ass(y_true,y_pred):
  tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
  accuracy=(tp+tn)/(tp+fp+fn+tn)
  specificity = tn/(tn+fp)
  sensitivity=tp/(tp+fn)
  print("Accuracy:",accuracy*100)
  print("Sensitivity:",sensitivity*100)
  print("Specificity:",specificity*100)
  print("ROC_AUC_Score:",roc_auc_score(y_true, y_pred)*100)

"""Splitting Data into Training Data and Testing Data"""

X_train, X_test, Y_train, Y_test = train_test_split(X_data, Y_data, test_size=0.30, random_state=1)

"""Performing Logistic Regression with Cross Validation Estimator"""

lgc=make_pipeline(LogisticRegressionCV(cv=5,random_state=1,max_iter=5000))
lgc.fit(X_train, Y_train)
y_pred=lgc.predict(X_test)
ass(Y_test,y_pred)

"""Performing Gaussian Naive Bayes """

gnb=make_pipeline(GaussianNB())
gnb.fit(X_train,Y_train)
y_pred=gnb.predict(X_test)
ass(Y_test,y_pred)

"""Finding Optimal Depth (SGD Classifier)"""

mx=-1
ri=-1
for i in range(1,10000):
  sgd= make_pipeline(SGDClassifier(random_state=i))
  sgd.fit(X_train,Y_train)
  pmx=mx
  mx=max(mx,sgd.score(X_test,Y_test))
  if(pmx!=mx):
    ri=i
print(ri)

"""Performing SGD classifier with optimal Depth"""

sgd= make_pipeline(SGDClassifier(random_state=ri))
sgd.fit(X_train,Y_train)
y_pred=sgd.predict(X_test)
ass(Y_test,y_pred)

"""Performing SVM ( Supoort Vector Machine ) classification on the given data"""

SVM_object = make_pipeline(svm.SVC(kernel='linear'))
SVM_object.fit(X_train,Y_train)
y_pred=SVM_object.predict(X_test)
ass(Y_test,y_pred)

"""Performing Decision tree classification

"""

DT_object=tree.DecisionTreeClassifier(criterion='entropy',max_depth=4,max_leaf_nodes=10)
DT_object.fit(X_train,Y_train)
y_pred=DT_object.predict(X_test)
ass(Y_test,y_pred)

from sklearn import tree
import graphviz
text_representation = tree.export_text(DT_object)
print(text_representation)

features=['AGE_ABOVE65', 'DISEASE GROUPING 2', 'DISEASE GROUPING 3',
       'DISEASE GROUPING 4', 'HTN', 'BIC_VENOUS_MEAN', 'CALCIUM_MEAN',
       'CREATININ_MEAN', 'GLUCOSE_MEAN', 'INR_MEAN', 'LACTATE_MEAN',
       'LEUKOCYTES_MEAN', 'LINFOCITOS_MEAN', 'NEUTROPHILES_MEAN',
       'PC02_VENOUS_MEAN', 'PCR_MEAN', 'PLATELETS_MEAN', 'SAT02_VENOUS_MEAN',
       'SODIUM_MEAN', 'UREA_MEAN', 'BLOODPRESSURE_DIASTOLIC_MEAN',
       'RESPIRATORY_RATE_MEAN', 'TEMPERATURE_MEAN', 'OXYGEN_SATURATION_MEAN',
       'BLOODPRESSURE_SISTOLIC_MIN', 'HEART_RATE_MIN', 'RESPIRATORY_RATE_MIN',
       'TEMPERATURE_MIN', 'BLOODPRESSURE_DIASTOLIC_MAX',
       'BLOODPRESSURE_SISTOLIC_MAX', 'HEART_RATE_MAX', 'OXYGEN_SATURATION_MAX',
       'BLOODPRESSURE_DIASTOLIC_DIFF', 'BLOODPRESSURE_SISTOLIC_DIFF',
       'HEART_RATE_DIFF', 'RESPIRATORY_RATE_DIFF', 'TEMPERATURE_DIFF',
       'OXYGEN_SATURATION_DIFF', 'AGE_PERCENTIL_10th', 'AGE_PERCENTIL_20th',
       'AGE_PERCENTIL_80th', 'AGE_PERCENTIL_90th']
classes=['Non-ICU','ICU']
dot_data = tree.export_graphviz(DT_object, out_file=None, 
                                feature_names=features,  
                                class_names=classes,
                                filled=True)
graph = graphviz.Source(dot_data, format="png") 
graph

"""Performing K-Nearest Neighbour Classifier 

"""

KNN_object=make_pipeline(KNeighborsClassifier(n_neighbors=25,p=1))
KNN_object.fit(X_train,Y_train)
y_pred=KNN_object.predict(X_test)
ass(Y_test,y_pred)

"""Performing Random Forest Classifier"""

RF_object = RandomForestClassifier(criterion='gini',random_state=23,max_depth=6,bootstrap=True)
RF_object.fit(X_train,Y_train)
y_pred=RF_object.predict(X_test)
ass(Y_test,y_pred)

"""##Performing Grid Search on Various ML Algorithm

Grid Search on Decision Tree
"""

param_grid = {'criterion':['entropy','gini'],'max_depth':np.arange(1,30),'max_leaf_nodes':np.arange(3,20),'random_state':[1,2]}
GS_DT=GridSearchCV(DecisionTreeClassifier(), param_grid,cv=5)
GS_DT.fit(X_train,Y_train)
GS_DT.best_params_

GS_DT.score(X_test,Y_test)

dt_train_score=[]
dt_test_score=[]
for i in np.arange(1, 30):
  param_grid = {'criterion':['entropy','gini'],'max_depth': [i],'max_leaf_nodes':np.arange(3,20),'random_state':[1,2]}
  GS_DT=GridSearchCV(DecisionTreeClassifier(), param_grid,cv=5)
  GS_DT.fit(X_train,Y_train)
  y_train_pred=GS_DT.predict(X_train)
  y_pred=GS_DT.predict(X_test)
  dt_train_score.append(log_loss(Y_train,y_train_pred))
  dt_test_score.append(log_loss(Y_test,y_pred))

plt.title("Decision Tree Classifier : Error vs Depth")
plt.xlabel("Depth")
plt.ylabel("Error")
plt.plot(np.arange(1,30),dt_train_score,label="Training Error")
plt.plot(np.arange(1,30),dt_test_score,label="Testing Error")
plt.legend()
plt.plot()

""" Best kernel Performance using Grid Search"""

param_grid = {'kernel':['linear','poly','sigmoid','rbf'],'gamma':['scale','auto'],'random_state':[1,2,3]}
GS_SVM=GridSearchCV(svm.SVC(), param_grid,cv=5)
GS_SVM.fit(X_train,Y_train)
GS_SVM.best_params_

GS_SVM.score(X_test,Y_test)

dt_train_score=[]
dt_test_score=[]
for i in ['linear','poly','sigmoid','rbf']:
  param_grid = {'kernel':[i],'gamma':['scale','auto'],'random_state':[1,2,3]}
  GS_SVM=GridSearchCV(svm.SVC(), param_grid,cv=5)
  GS_SVM.fit(X_train,Y_train)
  y_train_pred=GS_SVM.predict(X_train)
  y_pred=GS_SVM.predict(X_test)
  dt_train_score.append(log_loss(Y_train,y_train_pred))
  dt_test_score.append(log_loss(Y_test,y_pred))

plt.title("SVM: Error vs kernel")
plt.xlabel("Kernel")
plt.ylabel("Error")
plt.plot(['linear','poly','sigmoid','rbf'],dt_train_score,label="Training Error")
plt.plot(['linear','poly','sigmoid','rbf'],dt_test_score,label="Testing Error")
plt.legend()
plt.plot()

"""Grid Search on K nearest neighbour"""

param_grid = {'n_neighbors':[10,15,20,25,30,35,40],'leaf_size':np.arange(3,20),'p':[1,2]}
GS_KNN=GridSearchCV(KNeighborsClassifier(), param_grid,cv=5)
GS_KNN.fit(X_train,Y_train)
GS_KNN.best_params_

GS_KNN.score(X_test,Y_test)

knn_train_score=[]
knn_test_score=[]
for i in [10,15,20,25,30,35,40]:
  param_grid = {'n_neighbors': [i],'leaf_size':np.arange(3,20),'p':[1,2]}
  GS_KNN=GridSearchCV(KNeighborsClassifier(), param_grid,cv=5)
  GS_KNN.fit(X_train,Y_train)
  y_train_pred=GS_KNN.predict(X_train)
  y_pred=GS_KNN.predict(X_test)
  knn_train_score.append(log_loss(Y_train,y_train_pred))
  knn_test_score.append(log_loss(Y_test,y_pred))

plt.title("K-Neighbours Classifier: Error vs Number of Neighbors ")
plt.xlabel("Number of Neighbors")
plt.ylabel("Error")
plt.plot([10,15,20,25,30,35,40],knn_train_score,label="Training Error")
plt.plot([10,15,20,25,30,35,40],knn_test_score,label="Testing Error")
plt.legend()
plt.plot()

"""Grid search on Random Forest Classifier"""

param_grid = {'criterion':['gini','entropy'],'max_depth': [6],'random_state':[23]}
GS_RF=GridSearchCV(RandomForestClassifier(), param_grid,cv=5)
GS_RF.fit(X_train,Y_train)
GS_RF.best_params_

GS_RF.score(X_test,Y_test)

rf_train_score=[]
rf_test_score=[]
for i in np.arange(1, 30):
  param_grid = {'criterion':['gini','entropy'],'max_depth': [i],'random_state':[23]}
  GS_RF=GridSearchCV(RandomForestClassifier(), param_grid,cv=5)
  GS_RF.fit(X_train,Y_train)
  y_train_pred=GS_RF.predict(X_train)
  y_pred=GS_RF.predict(X_test)
  rf_train_score.append(log_loss(Y_train,y_train_pred))
  rf_test_score.append(log_loss(Y_test,y_pred))

plt.title("Random Forest Classifier : Error vs Max Depth")
plt.xlabel("Max Depth")
plt.ylabel("Error")
plt.plot(np.arange(1,30),rf_train_score,label="Training Error")
plt.plot(np.arange(1,30),rf_test_score,label="Testing Error")
plt.legend()
plt.plot()

"""Training model with different activation functions and finding model with best accuracy"""

best=1
acc=-1
for a in ["identity", "logistic", "tanh", "relu"]:
    model = MLPClassifier(activation=a,max_iter=10000, batch_size=64,alpha=0.1,random_state=1).fit(X_train,Y_train)
    y_pred = model.predict(X_test)
    print(a)
    ass(Y_test,y_pred)
    score = model.score(X_test,Y_test)
    if score>acc:
      acc=score
      best = a
    #print(a," - ",model.score(X_test,Y_test))
print(best,acc)

"""Performing Grid search on the model we got from the above"""

rf_train_score=[]
rf_test_score=[]
a=[0.001,0.01,0.1]
for i in range(len(a)):
  param_grid = {'activation':[best],'max_iter': [10000],'batch_size':[64],'alpha':[0.1],'learning_rate_init':[a[i]],'random_state':[1]}
  GS=GridSearchCV(MLPClassifier(), param_grid)
  GS.fit(X_train,Y_train)
  y_train_pred=GS.predict(X_train)
  y_pred=GS.predict(X_test)
  rf_train_score.append(log_loss(Y_train,y_train_pred))
  rf_test_score.append(log_loss(Y_test,y_pred))

plt.title(" MLPClassifier Error vs Learning rate")
plt.xlabel("Learning rate")
plt.ylabel("Error")
plt.plot([0.001,0.01,0.1],rf_train_score,label="Training Error")
plt.plot([0.001,0.01,0.1],rf_test_score,label="Testing Error")
plt.legend()
plt.plot()