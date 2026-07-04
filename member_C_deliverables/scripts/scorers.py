from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Protocol

from member_C_deliverables.scripts.metrics import CEFR_ORDER


class CEFRScorer(Protocol):
    def score(self, texts: list[str]) -> list[dict[str, Any]]: ...


class MeaningScorer(Protocol):
    def score_pairs(self, first: list[str], second: list[str]) -> list[float]: ...


class HeuristicCEFRScorer:
    """Deterministic development scorer; never use for reported results."""

    def score(self, texts: list[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for text in texts:
            words = text.split()
            average_length = (
                sum(len(word.strip(".,!?;:")) for word in words) / len(words)
                if words
                else 0.0
            )
            label = "A2" if average_length < 5.3 else "B1"
            results.append(
                {
                    "label": label,
                    "confidence": 0.5,
                    "selected_model": "heuristic-development-only",
                    "checkpoint_probabilities": {},
                }
            )
        return results


class TokenOverlapMeaningScorer:
    """Deterministic development scorer; never use for reported results."""

    def score_pairs(self, first: list[str], second: list[str]) -> list[float]:
        if len(first) != len(second):
            raise ValueError("meaning scorer inputs differ in length")
        scores: list[float] = []
        for left, right in zip(first, second, strict=True):
            left_tokens = set(left.lower().split())
            right_tokens = set(right.lower().split())
            union = left_tokens | right_tokens
            scores.append(
                1.0 if not union else len(left_tokens & right_tokens) / len(union)
            )
        return scores


class HuggingFaceCEFRScorer:
    def __init__(
        self,
        models: list[dict[str, str]],
        *,
        cache_dir: Path,
        batch_size: int = 8,
        device: str = "auto",
    ) -> None:
        if len(models) != 3:
            raise ValueError("official CEFR ensemble requires exactly three models")
        self.models = models
        self.cache_dir = cache_dir
        self.batch_size = batch_size
        self.device = device
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def score(self, texts: list[str]) -> list[dict[str, Any]]:
        per_model = [
            self._score_checkpoint(model_config, texts)
            for model_config in self.models
        ]
        results: list[dict[str, Any]] = []
        for index in range(len(texts)):
            candidates = [
                (model_results[index], model_config["id"])
                for model_results, model_config in zip(
                    per_model, self.models, strict=True
                )
            ]
            selected, selected_model = max(
                candidates, key=lambda item: item[0]["confidence"]
            )
            results.append(
                {
                    "label": selected["label"],
                    "confidence": selected["confidence"],
                    "selected_model": selected_model,
                    "checkpoint_probabilities": {
                        model_id: result["probabilities"]
                        for result, model_id in candidates
                    },
                }
            )
        return results

    def _score_checkpoint(
        self, config: dict[str, str], texts: list[str]
    ) -> list[dict[str, Any]]:
        cached: dict[int, dict[str, Any]] = {}
        missing_indices: list[int] = []
        for index, text in enumerate(texts):
            path = self._cache_path(config, text)
            if path.exists():
                cached[index] = json.loads(path.read_text(encoding="utf-8"))
            else:
                missing_indices.append(index)

        if missing_indices:
            computed = self._run_checkpoint(
                config, [texts[index] for index in missing_indices]
            )
            for index, result in zip(missing_indices, computed, strict=True):
                self._cache_path(config, texts[index]).write_text(
                    json.dumps(result, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                cached[index] = result
        return [cached[index] for index in range(len(texts))]

    def _run_checkpoint(
        self, config: dict[str, str], texts: list[str]
    ) -> list[dict[str, Any]]:
        try:
            import torch
            from transformers import (
                AutoModelForSequenceClassification,
                AutoTokenizer,
            )
        except ImportError as exc:
            raise RuntimeError(
                "neural evaluation requires torch and transformers"
            ) from exc

        tokenizer = AutoTokenizer.from_pretrained(
            config["id"], revision=config["revision"]
        )
        model = AutoModelForSequenceClassification.from_pretrained(
            config["id"], revision=config["revision"]
        )
        resolved_device = _resolve_device(torch, self.device)
        model.to(resolved_device)
        model.eval()
        id_to_label = {
            int(key): _normalize_cefr(value)
            for key, value in model.config.id2label.items()
        }
        results: list[dict[str, Any]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            encoded = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=8192,
                return_tensors="pt",
            )
            encoded = {
                key: value.to(resolved_device) for key, value in encoded.items()
            }
            with torch.inference_mode():
                logits = model(**encoded).logits
                probabilities = torch.softmax(logits, dim=-1).cpu().tolist()
            for vector in probabilities:
                mapped = {
                    id_to_label[index]: float(probability)
                    for index, probability in enumerate(vector)
                }
                label = max(mapped, key=mapped.get)  # type: ignore[arg-type]
                results.append(
                    {
                        "label": label,
                        "confidence": mapped[label],
                        "probabilities": mapped,
                    }
                )
        del model
        return results

    def _cache_path(self, config: dict[str, str], text: str) -> Path:
        key = hashlib.sha256(
            (
                config["id"]
                + "\0"
                + config["revision"]
                + "\0"
                + text
            ).encode()
        ).hexdigest()
        model_dir = self.cache_dir / config["id"].replace("/", "--")
        model_dir.mkdir(parents=True, exist_ok=True)
        return model_dir / f"{key}.json"


class HuggingFaceMeaningScorer:
    def __init__(
        self,
        model: dict[str, str],
        *,
        cache_dir: Path,
        batch_size: int = 8,
        device: str = "auto",
    ) -> None:
        self.model_config = model
        self.cache_dir = cache_dir
        self.batch_size = batch_size
        self.device = device
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._tokenizer: Any = None
        self._model: Any = None
        self._torch: Any = None

    def score_pairs(self, first: list[str], second: list[str]) -> list[float]:
        if len(first) != len(second):
            raise ValueError("meaning scorer inputs differ in length")
        cached: dict[int, float] = {}
        missing: list[int] = []
        for index, (left, right) in enumerate(
            zip(first, second, strict=True)
        ):
            path = self._cache_path(left, right)
            if path.exists():
                cached[index] = float(
                    json.loads(path.read_text(encoding="utf-8"))["score"]
                )
            else:
                missing.append(index)
        if missing:
            computed = self._run_pairs(
                [first[index] for index in missing],
                [second[index] for index in missing],
            )
            for index, score in zip(missing, computed, strict=True):
                self._cache_path(first[index], second[index]).write_text(
                    json.dumps({"score": score}) + "\n", encoding="utf-8"
                )
                cached[index] = score
        return [cached[index] for index in range(len(first))]

    def _run_pairs(self, first: list[str], second: list[str]) -> list[float]:
        if self._model is None:
            self._load()
        resolved_device = _resolve_device(self._torch, self.device)
        results: list[float] = []
        for start in range(0, len(first), self.batch_size):
            left = first[start : start + self.batch_size]
            right = second[start : start + self.batch_size]
            encoded = self._tokenizer(
                left,
                right,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            encoded = {
                key: value.to(resolved_device) for key, value in encoded.items()
            }
            with self._torch.inference_mode():
                logits = self._model(**encoded).logits.squeeze(-1)
            results.extend(
                float(value) for value in logits.reshape(-1).cpu().tolist()
            )
        return results

    def _load(self) -> None:
        try:
            import torch
            from transformers import (
                AutoModelForSequenceClassification,
                AutoTokenizer,
            )
        except ImportError as exc:
            raise RuntimeError(
                "neural evaluation requires torch and transformers"
            ) from exc
        self._torch = torch
        config = self.model_config
        self._tokenizer = AutoTokenizer.from_pretrained(
            config["id"], revision=config["revision"]
        )
        self._model = AutoModelForSequenceClassification.from_pretrained(
            config["id"], revision=config["revision"]
        )
        self._model.to(_resolve_device(torch, self.device))
        self._model.eval()

    def _cache_path(self, first: str, second: str) -> Path:
        config = self.model_config
        key = hashlib.sha256(
            (
                config["id"]
                + "\0"
                + config["revision"]
                + "\0"
                + first
                + "\0"
                + second
            ).encode()
        ).hexdigest()
        return self.cache_dir / f"{key}.json"


def _normalize_cefr(label: Any) -> str:
    normalized = str(label).upper().replace(" ", "").replace("_", "")
    for cefr in CEFR_ORDER:
        if cefr in normalized:
            return cefr
    raise ValueError(f"unrecognized CEFR label: {label!r}")


def _resolve_device(torch: Any, requested: str) -> str:
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"
