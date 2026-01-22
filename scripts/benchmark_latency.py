"""
성능 벤치마크 스크립트
추천 시스템의 레이턴시(P50, P95, P99)를 측정합니다.
"""

import sys
import time
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
from app.services.recommendation import RecommendationService
from app.data.store import user_store, item_store
from app.data.sample_data import init_sample_data

def run_benchmark(num_users: int = 50, iterations_per_user: int = 100, count: int = 20):
    """
    성능 벤치마크 실행

    Args:
        num_users: 테스트할 사용자 수
        iterations_per_user: 사용자당 반복 횟수
        count: 추천할 아이템 개수
    """
    print(f"🚀 성능 벤치마크 시작")
    print(f"   - 사용자 수: {num_users}")
    print(f"   - 사용자당 반복: {iterations_per_user}")
    print(f"   - Top-K: {count}")
    print(f"   - 총 요청 수: {num_users * iterations_per_user:,}\n")

    service = RecommendationService()
    latencies = []

    # 워밍업 (첫 요청은 제외)
    print("🔥 워밍업 중...")
    for _ in range(5):
        service.get_recommendations(user_id="1", count=count)

    print("⏱️  측정 중...\n")

    # 실제 측정
    total_requests = num_users * iterations_per_user
    for user_id in range(1, num_users + 1):
        for iteration in range(iterations_per_user):
            start = time.perf_counter()
            try:
                service.get_recommendations(user_id=str(user_id), count=count)
                elapsed = (time.perf_counter() - start) * 1000  # ms
                latencies.append(elapsed)
            except Exception as e:
                print(f"⚠️  오류 (user_id={user_id}): {e}")
                continue

            # 진행 상황 출력 (10%마다)
            completed = (user_id - 1) * iterations_per_user + iteration + 1
            if completed % (total_requests // 10) == 0:
                progress = (completed / total_requests) * 100
                print(f"   진행: {progress:.0f}% ({completed:,}/{total_requests:,})")

    # 통계 계산
    latencies_array = np.array(latencies)

    p50 = np.percentile(latencies_array, 50)
    p95 = np.percentile(latencies_array, 95)
    p99 = np.percentile(latencies_array, 99)
    mean = np.mean(latencies_array)
    min_latency = np.min(latencies_array)
    max_latency = np.max(latencies_array)
    std = np.std(latencies_array)

    # 결과 출력
    print("\n" + "="*60)
    print("📊 벤치마크 결과")
    print("="*60)
    print(f"\n총 요청 수: {len(latencies):,}")
    print(f"\n레이턴시 분포:")
    print(f"  • Min     : {min_latency:>7.2f} ms")
    print(f"  • P50     : {p50:>7.2f} ms  (중앙값)")
    print(f"  • Mean    : {mean:>7.2f} ms  (평균)")
    print(f"  • P95     : {p95:>7.2f} ms  (상위 5%)")
    print(f"  • P99     : {p99:>7.2f} ms  (상위 1%)")
    print(f"  • Max     : {max_latency:>7.2f} ms")
    print(f"  • StdDev  : {std:>7.2f} ms")

    print(f"\n처리량 (Throughput):")
    throughput = 1000 / mean  # requests per second
    print(f"  • {throughput:.2f} requests/sec")

    print("\n" + "="*60)
    print("📋 README 업데이트용 값:")
    print("="*60)
    print(f"| **P50 (중앙값)** | ~{p50:.0f}ms | 절반의 요청이 {p50:.0f}ms 이내 완료 |")
    print(f"| **P95** | ~{p95:.0f}ms | 95%의 요청이 {p95:.0f}ms 이내 완료 |")
    print(f"| **P99** | ~{p99:.0f}ms | 99%의 요청이 {p99:.0f}ms 이내 완료 |")
    print(f"| **평균** | ~{mean:.0f}ms | 산술 평균 응답 시간 |")
    print("="*60 + "\n")

    return {
        "p50": p50,
        "p95": p95,
        "p99": p99,
        "mean": mean,
        "min": min_latency,
        "max": max_latency,
        "std": std,
        "total_requests": len(latencies),
        "throughput": throughput
    }


if __name__ == "__main__":
    # 데이터 초기화
    print("📦 데이터 로드 중...")
    init_sample_data()

    # 데이터 스토어 확인
    total_users = len(user_store.get_all_users())
    total_items = len(item_store.get_all_items())

    print(f"   - 사용자: {total_users}명")
    print(f"   - 상품: {total_items}개\n")

    if total_items == 0:
        print("❌ 오류: 상품 데이터가 없습니다. musinsa_products.json 파일을 확인하세요.")
        sys.exit(1)

    # 사용자 수 결정 (최소 10명 필요)
    test_users = min(50, max(10, total_users)) if total_users > 0 else 10

    results = run_benchmark(num_users=test_users, iterations_per_user=100, count=20)

    print("✅ 벤치마크 완료!")
