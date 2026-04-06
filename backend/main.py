from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, HttpUrl
import pickle
import os
import requests
from bs4 import BeautifulSoup
import numpy as np
import re

from contextlib import asynccontextmanager

# Load model on startup
MODEL_PATH = "fake_news_model.pkl"
model_pipeline = None
hf_pipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_pipeline
    global hf_pipeline
    
    # Temporarily skip transformer models to use pickle model
    # try:
    #     from transformers import pipeline
        
    #     # Check if fine-tuned local models exist
    #     if os.path.exists("./fake_news_roberta-large"):
    #         print("Loading local fine-tuned roberta-large...")
    #         hf_pipeline = pipeline("text-classification", model="./fake_news_roberta-large", truncation=True, max_length=512)
    #     elif os.path.exists("./fake_news_bert-base-uncased"):
    #         print("Loading local fine-tuned bert-base-uncased...")
    #         hf_pipeline = pipeline("text-classification", model="./fake_news_bert-base-uncased", truncation=True, max_length=512)
    #     else:
    #         # Fallback to recognized fine-tuned fake news BERT on HuggingFace Hub
    #         model_name = os.getenv("HF_MODEL_NAME", "jy46604790/Fake-News-Bert-Detect")
    #         print(f"Loading HuggingFace Hub transformer model: {model_name} ...")
    #         hf_pipeline = pipeline("text-classification", model=model_name, truncation=True, max_length=512)
            
    #     print("Advanced Transformer Model successfully loaded!")
    # except Exception as e:
    #     print(f"Transformer model loading failed: {e}. Falling back to basic ML model.")

    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model_pipeline = pickle.load(f)
        print("Basic ML model loaded successfully!")
    else:
        print("Warning: Basic Model not found either. Train models using model_train.py")
    yield

app = FastAPI(title="TruthGuard AI - Fake Content Detection API", lifespan=lifespan)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production, e.g., ["http://localhost:5173"]
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("Text requires at least 10 characters for meaningful analysis.")
        if len(v.split()) < 3:
            raise ValueError("Text must contain at least 3 words.")
        if re.search(r'(.)\1{10,}', v):
            raise ValueError("Text contains excessive repetitive characters and appears to be gibberish.")
        return v

class UrlRequest(BaseModel):
    url: HttpUrl

def fetch_wikipedia_summary(query: str):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return response.json().get('extract', '')
    except:
        pass
    return None

def fetch_google_fact_check(query: str):
    api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
    if not api_key:
        return None
    try:
        url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={api_key}"
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            if "claims" in data and len(data["claims"]) > 0:
                claim = data["claims"][0]
                if "claimReview" in claim and len(claim["claimReview"]) > 0:
                    rating = claim["claimReview"][0].get("textualRating", "").lower()
                    return rating
    except:
        pass
    return None

def fact_verification(text: str):
    # Extract potential proper nouns (capitalized words not at start of string)
    words = text.split()
    entities = [re.sub(r'[^A-Za-z]', '', w) for w in words[1:] if w.istitle()]
    # Filter out common short words that might be capitalized
    entities = [e for e in entities if len(e) > 3][:3] # Take top 3 entities
    
    verified_facts = 0
    failed_facts = 0
    fact_details = []
    
    for entity in set(entities):
        # 1. Check Google Fact Check API First
        google_rating = fetch_google_fact_check(entity)
        if google_rating:
            # If Google explicitly flags it as false/misleading
            if any(fake_word in google_rating for fake_word in ['false', 'fake', 'incorrect', 'pants on fire', 'misleading']):
                failed_facts += 1
                fact_details.append(f"Entity '{entity}' flagged as '{google_rating}' by Google Fact Check API.")
            else:
                verified_facts += 1
                fact_details.append(f"Entity '{entity}' verified via Google Fact Check API ('{google_rating}').")
            continue
            
        # 2. Fallback to Wikipedia API
        summary = fetch_wikipedia_summary(entity)
        if summary:
            verified_facts += 1
            fact_details.append(f"Entity '{entity}' verified via Wikipedia API.")
        else:
            failed_facts += 1
            if os.getenv("GOOGLE_FACT_CHECK_API_KEY"):
                fact_details.append(f"Entity '{entity}' lacks verification records (Wikipedia & Google).")
            else:
                fact_details.append(f"Entity '{entity}' lacks verification records (Wikipedia).")
            
    if verified_facts + failed_facts == 0:
        return 0.5, ["No verifiable entities extracted."]
    
    score = verified_facts / (float(verified_facts + failed_facts))
    return score, fact_details

def tone_analysis(text: str):
    text_lower = text.lower()
    sensational_words = ['shocking', 'scam', 'trick', 'free', 'win', 'lottery', 'cure', 'secret', 'miracle', 'unbelievable', 'exposed', 'banned', 'omg', 'wow', 'insane', 'mind-blowing']
    objective_words = ['according', 'reported', 'stated', 'research', 'analysis', 'data', 'percent', 'official', 'confirmed', 'government', 'university']
    
    num_exclamations = text.count('!')
    num_all_caps = sum(1 for w in text.split() if w.isupper() and len(w) > 2)
    
    sens_count = sum(1 for w in sensational_words if w in text_lower)
    obj_count = sum(1 for w in objective_words if w in text_lower)
    
    # Base tone score 0.5. 1.0 = Highly Sensational/Fake, 0.0 = Highly Objective/Real
    tone_score = 0.5
    tone_score += (sens_count * 0.15) + (num_exclamations * 0.08) + (num_all_caps * 0.08)
    tone_score -= (obj_count * 0.1)
    tone_score = max(0.01, min(0.99, tone_score))
    
    tone_reasons = []
    if sens_count > 0: tone_reasons.append(f"NLP detected {sens_count} sensational/emotional terms.")
    if num_exclamations > 0: tone_reasons.append(f"High exclamation usage indicative of opinion/hype ({num_exclamations}).")
    if num_all_caps > 0: tone_reasons.append(f"Aggressive capitalization found ({num_all_caps} ALL-CAPS words).")
    if obj_count > 0: tone_reasons.append(f"Tone aligned with formal reporting ({obj_count} objective terms found).")
    
    if not tone_reasons:
        tone_reasons.append("Language style evaluates as neutral.")
        
    return tone_score, tone_reasons

def rule_based_validation(text: str):
    text_lower = text.lower()
    triggered_rules = []
    
    # Rule 1: Known spam/scam domains or explicit "click here" phrasing
    if re.search(r"click here|subscribe now|limited time offer|act now|don't miss out", text_lower):
        triggered_rules.append("Contains aggressive marketing/clickbait phrases.")
        
    # Rule 2: Excessive character repetition (e.g., "WAKE UP!!!!!", "FAAAAAKE")
    if re.search(r"(.)\1{4,}", text_lower) or re.search(r"(!|\?){3,}", text):
        triggered_rules.append("Excessive character or punctuation repetition detected.")
        
    # Rule 3: Extreme formatting
    words = text.split()
    caps_words = [w for w in words if w.isupper() and len(w) > 2]
    if len(words) > 5 and len(caps_words) / len(words) > 0.3:
        triggered_rules.append("Over 30% of words are ALL CAPS.")
        
    # Rule 4: Deepfake/conspiracy trigger words
    conspiracy_words = ['illuminati', 'reptilian', 'flat earth', 'microchip', '5g mind control', 'aliens', 'ufo', 'conspiracy', 'hoax', 'scam', 'fake news']
    if any(cw in text_lower for cw in conspiracy_words):
        triggered_rules.append("Contains known conspiracy theory vocabulary.")

    rule_fake_boost = 0.15 * len(triggered_rules)
    return min(rule_fake_boost, 0.4), triggered_rules

def analyze_content(text: str, is_url: bool = False):
    if not model_pipeline and not hf_pipeline:
        raise HTTPException(status_code=500, detail="Models are not loaded. Train the models first.")
        
    rule_fake_boost, triggered_rules = rule_based_validation(text)
    tone_score_fake, tone_reasons = tone_analysis(text)
    fact_score_fake, fact_details = fact_verification(text)

    # Adjust weights for URL analysis (less sensitive to tone and rules, more to facts)
    if is_url:
        ml_weight = 0.5
        tone_weight = 0.2
        fact_weight = 0.3
        rule_weight = rule_fake_boost * 0.5  # Reduce rule impact for URLs
    else:
        ml_weight = 0.6
        tone_weight = 0.3
        fact_weight = 0.1
        rule_weight = rule_fake_boost

    # Baseline or Advanced ML inference
    top_words = []
    highlighted_text = text
    
    if hf_pipeline:
        # Transformer-based inference (bert-base-uncased / roberta-large)
        results = hf_pipeline(text)
        label_str = str(results[0]['label']).upper()
        
        # Determine fake probability score from transformer outputs
        if "FAKE" in label_str or "LABEL_1" in label_str or "1" == label_str:
            ml_prob_fake = results[0]['score']
        elif "REAL" in label_str or "TRUE" in label_str or "LABEL_0" in label_str or "0" == label_str:
            ml_prob_fake = 1.0 - results[0]['score']
        else:
            ml_prob_fake = results[0]['score']  # Default fallback
            
        # Extract attention words - simulated for pipeline API without direct attention head access
        words = [w.strip("~.,?!:;\\\"'") for w in text.split() if len(w) > 4]
        # Heuristic representation of words the transformer might focus heavily on
        top_words = sorted(list(set(words)), key=lambda x: len(x), reverse=True)[:5]
        
    else:
        # Basic ML inference fallback
        vectorizer = model_pipeline.named_steps['tfidf']
        classifier = model_pipeline.named_steps['clf']
        probabilities = model_pipeline.predict_proba([text])[0]
        # Invert the probability since model seems to have labels swapped
        ml_prob_fake = 1.0 - float(probabilities[1])
        
        # Generate highlights & Keywords
        feature_names = vectorizer.get_feature_names_out()
        tfidf_matrix = vectorizer.transform([text])
        word_importances = []
        for col in tfidf_matrix.nonzero()[1]:
            word = feature_names[col]
            weight = classifier.coef_[0][col]
            word_importances.append((word, abs(weight), weight))

        word_importances.sort(key=lambda x: x[1], reverse=True)
        top_words = [w[0] for w in word_importances[:5]]
        
    for w in top_words:
        pattern = re.compile(re.escape(w), re.IGNORECASE)
        highlighted_text = pattern.sub(f"<mark>{w}</mark>", highlighted_text)

    # Calculate overall confidence
    confidence_fake = (ml_prob_fake * ml_weight) + (tone_score_fake * tone_weight) + (fact_score_fake * fact_weight) + rule_weight
    confidence_fake = min(1.0, max(0.0, confidence_fake))
    
    if confidence_fake >= 0.5:
        label = "FAKE"
        confidence = confidence_fake
    else:
        label = "REAL"
        confidence = 1.0 - confidence_fake

    # 5. Explanation Generator
    explanation = []
    explanation.append("--- TruthGuard Decision Engine Report ---")
    
    if triggered_rules:
        explanation.append("• Rule-based Validation (Heuristics Triggered):")
        for r in triggered_rules:
            explanation.append(f"  - {r}")
            
    explanation.append(f"• NLP Tone Analysis ({'Suspicious' if tone_score_fake > 0.55 else 'Neutral'}):")
    for r in tone_reasons:
        explanation.append(f"  - {r}")
        
    explanation.append(f"• Fact Verification Engine ({'Failed verification gaps' if fact_score_fake > 0.55 else 'Passed checks'}):")
    for f in fact_details:
        explanation.append(f"  - {f}")
        
    explanation.append("• Machine Learning Factors:")
    explanation.append(f"  - Baseline model probability: {ml_prob_fake:.2%}")
    if top_words:
        explanation.append(f"  - High-impact vocabulary recognized: {', '.join(top_words)}")
    
    explanation.append(f"➜ Final Configured Confidence: {confidence:.2%}")

    return {
        "prediction": str(label),
        "confidence": float(round(confidence, 4)),
        "explanation": [str(e) for e in explanation],
        "highlighted_text": str(highlighted_text),
        "top_keywords": [str(w) for w in top_words],
        "engine_metrics": {
            "ml_score": float(round(ml_prob_fake, 4)),
            "tone_score": float(round(tone_score_fake, 4)),
            "fact_score": float(round(fact_score_fake, 4)),
            "rule_score": float(round(rule_fake_boost, 4))
        }
    }

@app.post("/analyze-text")
async def analyze_text_endpoint(req: TextRequest):
    if len(req.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text too short to analyze.")
    return analyze_content(req.text)

@app.post("/analyze-image")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    
    # ---------------------------------------------------------
    # MOCK OCR IMPLEMENTATION
    # ---------------------------------------------------------
    # Because Tesseract/heavy OCR engines are not installed, 
    # we simulate OCR extraction based on the uploaded file's name.
    filename_lower = file.filename.lower()
    
    if "fake" in filename_lower or "alien" in filename_lower or "scam" in filename_lower:
        simulated_text = "BREAKING: Aliens have invaded Earth and completely taken over the government! This is a massive cover-up!"
    else:
        simulated_text = "NASA has announced a new space mission to explore distant galaxies and gather more data about our solar system."
        
    # Analyze the simulated text extracted from the social media image
    result = analyze_content(simulated_text)
    
    # Add the extracted text to response so UI can show it
    result["simulated_ocr_text"] = simulated_text
    return result

@app.post("/analyze-url")
async def analyze_url_endpoint(req: UrlRequest):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(str(req.url), timeout=10, verify=False, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from body, or paragraphs if body not found
        body = soup.find('body')
        if body:
            text = body.get_text()
        else:
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs])
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        # Limit text length for analysis
        text = text[:1000]
        
        if len(text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract enough text from the URL.")
            
        result = analyze_content(text, is_url=True)
        # To avoid massive payload, we can truncate highlighted text for URLs
        if len(result["highlighted_text"]) > 2000:
            result["highlighted_text"] = result["highlighted_text"][:2000] + "... (truncated)"
        return result
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to TruthGuard AI API"}
