# Quick Start Guide 🚀

Get your Student Early Warning System up and running in 5 minutes!

## 🎯 Prerequisites

- Python 3.8+
- Feature store at `data/processed/ews_feature_store.csv`

## ⚡ Quick Setup

### 1. Install Dependencies (1 min)

```bash
pip install streamlit plotly pandas scikit-learn joblib
```

### 2. Train Models (2-3 min)

```bash
python app/train_models.py --week 10
```

### 3. Generate Predictions (30 sec)

```bash
python app/batch_predict.py
```

### 4. Launch Dashboard (10 sec)

```bash
streamlit run app/dashboard.py
```

**Done!** 🎉 Your dashboard is now running at `http://localhost:8501`

---

## 📱 What You'll See

### Dashboard Features

1. **Overview Metrics**
   - Total students
   - Risk distribution (High/Medium/Low)
   - Real-time statistics

2. **Interactive Charts**
   - Risk distribution bar chart
   - Failure probability histogram
   - Module breakdown

3. **Student List**
   - Filter by risk level
   - Filter by module/presentation
   - Download CSV reports

---

## 🌐 Deploy to Cloud (Free)

### Streamlit Cloud

1. Push to GitHub:
   ```bash
   git add .
   git commit -m "Add deployment"
   git push
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io/)

3. Click "New app" → Select repo → Deploy

**Your app is live!** Share the URL with instructors.

---

## 🔄 Weekly Updates

### Automated (GitHub Actions)

- Runs every Sunday automatically
- No manual intervention needed

### Manual

```bash
python app/batch_predict.py
```

Then refresh the dashboard.

---

## 📊 Understanding Risk Levels

- 🔴 **High Risk** (>60% fail probability)
  - Immediate intervention needed
  - Contact student ASAP
  - Provide additional support

- 🟡 **Medium Risk** (30-60% fail probability)
  - Monitor closely
  - Offer optional tutoring
  - Check in weekly

- 🟢 **Low Risk** (<30% fail probability)
  - On track to pass
  - Standard support
  - Encourage continued effort

---

## 🆘 Quick Troubleshooting

### "No predictions found"
```bash
python app/batch_predict.py
```

### "No models found"
```bash
python app/train_models.py --week 10
```

### "Feature store not found"
```bash
# Run data preparation notebook first
jupyter lab notebooks/data_preparation.ipynb
```

---

## 📚 Full Documentation

- **README.md** - Project overview
- **DEPLOYMENT.md** - Complete deployment guide
- **.agent/workflows/deploy.md** - Deployment workflow

---

## 💡 Pro Tips

1. **Best Week to Predict**: Week 10 (mid-course)
   - Enough data for accuracy
   - Time for intervention

2. **Update Frequency**: Weekly
   - Catches students early
   - Allows timely intervention

3. **Focus on High Risk**: 
   - Download filtered list
   - Prioritize outreach
   - Track intervention outcomes

---

## 🎓 Example Workflow

### For Instructors

**Monday Morning:**
1. Open dashboard
2. Filter "High Risk" students
3. Download CSV
4. Send personalized emails
5. Schedule office hours

**Throughout Week:**
1. Monitor medium risk students
2. Check module-specific issues
3. Adjust teaching approach

**Friday:**
1. Review weekly trends
2. Plan next week's interventions
3. Update support resources

---

## 🚀 Next Steps

1. ✅ Set up dashboard
2. ✅ Generate first predictions
3. 📧 Share dashboard URL with team
4. 📅 Schedule weekly reviews
5. 📈 Track intervention success
6. 🔄 Retrain models monthly

---

**Need Help?** Check DEPLOYMENT.md or open a GitHub issue.

**Ready to save students!** 💪
