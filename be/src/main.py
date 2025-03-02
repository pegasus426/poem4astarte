from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modello per il payload JSON
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "name": "Sample Item", "price": 42.0}

@app.post("/items/")
def create_item(item: Item):
    # Logica per salvare o processare l'item
    return item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
