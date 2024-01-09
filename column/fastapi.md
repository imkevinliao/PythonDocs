# 快速上手
```
from typing import Union

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1",port=8000)
```
# 提高计划
```
# 为了防止出现安全问题，关闭所有的的接口文档（docs 和 redoc 都要关闭）
# openapi_url=None openapi.json也可以获取接口信息
app = FastAPI(docs_url=None, redoc_url=None)
```
