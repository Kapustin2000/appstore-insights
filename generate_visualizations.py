#!/usr/bin/env python3
"""
Universal visualization generator for app analysis reports
Automatically detects and processes analysis reports from data/ folder
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle
import warnings
import os
import glob
warnings.filterwarnings('ignore')

# Style configuration
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def find_analysis_report():
    """Finds the most recent analysis report in data/ folder"""
    pattern = 'data/*_Complete_Analysis_Report.json'
    reports = glob.glob(pattern)
    
    if not reports:
        raise FileNotFoundError(f"No analysis reports found in data/ folder. Expected pattern: {pattern}")
    
    # Return the most recent file
    latest_report = max(reports, key=os.path.getmtime)
    return latest_report

def load_data(report_path=None):
    """Loads data from JSON file"""
    if report_path is None:
        report_path = find_analysis_report()
    
    print(f"📄 Loading data from: {report_path}")
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_app_info(data):
    """Extracts app information from data"""
    app_name = data.get('report_header', {}).get('app_name', 'Unknown App')
    app_id = data.get('report_header', {}).get('app_id', 'unknown')
    
    # Create output prefix from app name
    output_prefix = app_name.lower().replace(' ', '_').replace(':', '').replace('&', 'and')
    
    return app_name, app_id, output_prefix

def create_sentiment_pie_chart(data, app_name, output_prefix):
    """Creates sentiment distribution pie chart"""
    sentiment = data['sentiment_analysis']['overall_sentiment']
    
    labels = ['Positive', 'Neutral', 'Negative']
    sizes = [sentiment['positive'] * 100, sentiment['neutral'] * 100, sentiment['negative'] * 100]
    colors = ['#2E8B57', '#808080', '#DC143C']
    explode = (0.05, 0, 0.1)  # Highlight negative
    
    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                                     startangle=90, explode=explode, shadow=True)
    
    # Improve appearance
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    ax.set_title(f'{app_name}: User Sentiment Distribution\n(500 Reviews Analyzed)', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Add legend with additional information
    legend_labels = [f'{label}: {size:.1f}%' for label, size in zip(labels, sizes)]
    ax.legend(wedges, legend_labels, title="Sentiment Categories", 
              loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.tight_layout()
    plt.savefig(f'visualizations/{output_prefix}_sentiment_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_rating_distribution_chart(data, app_name, output_prefix):
    """Creates rating distribution bar chart"""
    rating_dist = data['app_overview']['sample_metrics']['rating_distribution']
    
    stars = ['5⭐', '4⭐', '3⭐', '2⭐', '1⭐']
    counts = [rating_dist['5_stars'], rating_dist['4_stars'], rating_dist['3_stars'], 
              rating_dist['2_stars'], rating_dist['1_star']]
    
    colors = ['#2E8B57', '#90EE90', '#FFD700', '#FFA500', '#DC143C']
    
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(stars, counts, color=colors, edgecolor='black', linewidth=1.5)
    
    # Add values on bars
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{count}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    ax.set_title(f'{app_name}: Rating Distribution\n(Sample of 500 Reviews)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Star Rating', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Reviews', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add statistics
    total_reviews = sum(counts)
    mean_rating = data['app_overview']['sample_metrics']['sample_mean_rating']
    ax.text(0.02, 0.98, f'Total Reviews: {total_reviews}\nMean Rating: {mean_rating:.2f}/5.0', 
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(f'visualizations/{output_prefix}_rating_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_issues_importance_chart(data, app_name, output_prefix):
    """Creates horizontal bar chart of issue importance"""
    issues_data = data['critical_issues_analysis']['top_negative_concerns']
    
    issues = [issue['issue'] for issue in issues_data]
    tfidf_scores = [issue['tf_idf_score'] for issue in issues_data]
    frequencies = [float(issue['frequency'].split('%')[0]) for issue in issues_data]
    
    # Create color scheme based on criticality
    colors = ['#DC143C', '#FF6B6B', '#FF8E53', '#FFA500', '#FFD700']
    
    fig, ax = plt.subplots(figsize=(14, 8))
    bars = ax.barh(issues, tfidf_scores, color=colors, edgecolor='black', linewidth=1)
    
    # Add values on bars
    for i, (bar, score, freq) in enumerate(zip(bars, tfidf_scores, frequencies)):
        width = bar.get_width()
        ax.text(width + 0.2, bar.get_y() + bar.get_height()/2, 
                f'{score:.2f}\n({freq}%)', ha='left', va='center', 
                fontweight='bold', fontsize=10)
    
    ax.set_xlabel('TF-IDF Score (Importance)', fontsize=12, fontweight='bold')
    ax.set_title(f'{app_name}: Top Negative Issues by Importance\n(TF-IDF Analysis)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    
    # Add legend
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, edgecolor='black') 
                      for color in colors]
    legend_labels = ['Critical', 'High', 'High', 'High', 'Medium']
    ax.legend(legend_elements, legend_labels, title="Severity Level", 
              loc='lower right')
    
    plt.tight_layout()
    plt.savefig(f'visualizations/{output_prefix}_issues_importance.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_frequency_impact_scatter(data, app_name, output_prefix):
    """Creates scatter plot of frequency vs impact"""
    issues_data = data['critical_issues_analysis']['top_negative_concerns']
    
    frequencies = [float(issue['frequency'].split('%')[0]) for issue in issues_data]
    tfidf_scores = [issue['tf_idf_score'] for issue in issues_data]
    mentions = [issue['total_mentions'] for issue in issues_data]
    issues = [issue['issue'] for issue in issues_data]
    
    # Create scatter plot
    fig, ax = plt.subplots(figsize=(12, 8))
    scatter = ax.scatter(frequencies, tfidf_scores, s=[m*3 for m in mentions], 
                        c=range(len(issues)), cmap='viridis', alpha=0.7, 
                        edgecolors='black', linewidth=1)
    
    # Add labels
    for i, issue in enumerate(issues):
        ax.annotate(issue.replace(' problems', '').replace(' complaints', ''), 
                   (frequencies[i], tfidf_scores[i]), 
                   xytext=(5, 5), textcoords='offset points', 
                   fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Frequency in Negative Reviews (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('TF-IDF Score (Importance)', fontsize=12, fontweight='bold')
    ax.set_title(f'{app_name}: Issue Analysis - Frequency vs Importance\n(Bubble size = Number of mentions)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    # Add color bar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Issue Index', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'visualizations/{output_prefix}_frequency_impact_scatter.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_risk_assessment_heatmap(data, app_name, output_prefix):
    """Creates risk assessment heatmap"""
    risk_data = data['risk_assessment']
    
    # Prepare data
    risks = []
    probabilities = []
    impacts = []
    
    for risk in risk_data['high_risk_factors']:
        risks.append(risk['risk'])
        probabilities.append(risk['probability'])
        impacts.append(risk['impact'])
    
    for risk in risk_data['medium_risk_factors']:
        risks.append(risk['risk'])
        probabilities.append(risk['probability'])
        impacts.append(risk['impact'])
    
    # Convert to numeric values
    prob_map = {'High': 3, 'Medium': 2, 'Low': 1}
    impact_map = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
    
    prob_values = [prob_map[p] for p in probabilities]
    impact_values = [impact_map[i] for i in impacts]
    
    # Create matrix
    matrix = np.array([prob_values, impact_values]).T
    
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto')
    
    # Configure axes
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Probability', 'Impact'])
    ax.set_yticks(range(len(risks)))
    ax.set_yticklabels([r.replace(' ', '\n') for r in risks])
    
    # Add values in cells
    for i in range(len(risks)):
        for j in range(2):
            text = ax.text(j, i, matrix[i, j], ha="center", va="center", 
                          color="black", fontweight='bold')
    
    ax.set_title(f'{app_name}: Risk Assessment Matrix\n(Color: Green=Low Risk, Red=High Risk)', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Add color bar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Risk Level (1=Low, 4=Critical)', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'visualizations/{output_prefix}_risk_assessment.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_action_timeline_chart(data, app_name, output_prefix):
    """Creates action timeline chart"""
    actions = data['actionable_insights']
    
    # Prepare data for timeline
    immediate_actions = actions['immediate_priority_actions']
    medium_actions = actions['medium_term_improvements']
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Colors for different priorities
    colors = ['#DC143C', '#FF6B6B', '#FF8E53', '#FFA500', '#90EE90']
    
    y_pos = 0
    all_actions = []
    
    # Add immediate actions
    for i, action in enumerate(immediate_actions):
        all_actions.append(f"{action['priority']}. {action['issue']}")
        ax.barh(y_pos, 2, left=0, height=0.6, color=colors[i], 
               edgecolor='black', linewidth=1)
        ax.text(1, y_pos, f"{action['timeline']}", ha='left', va='center', 
               fontweight='bold', fontsize=10)
        y_pos += 1
    
    # Add medium-term actions
    for i, action in enumerate(medium_actions):
        all_actions.append(f"{action['priority']}. {action['issue']}")
        ax.barh(y_pos, 4, left=2, height=0.6, color=colors[i+2], 
               edgecolor='black', linewidth=1)
        ax.text(4, y_pos, f"{action['timeline']}", ha='left', va='center', 
               fontweight='bold', fontsize=10)
        y_pos += 1
    
    # Configure chart
    ax.set_yticks(range(len(all_actions)))
    ax.set_yticklabels(all_actions, fontsize=10)
    ax.set_xlabel('Timeline (Weeks)', fontsize=12, fontweight='bold')
    ax.set_title(f'{app_name}: Action Plan Timeline\n(App Improvement Strategy)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, 8)
    ax.grid(axis='x', alpha=0.3)
    
    # Add time markers
    ax.axvline(x=2, color='black', linestyle='--', alpha=0.5)
    ax.text(1, -0.5, 'Immediate\n(1-2 weeks)', ha='center', va='top', 
           fontweight='bold', fontsize=10)
    ax.text(4, -0.5, 'Medium-term\n(1-2 months)', ha='center', va='top', 
           fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'visualizations/{output_prefix}_action_timeline.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_summary_dashboard(data, app_name, output_prefix):
    """Creates summary dashboard with key metrics"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'{app_name} Analysis Dashboard', fontsize=20, fontweight='bold')
    
    # 1. Sentiment pie chart (simplified version)
    sentiment = data['sentiment_analysis']['overall_sentiment']
    ax1.pie([sentiment['positive'], sentiment['negative']], 
           labels=['Positive', 'Negative'], 
           colors=['#2E8B57', '#DC143C'], 
           autopct='%1.1f%%', startangle=90)
    ax1.set_title('Sentiment Overview', fontweight='bold')
    
    # 2. Rating comparison
    official_rating = data['app_overview']['app_store_metrics']['official_rating']
    sample_rating = data['app_overview']['sample_metrics']['sample_mean_rating']
    
    ratings = ['Official\nApp Store', 'Analyzed\nSample']
    values = [official_rating, sample_rating]
    colors = ['#4CAF50', '#FF9800']
    
    bars = ax2.bar(ratings, values, color=colors, edgecolor='black')
    ax2.set_ylabel('Rating (out of 5)')
    ax2.set_title('Rating Comparison', fontweight='bold')
    ax2.set_ylim(0, 5)
    
    for bar, value in zip(bars, values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Top 3 issues
    issues_data = data['critical_issues_analysis']['top_negative_concerns'][:3]
    issues = [issue['issue'][:20] + '...' if len(issue['issue']) > 20 else issue['issue'] 
              for issue in issues_data]
    tfidf_scores = [issue['tf_idf_score'] for issue in issues_data]
    
    ax3.barh(issues, tfidf_scores, color=['#DC143C', '#FF6B6B', '#FF8E53'])
    ax3.set_xlabel('TF-IDF Score')
    ax3.set_title('Top 3 Critical Issues', fontweight='bold')
    
    # 4. Key metrics
    ax4.axis('off')
    metrics_text = f"""
    Key Metrics:
    
    • Total Reviews Analyzed: 500
    • Positive Sentiment: {sentiment['positive']*100:.1f}%
    • Negative Sentiment: {sentiment['negative']*100:.1f}%
    • Official Rating: {official_rating:.2f}/5.0
    • Sample Rating: {sample_rating:.2f}/5.0
    • Total App Store Ratings: 162,790
    • Critical Issues Identified: 5
    • High Priority Actions: 3
    """
    ax4.text(0.1, 0.5, metrics_text, fontsize=12, verticalalignment='center',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(f'visualizations/{output_prefix}_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main function to generate all visualizations"""
    print("🚀 Loading data from analysis report...")
    data = load_data()
    
    # Extract app information
    app_name, app_id, output_prefix = get_app_info(data)
    print(f"📱 Processing app: {app_name} (ID: {app_id})")
    
    # Create visualizations directory if it doesn't exist
    os.makedirs('visualizations', exist_ok=True)
    
    print("📊 Creating visualizations...")
    
    print("  • Sentiment distribution pie chart...")
    create_sentiment_pie_chart(data, app_name, output_prefix)
    
    print("  • Rating distribution chart...")
    create_rating_distribution_chart(data, app_name, output_prefix)
    
    print("  • Issues importance chart...")
    create_issues_importance_chart(data, app_name, output_prefix)
    
    print("  • Frequency vs impact scatter plot...")
    create_frequency_impact_scatter(data, app_name, output_prefix)
    
    print("  • Risk assessment heatmap...")
    create_risk_assessment_heatmap(data, app_name, output_prefix)
    
    print("  • Action timeline chart...")
    create_action_timeline_chart(data, app_name, output_prefix)
    
    print("  • Summary dashboard...")
    create_summary_dashboard(data, app_name, output_prefix)
    
    print("✅ All visualizations created and saved!")
    print(f"\nCreated files for {app_name}:")
    print(f"  • visualizations/{output_prefix}_sentiment_distribution.png")
    print(f"  • visualizations/{output_prefix}_rating_distribution.png") 
    print(f"  • visualizations/{output_prefix}_issues_importance.png")
    print(f"  • visualizations/{output_prefix}_frequency_impact_scatter.png")
    print(f"  • visualizations/{output_prefix}_risk_assessment.png")
    print(f"  • visualizations/{output_prefix}_action_timeline.png")
    print(f"  • visualizations/{output_prefix}_dashboard.png")

if __name__ == "__main__":
    main()
