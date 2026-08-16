import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any

# Set dark theme friendly matplotlib style
plt.style.use('dark_background')

def create_band_stats_chart(band_stats: Dict[str, float]) -> plt.Figure:
    """Horizontal bar chart for normalized satellite band metrics."""
    fig, ax = plt.subplots(figsize=(6, 2.5))
    
    metrics = ['Hotspot Ratio', 'Anomaly Score']
    values = [
        band_stats.get('hotspot_ratio', 0.0),
        band_stats.get('anomaly_score', 0.0)
    ]
    
    colors = ['#FF4B4B', '#FF8C00']
    bars = ax.barh(metrics, values, color=colors, height=0.45)
    
    ax.set_xlim(0, 1.0)
    ax.set_xlabel('Ratio / Score (0.0 - 1.0)', fontsize=9, color='#CCCCCC')
    ax.tick_params(axis='both', which='major', labelsize=9, colors='#EEEEEE')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#444444')
    ax.spines['bottom'].set_color('#444444')
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2, f'{width:.2f}', 
                va='center', ha='left', fontsize=9, color='#FFFFFF', fontweight='bold')
                
    fig.tight_layout()
    return fig

def create_confidence_chart(confidence: float) -> plt.Figure:
    """Horizontal gauge/progress bar chart for confidence score."""
    fig, ax = plt.subplots(figsize=(6, 1.8))
    
    ax.barh(['Confidence'], [confidence], color='#00C853', height=0.4)
    ax.barh(['Confidence'], [1.0 - confidence], left=[confidence], color='#333333', height=0.4)
    
    ax.set_xlim(0, 1.0)
    ax.set_xlabel('Model Confidence Level', fontsize=9, color='#CCCCCC')
    ax.tick_params(axis='both', which='major', labelsize=9, colors='#EEEEEE')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#444444')
    ax.spines['bottom'].set_color('#444444')
    
    ax.text(confidence / 2 if confidence > 0.15 else confidence + 0.05, 0, f'{confidence * 100:.1f}%', 
            va='center', ha='center', fontsize=10, color='#FFFFFF', fontweight='bold')
            
    fig.tight_layout()
    return fig
