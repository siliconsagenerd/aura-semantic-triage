from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db, MessageRecord

load_dotenv()

app = FastAPI(title="Aura Semantic Triage API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")
else:
    genai.configure(api_key=api_key)


class MessageRequest(BaseModel):
    id: int = Field(..., gt=0)
    text: str = Field(..., min_length=5, max_length=2000)
    platform: str = Field(..., min_length=1, max_length=50)
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Message text cannot be empty")
        return v.strip()
    
    @validator('platform')
    def platform_valid(cls, v):
        valid_platforms = ['Instagram', 'Facebook', 'Twitter', 'LinkedIn', 'DM', 'Manual']
        if v not in valid_platforms:
            raise ValueError(f"Invalid platform")
        return v

class BatchTriageRequest(BaseModel):
    messages: List[MessageRequest] = Field(..., min_items=1, max_items=50)

class FeedbackRequest(BaseModel):
    message_id: int = Field(..., gt=0)
    feedback: str = Field(..., min_length=1, max_length=500)
    approved: bool


def get_triage_prompt(text: str) -> str:
    return f"""Analyze this message and categorize it.

Message: "{text}"

Return JSON with: "urgency" (High/Medium/Low), "category" (Grief Support/Crisis Intervention/Service Inquiry/Pricing/Sales/Technical Support/Feedback/General Comment/Memorial Request), "sentiment" (one word), "emotion_score" (0-100), "suggested_reply" (2-3 sentences in German).

No markdown, raw JSON only."""

def analyze_with_gemini(text: str) -> dict:
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(get_triage_prompt(text))
        response_text = response.text.replace('```json', '').replace('```', '').strip()
        analysis = json.loads(response_text)
        
        return {
            "urgency": analysis.get("urgency", "Medium"),
            "category": analysis.get("category", "Unknown"),
            "sentiment": analysis.get("sentiment", "Neutral"),
            "emotion_score": analysis.get("emotion_score", 50),
            "suggested_reply": analysis.get("suggested_reply", "Vielen Dank für Ihre Nachricht."),
            "ai_powered": True
        }
    except Exception as e:
        print(f"Gemini Error: {e}")
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["hilf", "verzweif", "selbstmord", "sterben", "kill", "töt"]):
            return {
                "urgency": "High",
                "category": "Crisis Intervention",
                "sentiment": "Desperate",
                "emotion_score": 85,
                "suggested_reply": "Bitte kontaktieren Sie sofort den Notfalldienst unter 112 oder die Telefonseelsorge: 0800 111 0 111",
                "ai_powered": False
            }
        elif any(word in text_lower for word in ["trauer", "traurig", "vermiss", "schmerz", "tot", "gestorben"]):
            return {
                "urgency": "High",
                "category": "Grief Support",
                "sentiment": "Sorrowful",
                "emotion_score": 75,
                "suggested_reply": "Es tut uns leid für Ihren Verlust. Wir unterstützen Sie gerne.",
                "ai_powered": False
            }
        elif any(word in text_lower for word in ["preis", "kosten", "paket", "angebot"]):
            return {
                "urgency": "Medium",
                "category": "Pricing/Sales",
                "sentiment": "Neutral",
                "emotion_score": 30,
                "suggested_reply": "Gerne stellen wir Ihnen unsere Pakete vor.",
                "ai_powered": False
            }
        elif any(word in text_lower for word in ["fehler", "problem", "funktioniert nicht"]):
            return {
                "urgency": "Medium",
                "category": "Technical Support",
                "sentiment": "Frustrated",
                "emotion_score": 40,
                "suggested_reply": "Entschuldigung. Unser Support kümmert sich darum.",
                "ai_powered": False
            }
        elif any(word in text_lower for word in ["danke", "toll", "super", "empfehle"]):
            return {
                "urgency": "Low",
                "category": "Feedback",
                "sentiment": "Grateful",
                "emotion_score": 10,
                "suggested_reply": "Vielen Dank für Ihre Worte!",
                "ai_powered": False
            }
        else:
            return {
                "urgency": "Low",
                "category": "General Comment",
                "sentiment": "Neutral",
                "emotion_score": 25,
                "suggested_reply": "Vielen Dank für Ihre Nachricht.",
                "ai_powered": False
            }


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.query(MessageRecord).first()
        db_status = "connected"
    except:
        db_status = "error"
    
    return {
        "status": "healthy",
        "api_version": "1.0",
        "gemini_configured": bool(api_key),
        "database": db_status
    }

@app.post("/api/triage")
async def analyze_message(request: MessageRequest, db: Session = Depends(get_db)):
    try:
        if not api_key:
            raise HTTPException(status_code=500, detail="API Key not configured")
        
        analysis = analyze_with_gemini(request.text)
        
        record = MessageRecord(
            original_id=request.id,
            text=request.text,
            platform=request.platform,
            urgency=analysis["urgency"],
            category=analysis["category"],
            sentiment=analysis["sentiment"],
            emotion_score=analysis["emotion_score"],
            suggested_reply=analysis["suggested_reply"],
            ai_powered=analysis["ai_powered"]
        )
        db.add(record)
        db.commit()
        
        return {
            "status": "success",
            "original_message_id": request.id,
            "analysis": {
                "urgency": analysis["urgency"],
                "category": analysis["category"],
                "sentiment": analysis["sentiment"],
                "emotion_score": analysis["emotion_score"],
                "ai_powered": analysis["ai_powered"]
            },
            "suggested_reply": analysis["suggested_reply"]
        }
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/triage/batch")
async def batch_triage(request: BatchTriageRequest, db: Session = Depends(get_db)):
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key not configured")
    
    results = []
    errors = []
    
    for msg in request.messages:
        try:
            analysis = analyze_with_gemini(msg.text)
            
            record = MessageRecord(
                original_id=msg.id,
                text=msg.text,
                platform=msg.platform,
                urgency=analysis["urgency"],
                category=analysis["category"],
                sentiment=analysis["sentiment"],
                emotion_score=analysis["emotion_score"],
                suggested_reply=analysis["suggested_reply"],
                ai_powered=analysis["ai_powered"]
            )
            db.add(record)
            
            results.append({
                "message_id": msg.id,
                "status": "success",
                "analysis": {
                    "urgency": analysis["urgency"],
                    "category": analysis["category"],
                    "sentiment": analysis["sentiment"],
                    "emotion_score": analysis["emotion_score"]
                },
                "suggested_reply": analysis["suggested_reply"]
            })
        except Exception as e:
            errors.append({"message_id": msg.id, "status": "error", "error": str(e)})
    
    db.commit()
    
    return {
        "status": "partial_success" if errors else "success",
        "count": len(results),
        "errors_count": len(errors),
        "results": results,
        "errors": errors if errors else None
    }

@app.get("/api/history")
async def get_history(limit: int = 50, urgency: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(MessageRecord)
    
    if urgency:
        if urgency not in ['High', 'Medium', 'Low']:
            raise HTTPException(status_code=422, detail="Invalid urgency")
        query = query.filter(MessageRecord.urgency == urgency)
    
    messages = query.order_by(MessageRecord.timestamp.desc()).limit(limit).all()
    
    return {
        "status": "success",
        "total": len(messages),
        "messages": [{
            "id": m.id,
            "original_id": m.original_id,
            "text": m.text,
            "platform": m.platform,
            "timestamp": m.timestamp.isoformat(),
            "urgency": m.urgency,
            "category": m.category,
            "sentiment": m.sentiment,
            "emotion_score": m.emotion_score,
            "suggested_reply": m.suggested_reply,
            "ai_powered": m.ai_powered
        } for m in messages]
    }

@app.get("/api/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    messages = db.query(MessageRecord).all()
    
    if not messages:
        return {
            "status": "success",
            "total_messages": 0,
            "by_urgency": {},
            "by_category": {},
            "average_emotion_score": 0,
            "platforms": {}
        }
    
    by_urgency = {}
    by_category = {}
    platforms = {}
    
    for msg in messages:
        by_urgency[msg.urgency] = by_urgency.get(msg.urgency, 0) + 1
        by_category[msg.category] = by_category.get(msg.category, 0) + 1
        platforms[msg.platform] = platforms.get(msg.platform, 0) + 1
    
    avg_emotion = sum(m.emotion_score for m in messages) / len(messages)
    
    return {
        "status": "success",
        "total_messages": len(messages),
        "by_urgency": by_urgency,
        "by_category": by_category,
        "average_emotion_score": round(avg_emotion, 1),
        "platforms": platforms,
        "high_priority_count": by_urgency.get("High", 0),
        "ai_powered_responses": sum(1 for m in messages if m.ai_powered)
    }

@app.get("/api/messages/high-priority")
async def get_high_priority(db: Session = Depends(get_db)):
    messages = db.query(MessageRecord).filter(MessageRecord.urgency == "High").order_by(MessageRecord.timestamp.desc()).all()
    
    return {
        "status": "success",
        "count": len(messages),
        "messages": [{
            "id": m.id,
            "text": m.text,
            "platform": m.platform,
            "timestamp": m.timestamp.isoformat(),
            "urgency": m.urgency,
            "category": m.category,
            "sentiment": m.sentiment,
            "emotion_score": m.emotion_score,
            "suggested_reply": m.suggested_reply,
            "ai_powered": m.ai_powered
        } for m in messages]
    }

@app.get("/api/messages/by-emotion")
async def get_by_emotion_threshold(threshold: int = 70, db: Session = Depends(get_db)):
    if not 0 <= threshold <= 100:
        raise HTTPException(status_code=422, detail="Threshold must be 0-100")
    
    messages = db.query(MessageRecord).filter(MessageRecord.emotion_score >= threshold).order_by(MessageRecord.timestamp.desc()).all()
    
    return {
        "status": "success",
        "threshold": threshold,
        "count": len(messages),
        "messages": [{
            "id": m.id,
            "text": m.text,
            "platform": m.platform,
            "emotion_score": m.emotion_score,
            "category": m.category,
            "suggested_reply": m.suggested_reply
        } for m in messages]
    }

@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    message = db.query(MessageRecord).filter(MessageRecord.original_id == request.message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.feedback = request.feedback
    message.approved = request.approved
    message.feedback_timestamp = datetime.utcnow()
    db.commit()
    
    return {"status": "success", "message": "Feedback recorded"}

@app.post("/api/clear-history")
async def clear_history(db: Session = Depends(get_db)):
    count = db.query(MessageRecord).count()
    db.query(MessageRecord).delete()
    db.commit()
    
    return {"status": "success", "message": f"Cleared {count} messages"}

@app.get("/")
async def root():
    return {
        "name": "Aura Semantic Triage API",
        "version": "1.0",
        "docs": "/docs"
    }
