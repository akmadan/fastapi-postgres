from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
from app.database.models import Questions, Choices
from app.database.database import engine, SessionLocal
from sqlalchemy.orm import Session
from app.models.base_models import QuestionBase, ChoiceBase

app = FastAPI()


@app.on_event("startup")
def startup_event():
    # Create database tables
    from app.database import models
    models.Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
def shutdown_event():
    # Close database connection
    engine.dispose()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/questions")
def create_question(question: QuestionBase, db: Session = Depends(get_db)):
    db_question = Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id
        )
        db.add(db_choice)
    db.commit()
