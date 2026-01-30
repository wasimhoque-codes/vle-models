"""
Student Early Warning System - Interactive Dashboard
Streamlit application for instructors and administrators
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.model_manager import ModelManager

# Page configuration
st.set_page_config(
    page_title="Student Early Warning System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .risk-high {
        color: #ef4444;
        font-weight: 600;
    }
    .risk-medium {
        color: #f59e0b;
        font-weight: 600;
    }
    .risk-low {
        color: #10b981;
        font-weight: 600;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_predictions():
    """Load latest predictions"""
    predictions_path = Path(__file__).parent.parent / "data" / "predictions" / "predictions_latest.csv"
    
    if not predictions_path.exists():
        return None
    
    return pd.read_csv(predictions_path)


@st.cache_data
def load_feature_store():
    """Load feature store for additional context"""
    feature_store_path = Path(__file__).parent.parent / "data" / "processed" / "ews_feature_store.csv"
    
    if not feature_store_path.exists():
        return None
    
    return pd.read_csv(feature_store_path)


def render_header():
    """Render dashboard header"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<h1 class="main-header">🎓 Student Early Warning System</h1>', unsafe_allow_html=True)
        st.markdown("**Real-time monitoring and intervention for at-risk students**")
    
    with col2:
        st.image("https://img.icons8.com/fluency/96/000000/student-center.png", width=80)


def render_metrics(df: pd.DataFrame):
    """Render key metrics"""
    st.markdown("### 📊 Overview Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_students = len(df)
    
    if 'risk_level' in df.columns:
        high_risk = len(df[df['risk_level'] == 'High Risk'])
        medium_risk = len(df[df['risk_level'] == 'Medium Risk'])
        low_risk = len(df[df['risk_level'] == 'Low Risk'])
    else:
        high_risk = len(df[df['prediction'] == 0])
        medium_risk = 0
        low_risk = len(df[df['prediction'] == 1])
    
    with col1:
        st.metric(
            label="Total Students",
            value=f"{total_students:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="High Risk",
            value=f"{high_risk:,}",
            delta=f"{(high_risk/total_students*100):.1f}%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Medium Risk",
            value=f"{medium_risk:,}",
            delta=f"{(medium_risk/total_students*100):.1f}%",
            delta_color="off"
        )
    
    with col4:
        st.metric(
            label="Low Risk",
            value=f"{low_risk:,}",
            delta=f"{(low_risk/total_students*100):.1f}%",
            delta_color="normal"
        )


def render_risk_distribution(df: pd.DataFrame):
    """Render risk distribution chart"""
    st.markdown("### 📈 Risk Distribution")
    
    if 'risk_level' in df.columns:
        risk_counts = df['risk_level'].value_counts().reset_index()
        risk_counts.columns = ['Risk Level', 'Count']
        
        # Define colors
        color_map = {
            'High Risk': '#ef4444',
            'Medium Risk': '#f59e0b',
            'Low Risk': '#10b981'
        }
        
        fig = px.bar(
            risk_counts,
            x='Risk Level',
            y='Count',
            color='Risk Level',
            color_discrete_map=color_map,
            text='Count'
        )
        
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="",
            yaxis_title="Number of Students",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Risk level data not available")


def render_module_breakdown(df: pd.DataFrame):
    """Render breakdown by module"""
    st.markdown("### 📚 Risk by Module")
    
    if 'code_module' in df.columns and 'risk_level' in df.columns:
        module_risk = df.groupby(['code_module', 'risk_level']).size().reset_index(name='count')
        
        fig = px.bar(
            module_risk,
            x='code_module',
            y='count',
            color='risk_level',
            color_discrete_map={
                'High Risk': '#ef4444',
                'Medium Risk': '#f59e0b',
                'Low Risk': '#10b981'
            },
            barmode='stack',
            text='count'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Module",
            yaxis_title="Number of Students",
            legend_title="Risk Level",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Module breakdown not available")


def render_student_list(df: pd.DataFrame):
    """Render filterable student list"""
    st.markdown("### 👥 Student Details")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'risk_level' in df.columns:
            risk_filter = st.multiselect(
                "Filter by Risk Level",
                options=['High Risk', 'Medium Risk', 'Low Risk'],
                default=['High Risk']
            )
        else:
            risk_filter = None
    
    with col2:
        if 'code_module' in df.columns:
            modules = ['All'] + sorted(df['code_module'].unique().tolist())
            module_filter = st.selectbox("Filter by Module", modules)
        else:
            module_filter = 'All'
    
    with col3:
        if 'code_presentation' in df.columns:
            presentations = ['All'] + sorted(df['code_presentation'].unique().tolist())
            presentation_filter = st.selectbox("Filter by Presentation", presentations)
        else:
            presentation_filter = 'All'
    
    # Apply filters
    filtered_df = df.copy()
    
    if risk_filter and 'risk_level' in df.columns:
        filtered_df = filtered_df[filtered_df['risk_level'].isin(risk_filter)]
    
    if module_filter != 'All' and 'code_module' in df.columns:
        filtered_df = filtered_df[filtered_df['code_module'] == module_filter]
    
    if presentation_filter != 'All' and 'code_presentation' in df.columns:
        filtered_df = filtered_df[filtered_df['code_presentation'] == presentation_filter]
    
    # Display count
    st.markdown(f"**Showing {len(filtered_df):,} students**")
    
    # Prepare display columns
    display_cols = ['student_id']
    
    if 'code_module' in filtered_df.columns:
        display_cols.append('code_module')
    if 'code_presentation' in filtered_df.columns:
        display_cols.append('code_presentation')
    if 'risk_level' in filtered_df.columns:
        display_cols.append('risk_level')
    if 'fail_probability' in filtered_df.columns:
        display_cols.append('fail_probability')
    if 'prediction' in filtered_df.columns:
        display_cols.append('prediction')
    
    # Format dataframe
    display_df = filtered_df[display_cols].copy()
    
    if 'fail_probability' in display_df.columns:
        display_df['fail_probability'] = display_df['fail_probability'].apply(lambda x: f"{x:.1%}")
    
    if 'prediction' in display_df.columns:
        display_df['prediction'] = display_df['prediction'].map({0: 'Fail', 1: 'Pass'})
    
    # Sort by risk
    if 'fail_probability' in filtered_df.columns:
        display_df = display_df.sort_values('fail_probability', ascending=False)
    
    # Display table
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name=f"at_risk_students_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


def render_probability_distribution(df: pd.DataFrame):
    """Render failure probability distribution"""
    if 'fail_probability' not in df.columns:
        return
    
    st.markdown("### 📊 Failure Probability Distribution")
    
    fig = px.histogram(
        df,
        x='fail_probability',
        nbins=50,
        color_discrete_sequence=['#667eea']
    )
    
    fig.update_layout(
        height=300,
        xaxis_title="Failure Probability",
        yaxis_title="Number of Students",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    # Add risk threshold lines
    fig.add_vline(x=0.3, line_dash="dash", line_color="green", annotation_text="Low Risk")
    fig.add_vline(x=0.6, line_dash="dash", line_color="orange", annotation_text="High Risk")
    
    st.plotly_chart(fig, use_container_width=True)


def main():
    """Main dashboard function"""
    render_header()
    
    # Load data
    with st.spinner("Loading predictions..."):
        predictions = load_predictions()
    
    if predictions is None:
        st.error("⚠️ No predictions found!")
        st.info("""
        **To generate predictions:**
        1. Train models by running the classifier notebook
        2. Run batch predictions: `python app/batch_predict.py`
        3. Refresh this dashboard
        """)
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        if 'prediction_date' in predictions.columns:
            st.info(f"**Last Updated:** {predictions['prediction_date'].iloc[0][:10]}")
        
        if 'week_predicted' in predictions.columns:
            st.info(f"**Week:** {predictions['week_predicted'].iloc[0]}")
        
        if 'model_used' in predictions.columns:
            st.info(f"**Model:** {predictions['model_used'].iloc[0]}")
        
        st.markdown("---")
        
        st.markdown("### 🔄 Actions")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📖 About")
        st.markdown("""
        This dashboard provides real-time insights into student performance 
        and identifies at-risk students for early intervention.
        
        **Risk Levels:**
        - 🔴 **High Risk**: >60% failure probability
        - 🟡 **Medium Risk**: 30-60% failure probability  
        - 🟢 **Low Risk**: <30% failure probability
        """)
    
    # Main content
    render_metrics(predictions)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_risk_distribution(predictions)
    
    with col2:
        render_probability_distribution(predictions)
    
    st.markdown("---")
    
    render_module_breakdown(predictions)
    
    st.markdown("---")
    
    render_student_list(predictions)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Student Early Warning System v1.0 | Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
