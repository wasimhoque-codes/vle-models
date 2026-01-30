# Deployment Guide 🚀

Complete guide for deploying the Student Early Warning System.

## Table of Contents

1. [Local Deployment](#local-deployment)
2. [Cloud Deployment (Streamlit Cloud)](#cloud-deployment)
3. [Automated Batch Processing](#automated-batch-processing)
4. [Troubleshooting](#troubleshooting)

---

## Local Deployment

### Prerequisites

- Python 3.8 or higher
- Git
- 2GB+ RAM
- Trained models or raw data to train models

### Step-by-Step

#### 1. Clone and Setup

```bash
# Clone repository
git clone <your-repo-url>
cd WM9QG-Group-Project

# Run setup script
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Prepare Data

Ensure you have the feature store:

```bash
# Check if feature store exists
ls data/processed/ews_feature_store.csv
```

If not, run the data preparation notebook:

```bash
jupyter lab notebooks/data_preparation.ipynb
```

#### 3. Train Models

```bash
# Train models for week 10 (recommended)
python app/train_models.py --week 10

# Or train for multiple weeks
python app/train_models.py --week 5
python app/train_models.py --week 15
python app/train_models.py --week 20
```

Expected output:
```
Training models for week 10...
Loaded 579,438 rows

Training E4_full_realistic | RandomForest...
  Accuracy: 0.892
  F1: 0.901
  ROC-AUC: 0.945
  ✓ Saved as: E4_full_realistic_RandomForest_week_10
```

#### 4. Generate Predictions

```bash
python app/batch_predict.py
```

Expected output:
```
Loading feature store from data/processed/ews_feature_store.csv
Loaded 579,438 rows, 99 columns
Week 38 snapshot: 25,516 students
...
Saved predictions to data/predictions/predictions_latest.csv

PREDICTION SUMMARY
Total students: 25,516
Risk Level Distribution:
  Low Risk: 18,234 (71.5%)
  Medium Risk: 4,512 (17.7%)
  High Risk: 2,770 (10.9%)
```

#### 5. Launch Dashboard

```bash
streamlit run app/dashboard.py
```

The dashboard will open at `http://localhost:8501`

---

## Cloud Deployment

### Streamlit Cloud (Free Tier)

#### Prerequisites

- GitHub account
- Trained models (or data to train them)
- Repository pushed to GitHub

#### Deployment Steps

##### 1. Prepare Repository

```bash
# Ensure all files are committed
git add .
git commit -m "Prepare for deployment"
git push origin main
```

##### 2. Handle Large Files

Models may be too large for GitHub. Options:

**Option A: Git LFS (Recommended)**

```bash
# Install Git LFS
git lfs install

# Track model files
git lfs track "models/*.pkl"
git add .gitattributes
git commit -m "Add Git LFS tracking"
git push
```

**Option B: Cloud Storage**

Store models in Google Drive/Dropbox and download in app:

```python
# Add to app/dashboard.py
import gdown

@st.cache_resource
def download_models():
    # Download from Google Drive
    gdown.download(
        'https://drive.google.com/uc?id=YOUR_FILE_ID',
        'models/model.pkl',
        quiet=False
    )
```

**Option C: Train on First Run**

Add to `app/dashboard.py`:

```python
if not Path("models").exists() or not list(Path("models").glob("*.pkl")):
    st.warning("Training models on first run...")
    import subprocess
    subprocess.run(["python", "app/train_models.py", "--week", "10"])
```

##### 3. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click **"New app"**
3. Select your GitHub repository
4. Configure:
   - **Branch**: `main`
   - **Main file path**: `app/dashboard.py`
   - **Python version**: 3.10
5. Click **"Deploy"**

##### 4. Monitor Deployment

- Check deployment logs for errors
- First deployment may take 5-10 minutes
- App will auto-update on git push

#### Streamlit Cloud Settings

In your Streamlit Cloud dashboard:

- **Secrets**: Add any API keys or credentials
- **Resources**: Free tier includes 1GB RAM
- **Custom domain**: Available on paid plans

---

## Automated Batch Processing

### GitHub Actions (Free)

The repository includes a GitHub Actions workflow for automated weekly predictions.

#### Setup

1. **Enable GitHub Actions**
   - Go to repository Settings → Actions → General
   - Enable "Allow all actions and reusable workflows"

2. **Verify Workflow File**
   - Check `.github/workflows/batch_predict.yml` exists
   - Workflow runs every Sunday at midnight UTC

3. **Manual Trigger**
   - Go to Actions tab
   - Select "Weekly Batch Predictions"
   - Click "Run workflow"

#### Workflow Features

- Runs weekly automatically
- Can be triggered manually
- Saves predictions as artifacts
- Optionally commits results to repo

#### Customization

Edit `.github/workflows/batch_predict.yml`:

```yaml
# Change schedule
on:
  schedule:
    - cron: '0 0 * * 1'  # Every Monday instead of Sunday

# Add notifications
- name: Send notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Alternative: Cron Job (Self-Hosted)

For on-premise deployment:

```bash
# Edit crontab
crontab -e

# Add weekly job (Sundays at midnight)
0 0 * * 0 cd /path/to/project && /path/to/.venv/bin/python app/batch_predict.py
```

---

## Troubleshooting

### Common Issues

#### 1. "No module named 'streamlit'"

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. "Feature store not found"

**Solution:**
```bash
# Run data preparation notebook
jupyter nbconvert --to notebook --execute notebooks/data_preparation.ipynb
```

#### 3. "No trained models found"

**Solution:**
```bash
# Train models
python app/train_models.py --week 10
```

#### 4. Dashboard shows "No predictions found"

**Solution:**
```bash
# Generate predictions
python app/batch_predict.py

# Verify file exists
ls data/predictions/predictions_latest.csv
```

#### 5. Streamlit Cloud deployment fails

**Possible causes:**

- **Large files**: Use Git LFS or cloud storage
- **Memory limit**: Reduce model size or upgrade plan
- **Missing dependencies**: Check `requirements.txt`

**Debug steps:**
1. Check deployment logs in Streamlit Cloud
2. Test locally first: `streamlit run app/dashboard.py`
3. Verify all files are committed and pushed

#### 6. Predictions are outdated

**Solution:**
```bash
# Re-run batch predictions
python app/batch_predict.py

# Or trigger GitHub Action manually
```

### Performance Optimization

#### For Large Datasets

```python
# In app/batch_predict.py, add sampling
snapshot = snapshot.sample(frac=0.1)  # Use 10% for testing
```

#### For Faster Dashboard

```python
# In app/dashboard.py, increase cache
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_predictions():
    ...
```

### Getting Help

1. Check logs:
   ```bash
   # Local logs
   streamlit run app/dashboard.py --logger.level=debug
   
   # Batch prediction logs
   python app/batch_predict.py 2>&1 | tee batch.log
   ```

2. GitHub Issues: Open an issue with:
   - Error message
   - Steps to reproduce
   - Environment details

---

## Production Checklist

Before deploying to production:

- [ ] Models trained and validated
- [ ] Predictions generated successfully
- [ ] Dashboard tested locally
- [ ] All dependencies in `requirements.txt`
- [ ] Sensitive data removed from repo
- [ ] Git LFS configured for large files
- [ ] GitHub Actions workflow tested
- [ ] Documentation updated
- [ ] Backup strategy in place
- [ ] Monitoring/alerting configured

---

## Next Steps

After successful deployment:

1. **Monitor Performance**
   - Track prediction accuracy
   - Monitor dashboard usage
   - Collect user feedback

2. **Iterate and Improve**
   - Retrain models with new data
   - Add new features
   - Enhance visualizations

3. **Scale Up**
   - Consider paid Streamlit tier for more resources
   - Implement caching strategies
   - Optimize model inference

---

**Happy Deploying! 🎉**
