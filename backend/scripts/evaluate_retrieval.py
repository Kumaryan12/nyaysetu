import json
import sys
from pathlib import Path
from typing import Dict, List


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_ROOT))

from app.services.rag_service import RAGService


EVAL_PATH = BACKEND_ROOT / "app" / "data" / "eval" / "rag_retrieval_eval.json"


def normalize(value: str) -> str:
    return value.lower().strip()


def source_matches(actual_title: str, expected_sources: List[str]) -> bool:
    actual = normalize(actual_title)

    for expected in expected_sources:
        expected_norm = normalize(expected)

        if expected_norm in actual or actual in expected_norm:
            return True

    return False


def domain_matches(actual_domain: str, expected_domains: List[str]) -> bool:
    actual = normalize(actual_domain)

    for expected in expected_domains:
        if normalize(expected) == actual:
            return True

    return False


def evaluate_query(rag_service: RAGService, item: Dict) -> Dict:
    query = item["query"]
    expected_domains = item.get("expected_domains", [])
    expected_sources = item.get("expected_sources", [])

    results = rag_service.retrieve_sources(query=query, top_k=5)

    domain_hit_at_1 = False
    domain_hit_at_3 = False
    source_hit_at_5 = False
    reciprocal_rank = 0.0

    for index, result in enumerate(results):
        rank = index + 1
        title = result.title
        domain = result.domain or ""

        if rank == 1 and domain_matches(domain, expected_domains):
            domain_hit_at_1 = True

        if rank <= 3 and domain_matches(domain, expected_domains):
            domain_hit_at_3 = True

        if source_matches(title, expected_sources):
            source_hit_at_5 = True

            if reciprocal_rank == 0.0:
                reciprocal_rank = 1.0 / rank

    return {
        "query": query,
        "domain_hit_at_1": domain_hit_at_1,
        "domain_hit_at_3": domain_hit_at_3,
        "source_hit_at_5": source_hit_at_5,
        "reciprocal_rank": reciprocal_rank,
        "top_results": [
            {
                "rank": index + 1,
                "title": result.title,
                "score": result.score,
                "domain": result.domain or "",
                "source_type": result.source_type,
                "url": result.url,
            }
            for index, result in enumerate(results)
        ],
    }


def main() -> None:
    print("NyayaSetu retrieval evaluation")
    print("-----------------------------")
    print("Eval path:", EVAL_PATH)

    eval_items = json.loads(EVAL_PATH.read_text(encoding="utf-8"))

    rag_service = RAGService()

    results = []

    for item in eval_items:
        result = evaluate_query(rag_service, item)
        results.append(result)

    total = len(results)

    domain_recall_at_1 = sum(item["domain_hit_at_1"] for item in results) / total
    domain_recall_at_3 = sum(item["domain_hit_at_3"] for item in results) / total
    source_recall_at_5 = sum(item["source_hit_at_5"] for item in results) / total
    mrr = sum(item["reciprocal_rank"] for item in results) / total

    print("\nMetrics")
    print("-------")
    print(f"Domain Recall@1: {domain_recall_at_1:.3f}")
    print(f"Domain Recall@3: {domain_recall_at_3:.3f}")
    print(f"Source Recall@5: {source_recall_at_5:.3f}")
    print(f"MRR:             {mrr:.3f}")

    print("\nPer-query results")
    print("-----------------")

    for item in results:
        print("\nQuery:", item["query"])
        print("Domain@1:", item["domain_hit_at_1"])
        print("Domain@3:", item["domain_hit_at_3"])
        print("Source@5:", item["source_hit_at_5"])
        print("RR:", item["reciprocal_rank"])

        for result in item["top_results"][:3]:
            print(
                f"  {result['rank']}. {result['title']} "
                f"({result['domain']}) score={result['score']:.3f}"
            )

    output_path = BACKEND_ROOT / "app" / "data" / "eval" / "retrieval_eval_report.json"
    output_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\nSaved detailed report:", output_path)


if __name__ == "__main__":
    main()