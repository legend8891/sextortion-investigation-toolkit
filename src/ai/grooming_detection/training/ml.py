import html
import re
import ssl
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import nltk
import pandas as pd
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.utils import resample

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download("wordnet")
nltk.download("omw-1.4")
nltk.download("stopwords")
wnl = WordNetLemmatizer()


def plot_confusion_matrix(cm) -> None:
    """
    Plots confusion matrix using pyplot
    :param cm: confusion matrix to plot
    :return:
    """
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot()
    plt.show()


def clean_text(s):
    """
    Performs small amount of data cleaning while preserving potentially important features
    :param s:
    :return:
    """
    # Convert HTML characters to ASCII
    s = html.unescape(s)
    # Lemmatise
    s = wnl.lemmatize(s)
    # Remove any non-ASCII characters
    s = ''.join([i if ord(i) < 128 else ' ' for i in s])
    # Remove trailing whitespace
    s = re.sub(r'\s+', ' ', s).strip()

    return s


# Get predator authors from the txt file that comes with the training corpus
predator_authors = open('datasets/pan12-sexual-predator-identification-training-corpus-predators-2012-05-01.txt',
                        'r').read()

# Get the training corpus xml and parse it
tree = ET.parse('datasets/pan12-sexual-predator-identification-training-corpus-2012-05-01.xml')
root = tree.getroot()

# Drop all but the text and label for each row
text_messages = []
labels = []
text_message = []
label = []
for messages in root.iter('message'):
    for ele in messages.findall('*'):
        if ele.tag == 'author':
            label.append(int(ele.text in predator_authors))
        elif ele.tag == 'text':
            text_message.append(ele.text)
for i in range(len(text_message)):
    if text_message[i] != None:
        text_messages.append(text_message[i])
        labels.append(label[i])

# Combine text and label columns
df = pd.DataFrame({'text': text_messages, "labels": labels})
print(df.info())

# Drop NaNs
df.dropna(subset=['text'], inplace=True)
df.reset_index(drop=True, inplace=True)
print(df.info())

# Perform limited text cleaning
df['text'] = df['text'].apply(clean_text)
df.info()

# Get only the rows where the text is more than 1 word
df_sub = df[df['text'].apply(lambda t: len(t.split()) > 1)]
df_sub.index = range(0, df_sub.shape[0])
print(df_sub.shape)

# Separate sexual predator and non-predator rows
predator_rows = df_sub[df_sub['labels'] == 1]
non_predator_rows = df_sub[df_sub['labels'] == 0]

# Downsample non-predator (majority) class by 1/2
non_predator_rows_downsampled = resample(non_predator_rows,
                                         replace=False,
                                         n_samples=315769)

# Upsample the predator (minority) class by x2
predator_rows_upsampled = resample(predator_rows,
                                   replace=True,
                                   n_samples=61032)

# Put downsampled and upsampled data back together
df_sub = pd.concat([non_predator_rows_downsampled, predator_rows_upsampled])
print(predator_rows.shape)
print(non_predator_rows.shape)
print(non_predator_rows_downsampled.shape)

# Test train split using 67% for training and 33% for testing
X_train_cleaned, X_test_cleaned, y_train, y_test = train_test_split(df_sub['text'], df_sub['labels'], test_size=0.33,
                                                                    random_state=42)

# TF-IDF instance
tf_idf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), max_features=100000)

# Apply TF-IDF to training and testing splits
X_train_tfidf = tf_idf.fit_transform(X_train_cleaned)

# # Save fitted TFIDF
# with open('models/tf_idf_vectoriser.pk', 'wb') as fin:
#     pickle.dump(tf_idf, fin)

X_val_tfidf = tf_idf.transform(X_test_cleaned)

# Create LR model using the best parameters from hyperparameter tuning
log_reg = LogisticRegression(penalty='l2', C=10, multi_class='multinomial', solver='lbfgs', random_state=100,
                             tol=0.0001,
                             max_iter=1000)

# Fit model to training data
log_reg.fit(X_train_tfidf, y_train)

# # Save the trained classifier to a pickle file
# with open('models/lr_model.pk', 'wb') as fin:
#     pickle.dump(log_reg, fin)


# Make predictions on test split
y_pred = log_reg.predict(X_val_tfidf)

# Get evaluation metrics
report = classification_report(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)
print(report)
print(conf_matrix)
plot_confusion_matrix(conf_matrix)


# -- Below is the grid search used for hyperparameter tuning --

# # Define the parameters for grid search
# param_grid = {'C': [100, 10, 1.0, 0.1, 0.01],
#               'tol': [1e-4, 1e-3, 1e-2, 1e-1]}
#
# # Create a GridSearchCV object
# grid_search = GridSearchCV(LogisticRegression(penalty='l2', multi_class='multinomial', solver='lbfgs', random_state=42, max_iter=1000),
#                            param_grid, cv=10, verbose=True)
#
# # Fit the GridSearchCV object to the training data
# grid_search.fit(X_train_tfidf, y_train)
#
# # Print the best parameters found
# print("Best parameters found:", grid_search.best_params_)
#
# # Get the best model
# best_model = grid_search.best_estimator_
#
# # Predict on the validation set using the best model
# y_pred = best_model.predict(X_val_tfidf)
#
# # Evaluate the model
# report = classification_report(y_test, y_pred)
# conf_matrix = confusion_matrix(y_test, y_pred)
#
# print(report)
# print(conf_matrix)

# loaded_tfidf = pickle.load(open("models/tf_idf.pickle", "rb"))
# loaded_lr = pickle.load(open("models/lr_classifier.pickle", "rb"))
#
# X_val_loaded = loaded_tfidf.transform(X_test_cleaned)
# y_pred_loaded = loaded_lr.predict(X_val_loaded)
#
# print(classification_report(y_test, y_pred_loaded))
