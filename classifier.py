"""Small, synthetic-data category classifier for the assessment demonstration."""

from collections.abc import Callable, Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline


def _make_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )


def train_category_classifier(examples: Sequence[tuple]) -> Pipeline:
    """Train on tuple field 6 (problem statement) and field 2 (category)."""
    statements = [example[5] for example in examples]
    categories = [example[1] for example in examples]
    return _make_pipeline().fit(statements, categories)


def cross_validate_categories(
    examples: Sequence[tuple], rule_predictor: Callable[[str], str | None]
) -> dict[str, float]:
    """Compare rule predictions and out-of-fold ML predictions on the same 5 folds."""
    statements = [example[5] for example in examples]
    categories = [example[1] for example in examples]
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    ml_predictions: list[str | None] = [None] * len(examples)

    for train_indices, test_indices in folds.split(statements, categories):
        model = _make_pipeline()
        model.fit([statements[i] for i in train_indices], [categories[i] for i in train_indices])
        for index, prediction in zip(test_indices, model.predict([statements[i] for i in test_indices])):
            ml_predictions[index] = str(prediction)

    rule_predictions = [rule_predictor(statement) or "Unrecognized" for statement in statements]
    return {
        "rule_accuracy": float(accuracy_score(categories, rule_predictions)),
        "ml_accuracy": float(accuracy_score(categories, ml_predictions)),
    }


def predict_category(model: Pipeline, statement: str) -> tuple[str, float]:
    """Return the predicted category and its maximum class probability."""
    probabilities = model.predict_proba([statement])[0]
    best_index = int(probabilities.argmax())
    category = str(model.classes_[best_index])
    return category, float(probabilities[best_index])
