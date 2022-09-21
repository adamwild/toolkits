"""
a = await (await fetch(`http://127.0.0.1:8000/rank`,{
      method: 'POST',
      mode: 'cors',
      cache: 'no-cache',
      headers: {
        // 'Content-Type': 'text/plain'
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        search_result: [{
            modified: 1. ,
            relevance: 1.,
            snippet: "coucou",
            title: "plop",
            url: "h"
        }],
        query: "toto"
      })
    })).json()

"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# add source
class SearchResult(BaseModel):
    modified: int
    relevance: float
    snippet: str
    title: str
    url: str


class RankingInput(BaseModel):
    search_result: list[SearchResult]
    query: str


class RankingOutput(BaseModel):
    items: str


# Web server part
app = FastAPI()

origins = ["http://localhost", "https://app.contentsquare.com/", "http://localhost:3000/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping() -> str:
    return "pong"


@app.post("/rank")
def rank(res: RankingInput) -> RankingOutput:
    # breakpoint()
    # ranking = do_ranking(res.query, res.items, num_docs=3)
    # return RankingOutput(items=ranking)
    print("plop")
    return RankingOutput(items="ranking")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
