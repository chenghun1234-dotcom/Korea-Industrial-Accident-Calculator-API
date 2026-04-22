from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import math

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Korea Industrial Accident Calculator API")

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, you can replace "*" with ["https://korea-industrial-accident-api.web.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Constants & Data Load ---
def get_standards():
    try:
        with open('standards.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "year": 2026,
            "max_daily_wage": 268299,
            "min_daily_wage": 82560,
            "update_date": "2026-04-22"
        }

# --- Models ---

class WageCalculationRequest(BaseModel):
    three_month_total_wage: float  # 최근 3개월간 임금 총액
    total_days: int                # 최근 3개월간 총 일수 (보통 89~92일)
    annual_bonus: Optional[float] = 0.0  # 상여금 (연간 총액)
    annual_leave_pay: Optional[float] = 0.0 # 연차수당 (연간 총액)

class TemporaryDisabilityRequest(BaseModel):
    average_wage: float
    injury_days: int

class DisabilityBenefitRequest(BaseModel):
    average_wage: float
    grade: int  # 1급~14급
    payment_method: str  # "lump_sum" (일시금) or "pension" (연금)

class SurvivorBenefitRequest(BaseModel):
    average_wage: float
    num_survivors: int  # 유족 수 (최대 4인)

# --- Logic Helpers ---

def apply_wage_limits(avg_wage: float):
    standards = get_standards()
    if avg_wage > standards['max_daily_wage']:
        return standards['max_daily_wage']
    if avg_wage < standards['min_daily_wage']:
        return standards['min_daily_wage']
    return avg_wage

# --- Endpoints ---

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Korea Industrial Accident API</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Noto+Sans+KR:wght@300;400;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --secondary: #a855f7;
                --glass: rgba(255, 255, 255, 0.1);
                --text: #ffffff;
            }
            body {
                margin: 0;
                padding: 0;
                font-family: 'Outfit', 'Noto Sans KR', sans-serif;
                background: radial-gradient(circle at top left, #1e1b4b, #0f172a);
                color: var(--text);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .glass-card {
                background: var(--glass);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 24px;
                padding: 3rem;
                max-width: 800px;
                width: 90%;
                text-align: center;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
                background: linear-gradient(to right, #818cf8, #c084fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            p {
                font-size: 1.2rem;
                color: #94a3b8;
                line-height: 1.6;
            }
            .badge {
                display: inline-block;
                padding: 0.5rem 1rem;
                background: rgba(99, 102, 241, 0.2);
                border: 1px solid var(--primary);
                border-radius: 99px;
                font-size: 0.9rem;
                color: #818cf8;
                margin-bottom: 2rem;
            }
            .buttons {
                margin-top: 2rem;
                display: flex;
                gap: 1rem;
                justify-content: center;
            }
            .btn {
                padding: 1rem 2rem;
                border-radius: 12px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s;
            }
            .btn-primary {
                background: var(--primary);
                color: white;
            }
            .btn-outline {
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
            }
            .btn:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin-top: 3rem;
                width: 100%;
            }
            .feature-item {
                background: rgba(255, 255, 255, 0.05);
                padding: 1.5rem;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .feature-item h3 {
                margin-top: 0;
                color: #e2e8f0;
            }
        </style>
    </head>
    <body>
        <div class="glass-card">
            <div class="badge">v1.2.0 - 2026 Standards Active</div>
            <h1>South Korea Industrial Accident API</h1>
            <p>한국 산재 보상 기준을 자동으로 산정하는 고성능 B2B API 엔진입니다.<br>병원 산재 담당자 및 기업 노무 실무자를 위해 설계되었습니다.</p>
            
            <div class="buttons">
                <a href="/docs" class="btn btn-primary">API Documentation</a>
                <a href="/standards" class="btn btn-outline">Check 2026 Standards</a>
            </div>

            <div class="features">
                <div class="feature-item">
                    <h3>평균임금</h3>
                    <p>상여금 및 연차수당 자동 포함 정밀 산출</p>
                </div>
                <div class="feature-item">
                    <h3>휴업급여</h3>
                    <p>최고/최저 상한액 자동 적용 계산</p>
                </div>
                <div class="feature-item">
                    <h3>장해급여</h3>
                    <p>1-14급 급여 및 연금 자동 변환</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/standards")
def read_standards():
    return get_standards()

@app.post("/calculate/average-wage")
def calculate_average_wage(req: WageCalculationRequest):
    # 공식: (3개월 임금 + (상여금/4) + (연차수당/4)) / 3개월 총 일수
    # 법적으로 상여금과 연차수당은 1년치를 3/12(즉 1/4)만큼 반영함
    bonus_reflection = req.annual_bonus / 4
    leave_reflection = req.annual_leave_pay / 4
    
    total_reflection_wage = req.three_month_total_wage + bonus_reflection + leave_reflection
    avg_wage = total_reflection_wage / req.total_days
    
    return {
        "raw_avg_wage": round(avg_wage, 2),
        "basis": {
            "three_month_wages": req.three_month_total_wage,
            "bonus_reflected": bonus_reflection,
            "leave_reflected": leave_reflection,
            "total_days": req.total_days
        }
    }

@app.post("/calculate/temporary-disability")
def calculate_temporary_disability(req: TemporaryDisabilityRequest):
    applied_wage = apply_wage_limits(req.average_wage)
    
    # 휴업급여 = 평균임금의 70%
    daily_benefit = applied_wage * 0.7
    total_benefit = daily_benefit * req.injury_days
    
    return {
        "applied_avg_wage": round(applied_wage, 0),
        "daily_benefit": round(daily_benefit, 0),
        "total_benefit": round(total_benefit, 0),
        "calculation": f"{round(applied_wage, 0)} * 70% * {req.injury_days}일"
    }

@app.post("/calculate/disability-benefit")
def calculate_disability_benefit(req: DisabilityBenefitRequest):
    applied_wage = apply_wage_limits(req.average_wage)
    
    # 장해 등급별 일수 (법정 기준)
    grade_days = {
        1: 1474, 2: 1313, 3: 1152, 4: 1012, 5: 869, 6: 737, 7: 611,
        8: 495, 9: 385, 10: 297, 11: 220, 12: 154, 13: 99, 14: 55
    }
    
    if req.grade not in grade_days:
        raise HTTPException(status_code=400, detail="Invalid disability grade (1-14)")
    
    days = grade_days[req.grade]
    total_benefit = applied_wage * days
    
    # 간략화를 위해 일시금 기준 정보를 주로 반환
    return {
        "grade": req.grade,
        "applied_avg_wage": round(applied_wage, 0),
        "statutory_days": days,
        "total_lump_sum": round(total_benefit, 0),
        "note": "1~3급은 연금 수령이 원칙이며, 4~7급은 선택 가능합니다."
    }

@app.post("/calculate/survivor-benefit")
def calculate_survivor_benefit(req: SurvivorBenefitRequest):
    applied_wage = apply_wage_limits(req.average_wage)
    
    # 장의비: 평균임금 120일분 (최고/최저 한도 내)
    funeral_expenses = applied_wage * 120
    
    # 유족연금 (기초연금액 = 평균임금 * 365 * 47%)
    # 가산금액: 유족 1인당 5% 추가 (최대 20%)
    base_percentage = 47
    survivor_bonus = min((req.num_survivors - 1) * 5, 20) if req.num_survivors > 0 else 0
    total_percentage = base_percentage + survivor_bonus
    
    annual_pension = (applied_wage * 365) * (total_percentage / 100)
    
    return {
        "applied_avg_wage": round(applied_wage, 0),
        "funeral_expenses": round(funeral_expenses, 0),
        "survivor_annual_pension": round(annual_pension, 0),
        "monthly_pension": round(annual_pension / 12, 0),
        "pension_percentage": f"{total_percentage}%"
    }
