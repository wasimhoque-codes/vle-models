# Student Early Warning System 🎓

A machine learning-powered system for identifying at-risk students and enabling early intervention.

## 🌟 Features

- **Predictive Analytics**: ML models predict student success/failure with high accuracy
- **Interactive Dashboard**: Real-time monitoring via Streamlit web interface
- **Batch Processing**: Automated weekly predictions for all students
- **Risk Categorization**: Students classified as Low/Medium/High risk
- **Multi-Model Support**: Random Forest, Logistic Regression, XGBoost
- **Cloud Deployment**: Free-tier deployment on Streamlit Cloud

## 📊 Dashboard Preview

The dashboard provides:
- Overview metrics (total students, risk distribution)
- Interactive visualizations
- Filterable student lists
- Downloadable reports
- Module-level breakdowns

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd WM9QG-Group-Project

# Install dependencies
pip install -r requirements.txt
```

### 2. Train Models

```bash
# Train models for week 10 (mid-course)
python app/train_models.py --week 10
```

### 3. Generate Predictions

```bash
# Run batch predictions
python app/batch_predict.py
```

### 4. Launch Dashboard

```bash
# Start the Streamlit dashboard
streamlit run app/dashboard.py
```

The dashboard will open at `http://localhost:8501`

## 📁 Project Structure

```
WM9QG-Group-Project/
├── app/
│   ├── dashboard.py          # Streamlit dashboard
│   ├── batch_predict.py      # Batch prediction script
│   ├── train_models.py       # Model training script
│   └── model_manager.py      # Model management utilities
├── data/
│   ├── processed/            # Processed feature store
│   └── predictions/          # Prediction outputs
├── models/                   # Saved ML models
├── notebooks/                # Jupyter notebooks
│   ├── classifier_baseline_refactored.ipynb
│   ├── xgb_classification_refactored.ipynb
│   ├── clustering.ipynb
│   └── regressor.ipynb
├── reports/                  # Analysis outputs
├── .github/workflows/        # CI/CD automation
├── requirements.txt          # Python dependencies
└── README.md
```

## 🌐 Deployment

### Deploy to Streamlit Cloud (Free)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add deployment files"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app/dashboard.py`
   - Click "Deploy"

3. **Your dashboard is live!** 🎉

### Automated Batch Predictions

The project includes GitHub Actions workflow for automated weekly predictions:

- **Schedule**: Every Sunday at midnight UTC
- **Manual Trigger**: Available in GitHub Actions tab
- **Outputs**: Predictions saved as artifacts

## 📈 Model Performance

The system uses multiple models trained on the OULAD dataset:

- **Random Forest**: Best overall performance (ROC-AUC ~0.85)
- **Logistic Regression**: Fast, interpretable baseline
- **XGBoost**: Advanced gradient boosting

Models are trained on weekly snapshots and can predict at any point in the course.

## 🔧 Configuration

### Model Training

Customize model training in `app/train_models.py`:

```python
# Train for different weeks
python app/train_models.py --week 5   # Early prediction
python app/train_models.py --week 10  # Mid-course
python app/train_models.py --week 20  # Late course
```

### Batch Predictions

Modify `app/batch_predict.py` for custom prediction logic:

```python
# Predict for specific week
predictor.run_predictions(week=10)

# Use specific model
predictor.run_predictions(model_name='E4_full_realistic_RandomForest_week_10')
```

## 📊 Data

The system uses the **Open University Learning Analytics Dataset (OULAD)**:

- 25,000+ students
- 7 courses
- 99 engineered features
- Weekly engagement snapshots

### Feature Categories

1. **Engagement Features**: VLE clicks, activity types, resource usage
2. **Demographic Features**: Education level, previous attempts, credits
3. **Assessment Features**: Scores, weights, progress tracking
4. **Temporal Features**: Week-over-week changes, velocity metrics

## 🛠️ Development

### Running Notebooks

```bash
# Start Jupyter Lab
jupyter lab

# Or convert and execute
jupyter nbconvert --to notebook --execute notebooks/classifier_baseline_refactored.ipynb
```

### Testing Locally

```bash
# Test batch predictions
python app/batch_predict.py

# Test dashboard
streamlit run app/dashboard.py
```

## 📝 Usage Examples

### For Instructors

1. **Monitor At-Risk Students**
   - Open dashboard
   - Filter by "High Risk"
   - Download student list
   - Plan interventions

2. **Module Analysis**
   - View risk distribution by module
   - Identify problematic courses
   - Allocate support resources

### For Administrators

1. **Weekly Reports**
   - Automated predictions every Sunday
   - Download CSV reports
   - Track trends over time

2. **Resource Planning**
   - Identify high-risk cohorts
   - Allocate tutoring resources
   - Plan intervention programs
