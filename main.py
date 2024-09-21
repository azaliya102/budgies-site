from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from yattag import Doc
from database import get_db, engine
from models import Budgie, Base
from fastapi.responses import JSONResponse

import uvicorn

app = FastAPI()

Base.metadata.create_all(bind=engine)
@app.get("/")
async def root():
    return {"message": "Welcome to the Budgies Gallery API! Use /add_budgie to add a budgie."}


class BudgieInput(BaseModel):
    name: str
    color: str
    weight: int
    path: str


@app.get("/{name}", response_class=HTMLResponse)
async def get_budgie_page(name: str):
    db = next(get_db())
    try:
        budgie = db.query(Budgie).filter(Budgie.name == name).first()
        if not budgie:
            return JSONResponse(content={"error": "Budgie not found"}, status_code=404)

        html_content = generate_budgie_page(budgie)
        return HTMLResponse(content=html_content)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


def generate_budgie_page(budgie):
    doc, tag, text = Doc().tagtext()

    with tag('html'):
        with tag('head'):
            with tag('title'):
                text(f"{budgie.name}'s Page")
            with tag('meta', charset="UTF-8"):
                pass
            with tag('style'):
                text("""
                body { background-color: #f5f5dc; text-align: center; font-family: Arial, sans-serif; }
                h1 { color: #333; }
                div { margin-bottom: 20px; }
                img { width: 300px; height: 350px; border-radius: 10px; }
                """)

        with tag('body'):
            with tag('h1'):
                text(f"{budgie.name}'s Photo Gallery")
            with tag('h2'):
                text(f"Name: {budgie.name}")
            with tag('h2'):
                text(f"Color: {budgie.color}")
            with tag('h2'):
                text(f"Weight: {budgie.weight} grams")
            with tag('div'):
                doc.stag('img', src=budgie.path, alt=budgie.name)

    return doc.getvalue()


@app.get("/{name}", response_class=HTMLResponse)
async def get_budgie_page(name: str):
    db = next(get_db())
    budgie = db.query(Budgie).filter(Budgie.name == name).first()
    if not budgie:
        return {"error": "Budgie not found"}

    html_content = generate_budgie_page(budgie)
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
