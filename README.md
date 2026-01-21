# X-Style Clothing Recommendation Service

X(Twitter) 추천 알고리즘의 핵심 원리를 Python/FastAPI로 구현한 옷 추천 서비스입니다.

## 핵심 기능

- **Multi-Action Prediction**: like, click, purchase 등 다중 행동 확률 예측
- **Pipeline Architecture**: Source → Hydration → Filter → Score → Select
- **Weighted Scoring**: 긍정/부정 행동 가중치 합산
- **Diversity Scoring**: 브랜드 편중 방지

## 설치 및 실행

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload --port 8080
```

## API 엔드포인트

- `GET /api/recommend?user_id={id}` - 추천 목록 조회
- `POST /api/engagement` - 사용자 행동 기록
- `GET /` - 테스트 웹 UI

## 참고

- X Algorithm: https://github.com/xai-org/x-algorithm
