from __future__ import annotations

"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import os, sys, json, math
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, TEST_SET_PATH


# Keep evaluator provenance separate from generation and judge configuration.
# These identifiers are passed to the evaluator clients below and returned in
# evaluate_ragas() metadata for the Phase A report.
RAGAS_EVALUATOR_LLM_MODEL = os.getenv("RAGAS_EVALUATOR_LLM_MODEL", "gpt-4o-mini").strip()
RAGAS_EVALUATOR_EMBEDDING_MODEL = os.getenv(
    "RAGAS_EVALUATOR_EMBEDDING_MODEL", "text-embedding-3-small"
).strip()


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    """Run all four required RAGAS metrics and return results plus provenance.

    The evaluator clients are configured explicitly so RAGAS defaults cannot
    silently select unreported models. Failed or non-finite metric results are
    raised as errors; they are never converted into fabricated zero scores.
    """
    input_lengths = {
        len(questions), len(answers), len(contexts), len(ground_truths),
    }
    if len(input_lengths) != 1:
        raise ValueError(
            "questions, answers, contexts, and ground_truths must have equal lengths"
        )
    if not questions:
        raise ValueError("RAGAS evaluation requires at least one question")
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for the configured RAGAS evaluators")
    if not RAGAS_EVALUATOR_LLM_MODEL or not RAGAS_EVALUATOR_EMBEDDING_MODEL:
        raise ValueError("RAGAS evaluator model identifiers must be non-empty")

    from datasets import Dataset
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from ragas import evaluate
    from ragas.metrics import (
        AnswerRelevancy,
        ContextPrecision,
        ContextRecall,
        Faithfulness,
    )

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })

    # Fresh metric instances prevent a prior RAGAS invocation from retaining
    # an earlier/default evaluator on the module-level metric singletons.
    metrics = [Faithfulness(), AnswerRelevancy(), ContextPrecision(), ContextRecall()]
    llm = ChatOpenAI(
        model_name=RAGAS_EVALUATOR_LLM_MODEL,
        openai_api_key=OPENAI_API_KEY,
        temperature=0,
    )
    embeddings = OpenAIEmbeddings(
        model=RAGAS_EVALUATOR_EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY,
    )

    result = evaluate(
        dataset,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings,
        raise_exceptions=True,
    )
    frame = result.to_pandas()
    if len(frame) != len(questions):
        raise ValueError(
            f"RAGAS returned {len(frame)} rows for {len(questions)} input questions"
        )

    metric_names = (
        "faithfulness",
        "answer_relevancy",
        "context_precision",
        "context_recall",
    )
    missing_metrics = [name for name in metric_names if name not in frame.columns]
    if missing_metrics:
        raise ValueError(f"RAGAS result is missing metrics: {missing_metrics}")

    def _metric_score(value, metric_name: str, row_index: int) -> float:
        try:
            score = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"RAGAS returned a non-numeric {metric_name} at row {row_index}: {value!r}"
            ) from exc
        if not math.isfinite(score) or not 0.0 <= score <= 1.0:
            raise ValueError(
                f"RAGAS returned an invalid {metric_name} at row {row_index}: {score!r}"
            )
        return score

    per_question = []
    for row_index, (_, row) in enumerate(frame.iterrows()):
        scores = {
            name: _metric_score(row[name], name, row_index)
            for name in metric_names
        }
        per_question.append(EvalResult(
            question=questions[row_index],
            answer=answers[row_index],
            contexts=list(contexts[row_index]),
            ground_truth=ground_truths[row_index],
            **scores,
        ))

    evaluator_models = list(dict.fromkeys((
        llm.model_name,
        embeddings.model,
    )))
    aggregate = {
        name: sum(getattr(item, name) for item in per_question) / len(per_question)
        for name in metric_names
    }
    aggregate["per_question"] = per_question
    aggregate["metadata"] = {"evaluator_models": evaluator_models}
    return aggregate


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    diagnostic_tree = {
        "faithfulness": ("LLM hallucinating", "Tighten prompt, lower temperature, and verify factual grounding."),
        "context_recall": ("Missing relevant chunks", "Improve chunking or expand retrieval with BM25/dense hybrid search."),
        "context_precision": ("Too many irrelevant chunks", "Add reranking and metadata filters to reduce noise."),
        "answer_relevancy": ("Answer doesn't match question", "Improve prompt template and ground the answer in the retrieved context."),
    }

    if not eval_results:
        return []

    ranked = []
    for result in eval_results:
        metrics = {
            "faithfulness": result.faithfulness,
            "answer_relevancy": result.answer_relevancy,
            "context_precision": result.context_precision,
            "context_recall": result.context_recall,
        }
        avg_score = sum(metrics.values()) / len(metrics)
        worst_metric, worst_score = min(metrics.items(), key=lambda item: item[1])
        diagnosis, suggested_fix = diagnostic_tree.get(worst_metric, ("Unknown issue", "Review retrieval and prompt logic."))
        ranked.append({
            "question": result.question,
            "worst_metric": worst_metric,
            "score": round(avg_score, 4),
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
            "worst_score": round(worst_score, 4),
        })

    ranked.sort(key=lambda item: item["score"])
    return ranked[:bottom_n]


def save_report(results: dict, failures: list[dict], path: str = "reports/ragas_report.json"):
    """Save evaluation report to JSON. (Đã implement sẵn)"""
    parent_dir = os.path.dirname(path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
