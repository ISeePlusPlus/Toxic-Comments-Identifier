# -*- coding: utf-8 -*-
"""seminar_toxic_comments.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sWhkWcZ7LCxXtmlUwF7hTjt1Z5iQ2UJn

# Seminar - toxic comments identification and classification #
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import re

from google.colab import drive
drive.mount('/content/drive', force_remount=True)
main_path = r'/content/drive/My Drive/Seminar/data'

class_names = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
train = pd.read_csv(main_path + "/train.csv").fillna('')
#test = pd.read_csv(main_path + "/test.csv").fillna('')

train, test = train_test_split(train, test_size=0.2)

print(train.shape)
print(test.shape)
y_test = test.iloc[:,2:]
print(y_test)
print("\n  train Data: \n",train.iloc[:,1:].head(5))
for label in class_names:
  test = test.drop(label,axis=1)
print("\n  Test Data: \n",test.iloc[:,1:].head(5))

print(train.shape)
print(test.shape)

train_text = train['comment_text']
test_text = test['comment_text']
print("Empty Comment Cells In Train: \n", train.isna().sum())
print("Empty Comment Cells In Test: \n",test.isna().sum())

"""### No null values in dataset, no need to preform preprocessing on null/missing values ###"""

train.describe(percentiles=[])

test.describe()

sns.set(font_scale = 2)
plt.figure(figsize=(15,10))
ax= sns.barplot(class_names, train.iloc[:,2:].sum().values)
plt.title("Comments in each category", fontsize=24)
plt.ylabel('Number of comments', fontsize=20)
plt.xlabel('Comment Type ', fontsize=20)
rects = ax.patches
labels = train.iloc[:,2:].sum().values
for rect, label in zip(rects, labels):
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2, height + 5, label, ha='center', va='bottom', fontsize=18)
plt.show()

train['char_length'] = train['comment_text'].apply(lambda x: len(str(x)))
unlabeled_comments = train[(train['toxic'] ==0) & (train['severe_toxic'] == 0) & (train['obscene'] == 0) & 
                            (train['threat'] == 0) & (train['insult'] == 0) & (train['identity_hate'] == 0)]
labeled_comments = train[(train['toxic'] !=0) | (train['severe_toxic'] != 0) | (train['obscene'] != 0) | 
                            (train['threat'] != 0) | (train['insult'] != 0) | (train['identity_hate'] != 0)]

print('out of all comments, unlabeled comments are: ', len(unlabeled_comments)/len(train) *100, "%")

print('Total samples in train:', len(train))
print('Total samples in test:', len(test))
sum = train[class_names].sum()
print('Total samples with some label:\n', sum.sort_values())

"""### Overall char lenght for train set"""

data = [100,200,400,600,800,1000,1500.,2000,2500] 
fig, ax = plt.subplots()
sns.distplot(train['char_length'], ax=ax)
plt.xlim(0, 2500)
plt.show()

"""### Char lenght for labeled comments"""

data = [100,200,400,600,800,1000,1500.,2000,2500] 
fig, ax = plt.subplots()
sns.distplot(labeled_comments['char_length'], ax=ax)
plt.xlim(0, 2500)
plt.show()

"""### Char lenght for unlabeled comments ###"""

data = [100,200,400,600,800,1000,1500.,2000,2500] 
fig, ax = plt.subplots()
sns.distplot(unlabeled_comments['char_length'], ax=ax)
plt.xlim(0, 2500)
plt.show()

"""## correlations  ##"""

corr = train[class_names]
plt.figure(figsize=(12,10))
sns.heatmap(corr.astype(float).corr(),linewidths=0.1,vmax=1.0,square=True,cmap=plt.cm.cividis,
           linecolor='white',annot=True)

"""##### Should draw conclusions from this. #####
  ##### for instance - there is a high corrolition between insulting comments and obsecene comments #####

# Preprocessing #

Make all text lower case and switch common shorttened words with the actual words
"""

def clean_text(text):
    text = text.lower()
    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "cannot ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub('\W', ' ', text)
    text = re.sub('\s+', ' ', text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r"\'scuse", " excuse ", text)
    text = text.strip(' ')
    return text

from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier


total_losses = []

for i in range(10):
  train_loop, test_loop = train_test_split(train)
  train_loop = train_loop.drop('char_length',axis=1)

  train_loop['comment_text'] = train_loop['comment_text'].map(lambda x : clean_text(x))
  test_loop['comment_text'] = test_loop['comment_text'].map(lambda x : clean_text(x))

  vectorizer = CountVectorizer(analyzer = 'word',stop_words='english',max_features=10000)
  train_comments=train_loop.iloc[:,1]
  test_comments = test_loop.iloc[:,1]
  TF_model = vectorizer.fit(train_comments).transform(train_comments)

  # TF - IDF  
  idf = TfidfTransformer()
  idf.fit(TF_model)
  train_tfidf = idf.transform(TF_model)

  #Same process for test
  TF_test = vectorizer.transform(test_comments)
  test_tfidf = idf.transform(TF_test)

  logreg = LogisticRegression(C=15.0, max_iter=100000)

  y_test = test_loop.iloc[:,2:]

  for label in class_names:
      print('... Processing', label)
      y = train_loop[label]
      # train the model using the tf-idf model
      logreg.fit(train_tfidf, y)
      # compute the training accuracy
      train_results = logreg.predict(train_tfidf)
      print('Training accuracy is:', accuracy_score(y, train_results))

  LogReg_pipeline = Pipeline([
                  ('clf', OneVsRestClassifier(LogisticRegression(solver='sag'), n_jobs=-1)),
              ])
  losses = []
  for label in class_names:
      print('... Processing', label)
      y = train_loop[label]
      LogReg_pipeline.fit(train_tfidf, y)
      # compute the training accuracy
      y_prediction = LogReg_pipeline.predict(test_tfidf)
      print('Test accuracy is:', accuracy_score(y_test[label], y_prediction))
      losses.append(accuracy_score(y_test[label], y_prediction))

  total_losses.append(losses)

tot_loss = []
for label_index in range(len(class_names)):
  mean_loss = []
  for i in range(10):
    mean_loss.append(total_losses[i][label_index])
  print('... Processing', class_names[label_index])
  print('Test accuracy is:', np.mean(mean_loss))
  tot_loss.append(mean_loss)
print("Total Test accuracy is:",  np.mean(tot_loss))

"""# TF - create Bag of words #

When dealing with textual data, feature extraction refers to conversion of data to numerical form(features) supported by Machine Learning Algorithms.

One way to do so is using "Bag of Words" , the model involves representation of text (referred as sentence or document) as a multiset of words keeping a record of their frequency. A Term Frequency Matrix is used to keep record of frequency of words in the document(comment).

CountVectorizer-Convert a collection of text documents to a matrix of token counts

fit : to generate learning model parameters from training data

transform : parameters generated from fit method are applied on model to generate transformed data set.

# Inverse Document Frequency #

We chose word frequency here to represent text features. However, Inverse Document Frequency can be applied to Term Frequency Matrix to furthur improve our classifier.

Term Frequency (TF) is a scoring of the frequency of the word in the current document, whereas
Inverse Document Frequency (IDF) is a scoring of how rare the word is across documents.

Why do we need to find rare words ? Terms that appear across many comments are less discriminating. TFIDF assigns weightage to words compared to other words in document.

TF-IDF not only counts the frequency of a term in the given document, but also reflects the importance of each term to the document by penalizing frequently appearing terms(words) in most samples.

# TF-IDF #

Same process for test

## Solving a multi-label classification problem ##

One way to approach a multi-label classification problem is to transform the problem into separate single-class classifier problems.

Binary Relevance: This is probably the simplest which treats each label as a separate single classification problems. The key assumption here though, is that there are no correlation among the various labels.
"""

total_mean = []
toxic_results = [0.944789120762048, 0.9469825155104342, 0.9430970733847214, 0.9476091997242589, 0.9469825155104342, 0.9460424891896974, 0.94356708654509, 0.944789120762048, 0.9475151970921852, 0.9455724760293288]
toxic_mean = np.mean(toxic_results)
total_mean.append(toxic_mean)
print('Mean CV score for class toxic is {}'.format(toxic_mean))

severe_toxic_results = [0.9898790499467318, 0.9896910446825844, 0.9904743999498652, 0.9910384157423074, 0.9891896973115247, 0.989503039418437, 0.99085041047816, 0.9899103841574229, 0.9902550604750266, 0.9894717052077459]
severe_toxic_mean = np.mean(severe_toxic_results)
total_mean.append(severe_toxic_mean)
print('Mean CV score for class severe_toxic  is {}'.format(severe_toxic_mean))

obscene = [0.976154665663972, 0.9775960393557687, 0.9769380209312527, 0.976562010402958, 0.9771573604060914, 0.9770320235633264, 0.9764680077708842, 0.9757786551356772, 0.9763740051388106, 0.9772826972488563]
obscene_mean = np.mean(obscene)
total_mean.append(obscene_mean)
print('Mean CV score for class obscene is {}'.format(obscene_mean))

threat = [0.9969605815629504, 0.9969605815629504, 0.9967099078774205, 0.9969292473522592, 0.9969292473522592, 0.9969710262998475, 0.9972739236698628, 0.9971485868270978, 0.9972112552484803, 0.9966785736667293]
threat_mean = np.mean(threat)
total_mean.append(threat_mean)
print('Mean CV score for class threat is {}'.format(threat_mean))

insult = [0.966065049821395, 0.9661590524534688, 0.9657517077144826, 0.9678824340414866, 0.9661903866641599, 0.9657517077144826, 0.9658457103465564, 0.9649683524472019, 0.9672557498276619, 0.964843015604437]
insult_mean = np.mean(insult)
total_mean.append(insult_mean)
print('Mean CV score for class insult is {}'.format(insult_mean))

identity_hate = [0.9912264210064549, 0.9918844394309708, 0.99085041047816, 0.9916964341668232, 0.9916337657454409, 0.9912577552171461, 0.9899103841574232, 0.9908190762674689, 0.9908190762674689, 0.99085041047816]
identity_hate_mean = np.mean(identity_hate)
total_mean.append(identity_hate_mean)
print('Mean CV score for class identity_hate is {}'.format(identity_hate_mean))

print('Total CV score is {}'.format(np.mean(total_mean)))

max = []

for i in range(10):
  score = toxic_results[i] + severe_toxic_results[i] + obscene[i] + threat[i] + insult[i] + identity_hate[i]
  score = score/6
  max.append(score)

print(np.max(max))