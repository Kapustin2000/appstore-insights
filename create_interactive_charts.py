#!/usr/bin/env python3
"""
Create interactive charts using Plotly
Universal tool for app analysis reports
"""

import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import os
import glob

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

def create_interactive_sentiment_chart(data, app_name, output_prefix):
    """Creates interactive sentiment pie chart"""
    sentiment = data['sentiment_analysis']['overall_sentiment']
    
    fig = go.Figure(data=[go.Pie(
        labels=['Positive', 'Neutral', 'Negative'],
        values=[sentiment['positive'] * 100, sentiment['neutral'] * 100, sentiment['negative'] * 100],
        hole=0.3,
        marker_colors=['#2E8B57', '#808080', '#DC143C'],
        textinfo='label+percent',
        textfont_size=14,
        hovertemplate='<b>%{label}</b><br>Percentage: %{percent}<br>Value: %{value:.1f}%<extra></extra>'
    )])
    
    fig.update_layout(
        title={
            'text': f'{app_name}: User Sentiment Distribution<br><sub>Interactive Analysis of 500 Reviews</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        annotations=[dict(text='Sentiment<br>Analysis', x=0.5, y=0.5, font_size=16, showarrow=False)],
        showlegend=True,
        height=600
    )
    
    fig.write_html(f'visualizations/{output_prefix}_sentiment_interactive.html')
    return fig

def create_interactive_issues_chart(data, app_name, output_prefix):
    """Creates interactive issues chart"""
    issues_data = data['critical_issues_analysis']['top_negative_concerns']
    
    df = pd.DataFrame(issues_data)
    df['frequency_num'] = df['frequency'].str.extract('(\d+)').astype(int)
    
    fig = go.Figure(data=[
        go.Bar(
            y=df['issue'],
            x=df['tf_idf_score'],
            orientation='h',
            marker_color=['#DC143C', '#FF6B6B', '#FF8E53', '#FFA500', '#FFD700'],
            text=[f"Score: {score:.2f}<br>Frequency: {freq}%" 
                  for score, freq in zip(df['tf_idf_score'], df['frequency_num'])],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>TF-IDF Score: %{x:.2f}<br>Frequency: %{customdata}%<extra></extra>',
            customdata=df['frequency_num']
        )
    ])
    
    fig.update_layout(
        title={
            'text': f'{app_name}: Top Negative Issues by Importance<br><sub>TF-IDF Analysis with Frequency Data</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='TF-IDF Score (Importance)',
        yaxis_title='Issues',
        height=500,
        hovermode='closest'
    )
    
    fig.write_html(f'visualizations/{output_prefix}_issues_interactive.html')
    return fig

def create_interactive_scatter_plot(data, app_name, output_prefix):
    """Creates interactive scatter plot"""
    issues_data = data['critical_issues_analysis']['top_negative_concerns']
    
    frequencies = [float(issue['frequency'].split('%')[0]) for issue in issues_data]
    tfidf_scores = [issue['tf_idf_score'] for issue in issues_data]
    mentions = [issue['total_mentions'] for issue in issues_data]
    issues = [issue['issue'] for issue in issues_data]
    severities = [issue['severity'] for issue in issues_data]
    
    # Create DataFrame
    df = pd.DataFrame({
        'Issue': issues,
        'Frequency': frequencies,
        'TF-IDF_Score': tfidf_scores,
        'Mentions': mentions,
        'Severity': severities
    })
    
    # Color scheme for severity
    color_map = {'Critical': '#DC143C', 'High': '#FF6B6B', 'Medium': '#FFA500'}
    colors = [color_map[sev] for sev in severities]
    
    fig = go.Figure(data=go.Scatter(
        x=df['Frequency'],
        y=df['TF-IDF_Score'],
        mode='markers+text',
        marker=dict(
            size=df['Mentions'] * 2,
            color=colors,
            opacity=0.7,
            line=dict(width=2, color='black')
        ),
        text=df['Issue'],
        textposition='top center',
        textfont=dict(size=10),
        hovertemplate='<b>%{text}</b><br>' +
                     'Frequency: %{x}%<br>' +
                     'TF-IDF Score: %{y:.2f}<br>' +
                     'Mentions: %{marker.size}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'{app_name}: Issue Analysis - Frequency vs Importance<br><sub>Bubble size represents number of mentions</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='Frequency in Negative Reviews (%)',
        yaxis_title='TF-IDF Score (Importance)',
        height=600,
        hovermode='closest'
    )
    
    fig.write_html(f'visualizations/{output_prefix}_scatter_interactive.html')
    return fig

def create_interactive_dashboard(data, app_name, output_prefix):
    """Creates interactive dashboard"""
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Sentiment Distribution', 'Rating Comparison', 
                       'Top Issues', 'Key Metrics'),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "table"}]]
    )
    
    # 1. Sentiment pie chart
    sentiment = data['sentiment_analysis']['overall_sentiment']
    fig.add_trace(
        go.Pie(
            labels=['Positive', 'Neutral', 'Negative'],
            values=[sentiment['positive'] * 100, sentiment['neutral'] * 100, sentiment['negative'] * 100],
            marker_colors=['#2E8B57', '#808080', '#DC143C'],
            name="Sentiment"
        ),
        row=1, col=1
    )
    
    # 2. Rating comparison
    official_rating = data['app_overview']['app_store_metrics']['official_rating']
    sample_rating = data['app_overview']['sample_metrics']['sample_mean_rating']
    
    fig.add_trace(
        go.Bar(
            x=['Official App Store', 'Analyzed Sample'],
            y=[official_rating, sample_rating],
            marker_color=['#4CAF50', '#FF9800'],
            name="Ratings",
            text=[f'{official_rating:.2f}', f'{sample_rating:.2f}'],
            textposition='auto'
        ),
        row=1, col=2
    )
    
    # 3. Top 3 issues
    issues_data = data['critical_issues_analysis']['top_negative_concerns'][:3]
    issues = [issue['issue'][:15] + '...' if len(issue['issue']) > 15 else issue['issue'] 
              for issue in issues_data]
    tfidf_scores = [issue['tf_idf_score'] for issue in issues_data]
    
    fig.add_trace(
        go.Bar(
            y=issues,
            x=tfidf_scores,
            orientation='h',
            marker_color=['#DC143C', '#FF6B6B', '#FF8E53'],
            name="Issues",
            text=[f'{score:.1f}' for score in tfidf_scores],
            textposition='auto'
        ),
        row=2, col=1
    )
    
    # 4. Key metrics table
    metrics_data = [
        ['Total Reviews Analyzed', '500'],
        ['Positive Sentiment', f"{sentiment['positive']*100:.1f}%"],
        ['Negative Sentiment', f"{sentiment['negative']*100:.1f}%"],
        ['Official Rating', f"{official_rating:.2f}/5.0"],
        ['Sample Rating', f"{sample_rating:.2f}/5.0"],
        ['Total App Store Ratings', '162,790'],
        ['Critical Issues', '5'],
        ['High Priority Actions', '3']
    ]
    
    fig.add_trace(
        go.Table(
            header=dict(values=['Metric', 'Value'], fill_color='lightblue'),
            cells=dict(values=list(zip(*metrics_data)), fill_color='white')
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title={
            'text': f'{app_name} Analysis Dashboard<br><sub>Interactive Overview</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        height=800,
        showlegend=False
    )
    
    fig.write_html(f'visualizations/{output_prefix}_interactive_dashboard.html')
    return fig

def create_timeline_chart(data, app_name, output_prefix):
    """Creates interactive timeline chart"""
    actions = data['actionable_insights']
    
    # Prepare data
    immediate_actions = actions['immediate_priority_actions']
    medium_actions = actions['medium_term_improvements']
    
    # Create data for Gantt chart
    tasks = []
    for action in immediate_actions:
        tasks.append({
            'Task': f"{action['priority']}. {action['issue']}",
            'Start': 0,
            'Finish': 2,
            'Resource': 'Immediate',
            'Description': action['action']
        })
    
    for action in medium_actions:
        tasks.append({
            'Task': f"{action['priority']}. {action['issue']}",
            'Start': 2,
            'Finish': 8,
            'Resource': 'Medium-term',
            'Description': action['action']
        })
    
    df = pd.DataFrame(tasks)
    
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", 
                     color="Resource", title="Action Plan Timeline")
    
    fig.update_layout(
        title={
            'text': f'{app_name}: Improvement Action Plan<br><sub>Timeline Visualization</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        height=500,
        hovermode='closest'
    )
    
    # Add hover information
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>' +
                     'Duration: %{x[1] - x[0]} weeks<br>' +
                     'Type: %{customdata[0]}<br>' +
                     'Action: %{customdata[1]}<br>' +
                     '<extra></extra>',
        customdata=df[['Resource', 'Description']].values
    )
    
    fig.write_html(f'visualizations/{output_prefix}_timeline_interactive.html')
    return fig

def main():
    """Main function to create interactive charts"""
    print("🚀 Loading data from analysis report...")
    data = load_data()
    
    # Extract app information
    app_name, app_id, output_prefix = get_app_info(data)
    print(f"📱 Processing app: {app_name} (ID: {app_id})")
    
    # Create visualizations directory if it doesn't exist
    os.makedirs('visualizations', exist_ok=True)
    
    print("📊 Creating interactive visualizations...")
    
    print("  • Interactive sentiment pie chart...")
    create_interactive_sentiment_chart(data, app_name, output_prefix)
    
    print("  • Interactive issues chart...")
    create_interactive_issues_chart(data, app_name, output_prefix)
    
    print("  • Interactive scatter plot...")
    create_interactive_scatter_plot(data, app_name, output_prefix)
    
    print("  • Interactive dashboard...")
    create_interactive_dashboard(data, app_name, output_prefix)
    
    print("  • Interactive timeline chart...")
    create_timeline_chart(data, app_name, output_prefix)
    
    print("✅ All interactive charts created!")
    print(f"\nCreated HTML files for {app_name}:")
    print(f"  • visualizations/{output_prefix}_sentiment_interactive.html")
    print(f"  • visualizations/{output_prefix}_issues_interactive.html")
    print(f"  • visualizations/{output_prefix}_scatter_interactive.html")
    print(f"  • visualizations/{output_prefix}_interactive_dashboard.html")
    print(f"  • visualizations/{output_prefix}_timeline_interactive.html")
    print("\nOpen HTML files in browser for interactive viewing!")

if __name__ == "__main__":
    main()
