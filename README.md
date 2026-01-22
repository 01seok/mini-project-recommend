# X 추천 알고리즘을 참고한 의류 추천 서비스

X(Twitter) 추천 알고리즘의 핵심 원리를 Python/FastAPI로 구현한 옷 추천 서비스입니다.

## 📋 프로젝트 의의

### X(Twitter) 알고리즘 학습
이 프로젝트는 X(구 Twitter)가 **2026년 1월** 오픈소스로 공개한 추천 알고리즘의 핵심 원리를 직접 구현하여 학습하는 것을 목표로 합니다.

**X 알고리즘의 핵심 특징:**
- **Multi-Action Prediction**: 좋아요/클릭/구매 등 다중 행동에 대한 확률을 독립적으로 예측
- **Weighted Scoring**: 긍정적 행동(구매, 좋아요)과 부정적 행동(숨김, 관심없음)에 가중치를 적용
- **Diversity Penalty**: 특정 브랜드/저자 편중 방지를 위한 다양성 점수

### 구현 아키텍처
```
Request → Query Hydration → Candidate Sourcing → 
Filtering → Scoring → Selection → Response
```

---

## 📊 NDCG란?

NDCG (Normalized Discounted Cumulative Gain)는 추천 시스템의 순위 품질을 평가하는 표준 메트릭입니다.

### 핵심 개념

```
DCG@k = Σ (2^relevance_i - 1) / log₂(i + 1)
NDCG@k = DCG@k / IDCG@k
```

| 개념 | 설명 |
|------|------|
| **Relevance** | 각 아이템의 관련성 점수 (0~3) |
| **DCG** | 상위 순위에 관련성 높은 아이템이 있을수록 높은 점수 |
| **IDCG** | 완벽한 순서(이상적 순위)일 때의 DCG |
| **NDCG** | DCG / IDCG로 0~1 사이 정규화된 점수 |

### 왜 NDCG인가?
- **순위 민감**: 상위 결과가 더 중요하게 평가됨
- **표준화**: 0~1 범위로 비교 가능
- **산업 표준**: Netflix, Amazon, Google 등에서 사용

---

## 📈 평가 결과 및 분석

### 성능 지표

무신사 스타일 상품 데이터 **1000개**와 합성 사용자 **50명**을 대상으로 평가:

| Metric | Score | 해석 |
|--------|-------|------|
| **NDCG@5** | 0.5866 | 상위 5개 추천 중 59% 정도가 이상적 순서에 근접 |
| **NDCG@10** | 0.6825 | 상위 10개로 확장하면 68%까지 향상 |
| **NDCG@20** | 0.8107 | 상위 20개에서 81% 달성 (우수) |
| Precision@5 | 1.0000 | 상위 5개 모두 관련 있는 아이템 |
| MRR | 1.0000 | 첫 번째 결과가 항상 관련 있음 |

### 결과 해석

| NDCG 범위 | 평가 |
|-----------|------|
| 0.8 이상 | 매우 우수 |
| 0.6 ~ 0.8 | 양호 |
| 0.4 ~ 0.6 | 보통 |
| 0.4 미만 | 개선 필요 |

**우리 시스템 평가**: NDCG@20 = 0.81로 **매우 우수** 수준

하지만 NDCG@5 = 0.59는 **상위 추천의 순서 최적화가 필요**함을 시사합니다.

---

## 🧪 AI Agent 테스트 방법론

### 테스트 설계

AI Agent를 활용하여 다음과 같은 체계적인 테스트를 수행했습니다:

#### 1. 데이터 수집
```python
# 무신사 웹사이트에서 브라우저 기반 크롤링
# __NEXT_DATA__ JSON 및 DOM 파싱으로 상품 정보 추출
# 실제 브랜드: 퍼스텝, 메르시마리에, 마리떼 프랑소와 저버 등
```

#### 2. 합성 사용자 생성
```python
# 각 사용자에게 부여되는 특성:
# - 선호 브랜드 2~4개
# - 선호 카테고리 1~2개  
# - 가격대 범위
# - 가상의 구매 이력 (ground truth)
```

#### 3. 평가 자동화
```bash
python scripts/run_evaluation.py --users 50 --k 20 --seed 42
```

### 테스트 결과 스크린샷

AI Agent가 브라우저에서 무신사 상품을 크롤링하는 과정:

1. 카테고리 페이지 접근 및 스크롤
2. JavaScript로 DOM에서 상품 정보 추출
3. 브랜드, 상품명, 가격, 이미지 URL 파싱
4. 84개 실제 상품 데이터 수집 성공

### 2. UI 검증 (AI Agent)

AI Agent가 직접 추천 시스템을 실행하여 실제 무신사 이미지와 추천 로직이 정상 작동함을 검증했습니다.

![UI Verification](assets/real_images_verification.png)

---

## 🔧 개선점

### 현재 한계

| 영역 | 현재 상태 | 개선 방향 |
|------|----------|----------|
| **NDCG@5** | 0.59 | 상위 순위 품질 향상 필요 |
| **Cold Start** | 새 사용자에 기본 추천 | 협업 필터링/인기 기반 하이브리드 |
| **Real-time ML** | 휴리스틱 스코어링 | 실제 ML 모델 (XGBoost, DNN) 적용 |
| **Feature** | 브랜드/카테고리만 사용 | 이미지 임베딩, 텍스트 임베딩 추가 |

### 다음 단계 로드맵

1. **실제 ML 모델 적용**
   - XGBoost로 Multi-Action Prediction 학습
   - 사용자 행동 로그 기반 fine-tuning

2. **임베딩 도입**
   - CLIP 모델로 상품 이미지 임베딩
   - Word2Vec/BERT로 상품명 임베딩
   - 코사인 유사도 기반 후보 탐색

3. **A/B 테스트 프레임워크**
   - 실시간 메트릭 수집
   - 통계적 유의미성 검정

4. **개인화 강화**
   - 실시간 사용자 행동 반영
   - 세션 기반 컨텍스트 추가

---

## 🚀 핵심 기능

- **Multi-Action Prediction**: like, click, purchase 등 다중 행동 확률 예측
- **Pipeline Architecture**: Source → Hydration → Filter → Score → Select
- **Weighted Scoring**: 긍정/부정 행동 가중치 합산 (`P(purchase)*2.0 - P(hide)*3.0`)
- **Diversity Scoring**: 브랜드 편중 방지
- **상품 이미지 표시**: 무신사 CDN 연동

---

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
│   ├── crawler.py             # 무신사 크롤러
│   └── generate_dataset.py    # 데이터셋 생성
└── routers/         # API 라우터
```

---

## 🏗️ 아키텍처 다이어그램

### 1. 파이프라인 흐름도

전체 추천 파이프라인의 데이터 흐름을 보여줍니다:

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#ffffff', 'primaryTextColor':'#000000', 'primaryBorderColor':'#7C7C7C', 'lineColor':'#7C7C7C', 'secondaryColor':'#f0f0f0', 'tertiaryColor':'#ffffff', 'background':'#ffffff', 'mainBkg':'#ffffff', 'secondBkg':'#f0f0f0', 'edgeLabelBackground':'#ffffff'}}}%%
graph TD
    A[사용자 요청] --> B[Query Hydration]
    B --> C{Candidate Sourcing}

    C --> D1[In-Network Source<br/>선호 브랜드/카테고리]
    C --> D2[Out-of-Network Source<br/>전체 카탈로그]

    D1 --> E[Combined Source<br/>후보 병합 & 중복 제거]
    D2 --> E

    E --> F[Filtering Stage]
    F --> F1[Duplicate Filter]
    F1 --> F2[Seen Items Filter]
    F2 --> F3[Engaged Items Filter]

    F3 --> G[Scoring Stage]
    G --> G1[MultiAction Scorer<br/>7개 행동 확률 예측]
    G1 --> G2[Weighted Scorer<br/>가중치 합산]
    G2 --> G3[Diversity Scorer<br/>브랜드 다양성 페널티]

    G3 --> H[Selection Stage<br/>TopK Selector]
    H --> I[추천 결과 응답]

    style A fill:#e1f5ff,stroke:#1976d2
    style I fill:#e1f5ff,stroke:#1976d2
    style G1 fill:#fff3cd,stroke:#f57c00
    style G2 fill:#fff3cd,stroke:#f57c00
    style G3 fill:#fff3cd,stroke:#f57c00
```

### 2. Multi-Action 점수 계산

7가지 행동 확률을 예측하고 가중치를 적용하여 최종 점수를 계산하는 과정:

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#ffffff', 'primaryTextColor':'#000000', 'primaryBorderColor':'#7C7C7C', 'lineColor':'#7C7C7C', 'secondaryColor':'#f0f0f0', 'tertiaryColor':'#ffffff', 'background':'#ffffff', 'mainBkg':'#ffffff', 'secondBkg':'#f0f0f0', 'edgeLabelBackground':'#ffffff'}}}%%
graph LR
    A[사용자 프로필] --> B[Affinity 계산]
    C[상품 정보] --> B

    B --> D[브랜드 친화도<br/>0.0-1.0]
    B --> E[스타일 친화도<br/>0.0-1.0]
    B --> F[카테고리 친화도<br/>0.0-1.0]

    D --> G[MultiAction Scorer]
    E --> G
    F --> G

    G --> H1[P좋아요 × 1.0]
    G --> H2[P클릭 × 0.5]
    G --> H3[P장바구니 × 1.5]
    G --> H4[P구매 × 3.0]
    G --> H5[P공유 × 2.0]
    G --> H6[P관심없음 × -1.0]
    G --> H7[P숨김 × -2.0]

    H1 --> I[최종 점수 합산]
    H2 --> I
    H3 --> I
    H4 --> I
    H5 --> I
    H6 --> I
    H7 --> I

    I --> J[Diversity Penalty<br/>0.8^count]
    J --> K[최종 추천 점수]

    style G fill:#fff3cd,stroke:#f57c00
    style I fill:#d4edda,stroke:#388e3c
    style K fill:#d4edda,stroke:#388e3c
```

### 3. 시스템 레이어 아키텍처

FastAPI 기반 4-Tier 아키텍처:

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#ffffff', 'primaryTextColor':'#000000', 'primaryBorderColor':'#7C7C7C', 'lineColor':'#7C7C7C', 'secondaryColor':'#f0f0f0', 'tertiaryColor':'#ffffff', 'background':'#ffffff', 'mainBkg':'#ffffff', 'secondBkg':'#f0f0f0', 'edgeLabelBackground':'#ffffff', 'clusterBkg':'#ffffff', 'clusterBorder':'#7C7C7C'}}}%%
graph TB
    subgraph "🌐 Presentation Layer"
        A1[Web UI<br/>HTML/CSS/JS]
        A2[API Client<br/>HTTP/JSON]
    end

    subgraph "🔌 API Layer - FastAPI Routers"
        B1["🔵 RecommendRouter<br/>GET /api/recommend<br/>사용자별 추천 조회"]
        B2["🟢 EngagementRouter<br/>POST /api/engagement<br/>사용자 행동 기록"]
    end

    subgraph "⚙️ Service Layer - Business Logic"
        C1["📊 RecommendationService<br/>• 파이프라인 오케스트레이션<br/>• Context 생성 및 관리"]
        C2["📝 EngagementService<br/>• 행동 데이터 저장<br/>• 이력 집계"]
        C3["📈 EvaluationService<br/>• NDCG 계산<br/>• 성능 메트릭 측정"]
    end

    subgraph "🔄 Pipeline Layer - Recommendation Components"
        direction TB
        D1["1️⃣ Sources<br/>• InNetworkSource<br/>• OutOfNetworkSource<br/>• CombinedSource"]
        D2["2️⃣ Filters<br/>• DuplicateFilter<br/>• SeenItemsFilter<br/>• EngagedItemsFilter"]
        D3["3️⃣ Scorers<br/>• MultiActionScorer<br/>• WeightedScorer<br/>• DiversityScorer"]
        D4["4️⃣ Selector<br/>• TopKSelector"]

        D1 --> D2
        D2 --> D3
        D3 --> D4
    end

    subgraph "💾 Data Layer - Storage"
        E1[("👤 UserStore<br/>사용자 프로필<br/>선호 브랜드/카테고리")]
        E2[("📦 ItemStore<br/>상품 데이터<br/>1000개 무신사 상품")]
        E3[("📋 EngagementStore<br/>행동 히스토리<br/>like/purchase/click")]
    end

    subgraph "📂 Data Source"
        F1[("📄 musinsa_products.json")]
    end

    A1 --> B1
    A2 --> B1
    A2 --> B2

    B1 --> C1
    B2 --> C2

    C1 --> D1
    C1 --> E1
    C1 --> E2
    C1 --> E3

    C2 --> E3
    C3 --> E2
    C3 --> E3

    E2 -.->|초기 로드| F1

    style B1 fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style B2 fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
    style C1 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style D1 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style D2 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style D3 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style D4 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style E1 fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    style E2 fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    style E3 fill:#fce4ec,stroke:#c2185b,stroke-width:2px
```

### 4. 주요 컴포넌트 설명

| 레이어 | 컴포넌트 | 책임 | 코드 위치 |
|--------|---------|------|----------|
| **Router** | recommend.py | API 엔드포인트 정의 | [app/routers/recommend.py](app/routers/recommend.py) |
| **Service** | recommendation.py | 파이프라인 오케스트레이션 | [app/services/recommendation.py](app/services/recommendation.py) |
| **Pipeline** | sources.py | 후보 아이템 소싱 | [app/pipeline/sources.py](app/pipeline/sources.py) |
| **Pipeline** | filters.py | 부적합 후보 필터링 | [app/pipeline/filters.py](app/pipeline/filters.py) |
| **Pipeline** | scorers.py | Multi-Action 점수 계산 | [app/pipeline/scorers.py](app/pipeline/scorers.py) |
| **Pipeline** | selectors.py | Top-K 선택 | [app/pipeline/selectors.py](app/pipeline/selectors.py) |
| **Data** | store.py | 인메모리 데이터 저장소 | [app/data/store.py](app/data/store.py) |

---

## 🔄 추천 요청 시퀀스 다이어그램

사용자가 추천을 요청했을 때 시스템 내부에서 일어나는 전체 흐름:

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#ffffff', 'primaryTextColor':'#000000', 'primaryBorderColor':'#7C7C7C', 'lineColor':'#7C7C7C', 'secondaryColor':'#f0f0f0', 'tertiaryColor':'#ffffff', 'background':'#ffffff', 'mainBkg':'#ffffff', 'secondBkg':'#f0f0f0', 'edgeLabelBackground':'#ffffff', 'actorBkg':'#e3f2fd', 'actorBorder':'#1976d2', 'actorTextColor':'#000000', 'actorLineColor':'#7C7C7C', 'signalColor':'#7C7C7C', 'signalTextColor':'#000000', 'labelBoxBkgColor':'#f0f0f0', 'labelBoxBorderColor':'#7C7C7C', 'labelTextColor':'#000000', 'loopTextColor':'#000000', 'noteBorderColor':'#7C7C7C', 'noteBkgColor':'#fff3cd', 'noteTextColor':'#000000', 'activationBorderColor':'#7C7C7C', 'activationBkgColor':'#e1f5ff', 'sequenceNumberColor':'#000000'}}}%%
sequenceDiagram
    actor User as 👤 사용자
    participant API as FastAPI Router
    participant Service as RecommendationService
    participant Pipeline as 추천 파이프라인

    User->>+API: GET /api/recommend?user_id=1
    API->>+Service: get_recommendations(user_id)

    Note over Service: Query Hydration<br/>사용자 프로필 & 참여 이력 조회

    Service->>+Pipeline: 1️⃣ Candidate Sourcing
    Pipeline-->>-Service: 후보 200개 (In/Out Network)

    Service->>+Pipeline: 2️⃣ Filtering
    Pipeline-->>-Service: 필터링된 후보 150개

    Service->>+Pipeline: 3️⃣ Scoring
    Note right of Pipeline: Multi-Action 확률 예측<br/>가중치 합산<br/>다양성 페널티
    Pipeline-->>-Service: 점수화된 후보

    Service->>+Pipeline: 4️⃣ Selection
    Pipeline-->>-Service: Top 20 추천 결과

    Service-->>-API: RecommendationResponse
    API-->>-User: JSON Response
```

---

## 📊 기술 스택 및 아키텍처 특징

### 구현 특징

#### ✅ 강점
- **Strategy Pattern**: Source, Filter, Scorer, Selector 모두 추상 인터페이스 구현
- **Composite Pattern**: CompositeFilter, CompositeScorer로 컴포넌트 조합 가능
- **Pipeline Pattern**: 명확한 입출력 계약으로 단계별 처리
- **Dependency Injection**: PipelineContext로 의존성 전달
- **타입 안전성**: Pydantic BaseModel + 타입 힌트 완비
- **평가 인프라**: NDCG, Precision, MRR 메트릭 구현

#### ⚠️ 개선 고려사항
- **확장성**: 인메모리 저장소로 대용량 데이터 처리 제한
- **실시간 학습**: 현재는 휴리스틱 기반, ML 모델 적용 가능
- **캐싱**: Redis 등 캐싱 레이어 미적용
- **에러 처리**: 엣지 케이스 핸들링 보강 필요

### 코드 복잡도

| 파일 | 라인 수 | 클래스 수 | 특징 |
|------|---------|----------|------|
| scorers.py | 207 | 4 | 다중 행동 확률 예측 및 가중치 계산 |
| sources.py | 92 | 3 | In/Out Network 후보 소싱 |
| filters.py | 82 | 5 | 중복/본 상품/참여 이력 필터링 |
| recommendation.py | 172 | 1 | 파이프라인 오케스트레이션 |
| selectors.py | 26 | 1 | Top-K 선택 |

### 성능 특성

실측 벤치마크 결과 (1000개 상품, 1000회 요청):

| Metric | Value | 설명 |
|--------|-------|------|
| **P50 (중앙값)** | 5ms | 절반의 요청이 5ms 이내 완료 |
| **P95** | 7ms | 95%의 요청이 7ms 이내 완료 |
| **P99** | 8ms | 99%의 요청이 8ms 이내 완료 |
| **평균** | 5ms | 산술 평균 응답 시간 |
| **처리량** | 205 req/sec | 초당 처리 가능한 요청 수 |
| **파이프라인 병목** | MultiActionScorer | Affinity 계산이 가장 오래 걸림 |
| **메모리 사용** | ~100MB | JSON 데이터 로드 시 |

*측정 환경: Python 3.9, macOS, 인메모리 저장소*

성능 측정 방법:
```bash
python scripts/benchmark_latency.py
```

---

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
- `GET /health` - 헬스 체크
- `GET /` - 테스트 웹 UI

---

## 🐳 Docker 배포

### 이미지 빌드 및 실행

```bash
# Docker Compose로 실행 (권장)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 수동 Docker 실행

```bash
# 이미지 빌드
docker build -t musinsa-recommend:latest .

# 컨테이너 실행
docker run -d \
  -p 8080:8080 \
  --name recommend-service \
  -v $(pwd)/app/data/musinsa_products.json:/app/app/data/musinsa_products.json:ro \
  musinsa-recommend:latest

# Health Check
curl http://localhost:8080/health
```

### 배포 확인

```bash
# API 테스트
curl "http://localhost:8080/api/recommend?user_id=1&count=5"

# 웹 UI 접속
open http://localhost:8080
```

### Docker 특징

- **경량 이미지**: Python 3.9-slim 기반
- **Health Check**: 30초 간격으로 자동 헬스 체크
- **자동 재시작**: 컨테이너 장애 시 자동 재시작
- **볼륨 마운트**: 상품 데이터 외부 관리 가능
- **포트**: 8080 (변경 가능)

---

## 📈 평가 실행

```bash
# NDCG 평가 실행
python scripts/run_evaluation.py --users 100 --k 20

# 결과 확인
cat scripts/evaluation_results.json
```

---

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

---

## 📚 참고

- X Algorithm: https://github.com/xai-org/x-algorithm
- NDCG Metric: [Wikipedia](https://en.wikipedia.org/wiki/Discounted_cumulative_gain)
