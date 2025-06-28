"""
feedback/analyze.py
Enterprise-grade feedback analyzer for Watchtower.
Uses NLP/AI (if available) to classify feedback sentiment, topic, and route for protocol improvement.
"""

from typing import Dict, Any
from database.models.feedback import Feedback
from sqlalchemy.orm import Session
from datetime import datetime

try:
    from textblob import TextBlob  # Or any NLP sentiment analysis library
except ImportError:
    TextBlob = None

class FeedbackAnalyzer:
    def __init__(self, session: Session):
        self.session = session

    def analyze_feedback(self, feedback_id: int) -> Dict[str, Any]:
        feedback = self.session.query(Feedback).filter_by(id=feedback_id).first()
        if not feedback:
            return {"error": f"Feedback ID {feedback_id} not found"}
        message = feedback.message or ""
        sentiment = "neutral"
        polarity = 0.0
        subjectivity = 0.0
        if TextBlob and message:
            tb = TextBlob(message)
            polarity = tb.sentiment.polarity
            subjectivity = tb.sentiment.subjectivity
            if polarity > 0.2:
                sentiment = "positive"
            elif polarity < -0.2:
                sentiment = "negative"
        # Update feedback analysis in DB
        feedback.sentiment = sentiment
        feedback.analysis = {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        self.session.commit()
        return {
            "feedback_id": feedback_id,
            "sentiment": sentiment,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "message": message
        }

if __name__ == "__main__":
    print("FeedbackAnalyzer requires an active SQLAlchemy session.")
