# %%
import requests
import os
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


import datetime as dt

token = os.environ["GITHUB_TOKEN"]
url = "https://api.github.com/repos/{owner}/{repo}/stargazers?per_page=100&page={page}"


def get_stars_data(owner: str, repo: str):
    p=1
    data = []
    while True:
        print(p)
        d = requests.get(url.format(owner=owner, repo=repo, page=p), headers={
            "Accept": "application/vnd.github.star+json",
            "Authorization": f"Bearer {token}"
        })

        if d.status_code != 200:
            raise ValueError(f"can't get data: {d.text}")
        j = d.json()
        data.extend(dt.datetime.strptime(user["starred_at"].split("T")[0], "%Y-%m-%d").date()
            for user in j)
        if len(j) == 100:
            p += 1
        else:
            break
    return data
# %%
data = get_stars_data("mlrun", "mlrun")
data2 = get_stars_data("SeldonIO", "seldon-core") 
data3 = get_stars_data("kserve", "kserve") 
data4 = get_stars_data("bentoml", "BentoML") 
data5 = get_stars_data("mlflow", "mlflow") 

plt.plot(data, range(len(data)), label='mlrun')
plt.plot(data2, range(len(data2)), label='seldon-core')
plt.plot(data3, range(len(data3)), label='kserve')
plt.plot(data4, range(len(data4)), label='BentoML')
# plt.plot(data5, range(len(data5)), label='mlflow')

plt.legend(loc='upper left')  

# %% 
data = get_stars_data("triton-inference-server", "server")
data2 = get_stars_data("tensorflow", "serving")
data3 = get_stars_data("pytorch", "serve")
data4 = get_stars_data("SeldonIO", "MLServer")
# %%
plt.plot(data, range(len(data)), label='triton')
plt.plot(data2, range(len(data2)), label='tensorflow serving')
plt.plot(data3, range(len(data3)), label='pytorch serve')
plt.plot(data4, range(len(data4)), label='MLServer')

plt.legend(loc='upper left')  
# %%
data = get_stars_data("foambubble", "foam")

# %%

# %%

data2 = get_stars_data("logseq", "logseq")

# %%

plt.plot(data, range(len(data)), label='foam')
plt.plot(data, range(len(data)), label='logseq')
# %%
data3 = get_stars_data("zim-desktop-wiki", "zim-desktop-wiki")

# %%

plt.plot(data, range(len(data)), label='foam')
plt.plot(data2, range(len(data2)), label='logseq')
plt.plot(data3, range(len(data3)), label='zim')
plt.legend(loc='upper left')  

# %%
