# X-Style Clothing Recommendation Service

X(Twitter) 추천 알고리즘의 핵심 원리를 Python/FastAPI로 구현한 옷 추천 서비스입니다.

## 📋 프로젝트 의의

### X(Twitter) 알고리즘 학습
이 프로젝트는 X(구 Twitter)가 2023년 오픈소스로 공개한 추천 알고리즘의 핵심 원리를 직접 구현하여 학습하는 것을 목표로 합니다.

**X 알고리즘의 핵심 특징:**
- **Multi-Action Prediction**: 좋아요/클릭/구매 등 다중 행동에 대한 확률을 독립적으로 예측
- **Weighted Scoring**: 긍정적 행동(구매, 좋아요)과 부정적 행동(숨김, 관심없음)에 가중치를 적용
- **Diversity Penalty**: 특정 브랜드/저자 편중 방지를 위한 다양성 점수

### 구현 아키텍처
```
Request → Query Hydration → Candidate Sourcing → 
Filtering → Scoring → Selection → Response
```

## 📊 성능 평가 (NDCG)

무신사 스타일 상품 데이터 1000개와 합성 사용자 50명을 대상으로 평가:

| Metric | Score |
|--------|-------|
| **NDCG@5** | 0.5866 |
| **NDCG@10** | 0.6825 |
| **NDCG@20** | 0.8107 |
| Precision@5 | 1.0000 |
| Precision@10 | 1.0000 |
| MRR | 1.0000 |

> NDCG (Normalized Discounted Cumulative Gain): 추천 순위의 품질을 측정하는 표준 메트릭.
> 상위에 관련성 높은 아이템이 배치될수록 높은 점수를 받습니다.

## 🚀 핵심 기능

- **Multi-Action Prediction**: like, click, purchase 등 다중 행동 확률 예측
- **Pipeline Architecture**: Source → Hydration → Filter → Score → Select
- **Weighted Scoring**: 긍정/부정 행동 가중치 합산 (`P(purchase)*2.0 - P(hide)*3.0`)
- **Diversity Scoring**: 브랜드 편중 방지

## 📁 프로젝트 구조

```
app/
├── models/          # Pydantic 데이터 모델
│   ├── item.py      # 상품, ActionScores, ScoredItem
│   ├── user.py      # 사용자 선호도
│   └── engagement.py # 사용자 행동 기록
├── pipeline/        # 추천 파이프라인 컴포넌트
│   ├── sources.py   # Candidate Sourcing (In/Out Network)
│   ├── filters.py   # Filtering (Duplicate, Seen, Engaged)
│   ├── scorers.py   # Scoring (MultiAction, Weighted, Diversity)
│   └── selectors.py # Selection (TopK)
├── services/        # 비즈니스 로직
│   ├── recommendation.py # 추천 서비스
│   └── evaluation.py     # NDCG 평가
├── data/            # 데이터 및 저장소
│   ├── musinsa_products.json  # 무신사 스타일 상품 1000개
│   └── sample_data.py         # 샘플 데이터 생성
└── routers/         # API 라우터
```

## ⚙️ 설치 및 실행

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload --port 8080
```

## 🔌 API 엔드포인트

- `GET /api/recommend?user_id={id}` - 추천 목록 조회
- `POST /api/engagement` - 사용자 행동 기록
- `GET /` - 테스트 웹 UI

## 📈 평가 실행

```bash
# NDCG 평가 실행
python scripts/run_evaluation.py --users 100 --k 20

# 결과 확인
cat scripts/evaluation_results.json
```

## ⏱️ 개발 타임라인

| 단계 | 소요 시간 |
|------|----------|
| X 알고리즘 분석 | 30분 |
| FastAPI 프로젝트 구조 | 20분 |
| 파이프라인 컴포넌트 구현 | 40분 |
| 웹 UI 구현 | 20분 |
| 무신사 데이터 생성 | 20분 |
| NDCG 평가 구현 | 30분 |
| **총** | **~2.5시간** |

## 📚 참고

- X Algorithm: https://github.com/xai-org/x-algorithm
- NDCG Metric: [Wikipedia](https://en.wikipedia.org/wiki/Discounted_cumulative_gain)
