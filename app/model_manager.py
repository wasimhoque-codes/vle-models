"""
Model Manager - Handles model loading, saving, and predictions
"""

import pickle
import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelManager:
    """Manages ML models for the Student Early Warning System"""
    
    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize ModelManager
        
        Args:
            models_dir: Directory containing saved models. Defaults to ../models/
        """
        if models_dir is None:
            self.models_dir = Path(__file__).parent.parent / "models"
        else:
            self.models_dir = Path(models_dir)
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_models = {}
        
    def save_model(self, model: Any, name: str, metadata: Optional[Dict] = None):
        """
        Save a trained model with metadata
        
        Args:
            model: Trained sklearn/xgboost model or pipeline
            name: Model name (e.g., 'random_forest_week_10')
            metadata: Optional metadata dict (metrics, features, etc.)
        """
        model_path = self.models_dir / f"{name}.pkl"
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"Saved model to {model_path}")
        
        # Save metadata if provided
        if metadata:
            metadata_path = self.models_dir / f"{name}_metadata.pkl"
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            logger.info(f"Saved metadata to {metadata_path}")
    
    def load_model(self, name: str, use_cache: bool = True) -> Any:
        """
        Load a saved model
        
        Args:
            name: Model name (without .pkl extension)
            use_cache: Whether to use cached model if already loaded
            
        Returns:
            Loaded model
        """
        if use_cache and name in self.loaded_models:
            return self.loaded_models[name]
        
        model_path = self.models_dir / f"{name}.pkl"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        if use_cache:
            self.loaded_models[name] = model
        
        logger.info(f"Loaded model from {model_path}")
        return model
    
    def load_metadata(self, name: str) -> Optional[Dict]:
        """Load model metadata if available"""
        metadata_path = self.models_dir / f"{name}_metadata.pkl"
        
        if not metadata_path.exists():
            return None
        
        with open(metadata_path, 'rb') as f:
            return pickle.load(f)
    
    def list_models(self) -> list:
        """List all available models"""
        models = []
        for path in self.models_dir.glob("*.pkl"):
            if not path.name.endswith("_metadata.pkl"):
                models.append(path.stem)
        return sorted(models)
    
    def predict(self, model_name: str, X: pd.DataFrame) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Make predictions using a loaded model
        
        Args:
            model_name: Name of the model to use
            X: Feature dataframe
            
        Returns:
            Tuple of (predictions, probabilities)
        """
        model = self.load_model(model_name)
        
        predictions = model.predict(X)
        
        # Get probabilities if available
        probabilities = None
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X)
        
        return predictions, probabilities
    
    def predict_risk_level(self, model_name: str, X: pd.DataFrame) -> pd.DataFrame:
        """
        Predict risk levels for students
        
        Args:
            model_name: Name of the model to use
            X: Feature dataframe
            
        Returns:
            DataFrame with predictions and risk levels
        """
        predictions, probabilities = self.predict(model_name, X)
        
        results = pd.DataFrame({
            'prediction': predictions,
        })
        
        if probabilities is not None:
            # Probability of failure (class 0)
            fail_prob = probabilities[:, 0]
            results['fail_probability'] = fail_prob
            
            # Categorize risk levels
            results['risk_level'] = pd.cut(
                fail_prob,
                bins=[0, 0.3, 0.6, 1.0],
                labels=['Low Risk', 'Medium Risk', 'High Risk']
            )
        else:
            results['risk_level'] = results['prediction'].map({
                0: 'High Risk',
                1: 'Low Risk'
            })
        
        return results


def create_model_snapshot(
    df: pd.DataFrame,
    model: Any,
    week: int,
    experiment_name: str,
    model_name: str,
    metrics: Dict[str, float],
    feature_names: list
) -> str:
    """
    Save a model snapshot with full metadata
    
    Args:
        df: Training dataframe
        model: Trained model/pipeline
        week: Week number for this snapshot
        experiment_name: Experiment identifier
        model_name: Model type (e.g., 'RandomForest')
        metrics: Performance metrics dict
        feature_names: List of feature names used
        
    Returns:
        Snapshot name
    """
    manager = ModelManager()
    
    snapshot_name = f"{experiment_name}_{model_name}_week_{week}"
    
    metadata = {
        'week': week,
        'experiment': experiment_name,
        'model_type': model_name,
        'metrics': metrics,
        'features': feature_names,
        'n_samples': len(df),
        'timestamp': pd.Timestamp.now().isoformat()
    }
    
    manager.save_model(model, snapshot_name, metadata)
    
    return snapshot_name


if __name__ == "__main__":
    # Example usage
    manager = ModelManager()
    print("Available models:", manager.list_models())
