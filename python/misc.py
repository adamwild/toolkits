# %%
# path
from pathlib import Path

from IPython.display import display

repo_dir = Path.cwd().parent
print(repo_dir)
# %%
# pandas
import pandas as pd

df = pd.DataFrame([{"x": 1, "y": 1}, {"x": 2, "y": 0}, {"x": 3, "y": 2}])
df.to_csv("nodes.csv", index=False)

df.info()
df.dropna(inplace=True)
df.count()

# replace empty values
df.fillna("")

# number of item in a groupby
df.groupby("x").size()

import matplotlib.pyplot as plt
import numpy as np

# %%
# seaborn
import seaborn as sns

sns.histplot(df, x="x", bins=3, hue="y", multiple="stack")  # , log_scale=(False, True))

sns.scatterplot(data=df, x="x", y="y", hue="y")

sns.histplot(df, x="x", log_scale=(False, False), bins=np.arange(40))
plt.xticks(np.arange(40))
plt.show()
# %%
# matplotlib
def display_images(pageviews: list[str], folder_path: str) -> None:
    fig = plt.figure(figsize=(100 * 20 / len(pageviews), 250))
    columns = 4
    rows = np.ceil(len(pageviews))

    for i, pageview in enumerate(pageviews):
        img = plt.imread(os.path.join(folder_path, pageview, "00_web_site.png"))
        fig.add_subplot(rows, columns, i + 1)
        plt.imshow(img)
    plt.show()


# %%
# scikit learn
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix, precision_score

classification_report(pred, y_test, target_names=class_labels)

import datetime

from joblib import dump

date = str(datetime.datetime.now()).replace(" ", "_")
dump(best_model, f"model_{best_macro_f1_score:.03}_{date}.joblib")
# %%
# NLP
from sentence_transformers import SentenceTransformer, util

cache_path = "/home/seb/.cache/torch/sentence_transformers"
model_path = os.path.join(cache_path, "sentence-transformers_multi-qa-mpnet-base-dot-v1")
bert_model = SentenceTransformer(model_path)

sentence_embs = bert_model.encode(sentences)
query_emb = bert_model.encode(query)
util.dot_score(query_emb, sentence_embs).tolist()[0]
import queue

# %%
# threading
from typing import Any


class InterruptExcept(Exception):
    pass


class InterruptableQueue:
    def __init__(self, maxsize: int = 15) -> None:
        self.queue = queue.Queue(maxsize=maxsize)
        self.stopped = False

    def put(self, message: Any) -> None:
        """put a message in the queue.
        If the queue is full then wait forever, except if a stopped signal is sent
        In this case, break the loop and raise a InterruptExcept
        """
        while True:
            if self.stopped:
                raise InterruptExcept
            try:
                self.queue.put(message, timeout=0.5)
                return
            except queue.Full:
                continue

    def get(self) -> Any:
        while True:
            if self.stopped:
                raise InterruptExcept
            try:
                return self.queue.get(timeout=0.5)
            except queue.Empty:
                continue

    def stop(self) -> None:
        self.stopped = True


data_queue = InterruptableQueue(maxsize=15)

import threading
import time

q_in = InterruptableQueue(3)
q_out = InterruptableQueue(3)


class DataProces(threading.Thread):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def run(self) -> None:
        while True:
            data = q_in.get()
            print("process", self.name, ":", data)
            time.sleep(1)


dp = DataProces("dp")
dp2 = DataProces("dp2")
dp.start()
dp2.start()

q_in.put(1)
q_in.put(2)
q_in.put(3)
q_in.put(4)
q_in.put(5)

time.sleep(3)
q_in.stop()
q_out.stop()

# %%
# algo
def smart_insert(list, item):
    """list is a list of element with (score, something) that need to be order by score"""
    min = 0
    max = len(list)
    while max != min:
        m = (min + max) // 2
        if list[m][0] > item[0]:
            max = m
        else:
            min = m + 1
    return list[:min] + [item] + list[min:]


assert smart_insert([], (6,)) == [(6,)]
assert smart_insert([(1,)], (6,)) == [(1,), (6,)]
assert smart_insert([(7,)], (6,)) == [(6,), (7,)]
assert smart_insert([(1,), (5,), (7,)], (6,)) == [(1,), (5,), (6,), (7,)]
assert smart_insert([(1,), (5,), (7,)], (8,)) == [(1,), (5,), (7,), (8,)]
assert smart_insert([(1,), (5,), (7,)], (0,)) == [(0,), (1,), (5,), (7,)]
# %%
