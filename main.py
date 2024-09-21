from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from starlette.responses import HTMLResponse
from yattag import Doc

DATABASE_URL = "postgresql://azaliya02:test@localhost:5432/testtest"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Budgie(Base):
    __tablename__ = "budgies"

    budgie_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    color = Column(String)
    weight = Column(Integer)
    path = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class BudgieInput(BaseModel):
    name: str
    color: str
    weight: int
    path: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/add_budgie")
async def add_budgie(budgie: BudgieInput, db: Session = Depends(get_db)):
    existing_budgie = db.query(Budgie).filter(Budgie.name == budgie.name).first()
    if existing_budgie:
        raise HTTPException(status_code=400, detail="Budgie already exists.")

    new_budgie = Budgie(name=budgie.name, color=budgie.color, weight=budgie.weight, path=budgie.path)
    db.add(new_budgie)
    db.commit()
    db.refresh(new_budgie)
    return {"message": f"Budgie {budgie.name} added successfully!"}

@app.get("/", response_class=HTMLResponse)
async def root():
    db = next(get_db())
    budgies = db.query(Budgie).all()
    return generate_budgies_list_page(budgies)

def generate_budgies_list_page(budgies):
    doc, tag, text = Doc().tagtext()

    with tag('html'):
        with tag('head'):
            with tag('title'):
                text("Budgies Gallery")
            with tag('meta', charset="UTF-8"):
                pass
            with tag('style'):
                text("""
                body { font-family: Arial, sans-serif; text-align: center; }
                h1 { color: #333; }
                a { display: block; font-size: 24px; margin: 10px 0; }
                """)

        with tag('body'):
            with tag('h1'):
                text("Budgies List")
            for budgie in budgies:
                with tag('a', href=f"/{budgie.name}"):
                    text(budgie.name)

    return doc.getvalue()


@app.get("/{name}")
async def get_budgie_page(name: str, db: Session = Depends(get_db)):
    budgie = db.query(Budgie).filter(Budgie.name == name).first()
    if not budgie:
        raise HTTPException(status_code=404, detail="Budgie not found")

    html_content = generate_budgie_page(budgie)
    return HTMLResponse(content=html_content)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
