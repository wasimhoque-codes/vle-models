"""
Batch Prediction Script
Runs predictions on all students and saves results for dashboard consumption
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.model_manager import ModelManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchPredictor:
    """Handles batch predictions for all students"""
    
    def __init__(self, data_dir: Path, output_dir: Path):
        """
        Initialize BatchPredictor
        
        Args:
            data_dir: Directory containing processed data
            output_dir: Directory to save prediction results
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.model_manager = ModelManager()
        
    def load_feature_store(self) -> pd.DataFrame:
        """Load the EWS feature store"""
        feature_store_path = self.data_dir / "ews_feature_store.csv"
        
        if not feature_store_path.exists():
            raise FileNotFoundError(f"Feature store not found: {feature_store_path}")
        
        logger.info(f"Loading feature store from {feature_store_path}")
        df = pd.read_csv(feature_store_path)
        logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
        
        return df
    
    def prepare_features(self, df: pd.DataFrame, week: int) -> pd.DataFrame:
        """
        Prepare features for a specific week snapshot
        
        Args:
            df: Full feature store
            week: Week number to predict for
            
        Returns:
            Prepared feature dataframe
        """
        # Get latest snapshot for each student up to this week
        snapshot = df[df['week'] <= week].copy()
        snapshot = snapshot.sort_values(['student_id', 'code_module', 'code_presentation', 'week'])
        snapshot = snapshot.groupby(['student_id', 'code_module', 'code_presentation'], as_index=False).tail(1)
        
        logger.info(f"Week {week} snapshot: {len(snapshot):,} students")
        
        return snapshot
    
    def run_predictions(self, week: int = None, model_name: str = None):
        """
        Run batch predictions for all students
        
        Args:
            week: Week to predict for (defaults to latest week)
            model_name: Model to use (defaults to best available model)
        """
        # Load data
        df = self.load_feature_store()
        
        # Determine week
        if week is None:
            week = int(df['week'].max())
        
        logger.info(f"Running predictions for week {week}")
        
        # Prepare features
        snapshot = self.prepare_features(df, week)
        
        # Determine model
        available_models = self.model_manager.list_models()
        
        if not available_models:
            logger.error("No trained models found! Please train models first.")
            logger.info("Run: jupyter nbconvert --to notebook --execute notebooks/classifier_baseline_refactored.ipynb")
            return
        
        if model_name is None:
            # Use the first available model (you can implement smarter selection)
            model_name = available_models[0]
            logger.info(f"Auto-selected model: {model_name}")
        
        # Prepare X (drop identifiers and target)
        identifier_cols = ['student_id', 'code_module', 'code_presentation', 'week']
        leakage_cols = ['date_unregistration', 'final_result', 'target_score', 'target_score_norm', 'target_pass']
        
        # Keep identifiers for results
        identifiers = snapshot[identifier_cols].copy()
        
        # Drop columns for prediction
        drop_cols = identifier_cols + leakage_cols
        X = snapshot.drop(columns=[c for c in drop_cols if c in snapshot.columns], errors='ignore')
        
        logger.info(f"Features shape: {X.shape}")
        
        # Make predictions
        try:
            results = self.model_manager.predict_risk_level(model_name, X)
            
            # Combine with identifiers
            results = pd.concat([identifiers.reset_index(drop=True), results], axis=1)
            
            # Add metadata
            results['prediction_date'] = datetime.now().isoformat()
            results['model_used'] = model_name
            results['week_predicted'] = week
            
            # Save results
            output_path = self.output_dir / f"predictions_week_{week}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            results.to_csv(output_path, index=False)
            logger.info(f"Saved predictions to {output_path}")
            
            # Save latest predictions (for dashboard)
            latest_path = self.output_dir / "predictions_latest.csv"
            results.to_csv(latest_path, index=False)
            logger.info(f"Saved latest predictions to {latest_path}")
            
            # Print summary
            self.print_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def print_summary(self, results: pd.DataFrame):
        """Print prediction summary"""
        logger.info("\n" + "="*60)
        logger.info("PREDICTION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total students: {len(results):,}")
        
        if 'risk_level' in results.columns:
            risk_counts = results['risk_level'].value_counts()
            logger.info("\nRisk Level Distribution:")
            for level, count in risk_counts.items():
                pct = (count / len(results)) * 100
                logger.info(f"  {level}: {count:,} ({pct:.1f}%)")
        
        if 'fail_probability' in results.columns:
            logger.info(f"\nAverage Failure Probability: {results['fail_probability'].mean():.2%}")
            logger.info(f"High Risk Students (>60% fail prob): {(results['fail_probability'] > 0.6).sum():,}")
        
        logger.info("="*60 + "\n")


def main():
    """Main execution function"""
    # Setup paths
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "data" / "processed"
    output_dir = repo_root / "data" / "predictions"
    
    # Create predictor
    predictor = BatchPredictor(data_dir, output_dir)
    
    # Run predictions
    try:
        predictor.run_predictions()
        logger.info("Batch prediction completed successfully!")
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
