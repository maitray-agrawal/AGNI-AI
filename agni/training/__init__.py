"""
AGNI MLOps Training & Model Lifecycle Package
=============================================
Separates offline training, calibration, and validation from online inference.
"""

def train_event_conditioned_model(*args, **kwargs):
    from agni.training.train_forecaster import train_event_conditioned_model as _fn
    return _fn(*args, **kwargs)


def evaluate_model_performance(*args, **kwargs):
    from agni.training.evaluate_forecaster import evaluate_model_performance as _fn
    return _fn(*args, **kwargs)


def run_full_backtest_pipeline(*args, **kwargs):
    from agni.training.backtest import run_full_backtest_pipeline as _fn
    return _fn(*args, **kwargs)


__all__ = [
    "train_event_conditioned_model",
    "evaluate_model_performance",
    "run_full_backtest_pipeline",
]
