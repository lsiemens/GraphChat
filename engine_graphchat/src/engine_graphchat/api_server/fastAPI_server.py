from fastapi import FastAPI


api = FastAPI()

@api.get("/")
async def get():
    return {"message": "Hello World"}
