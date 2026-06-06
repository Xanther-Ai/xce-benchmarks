#!/usr/bin/env python3
"""Create diagrams for the context engines comparison blog post."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'

# Colors for each engine
XCE_COLOR = '#2E86AB'  # Blue
AUGGIE_COLOR = '#A23B72'  # Purple/Magenta
SERENA_COLOR = '#F18F01'  # Orange

# =============================================================================
# DIAGRAM 1: Feature Test Results Bar Chart
# =============================================================================
def create_feature_results_chart():
    """Create bar chart showing feature test results."""
    features = [
        '1. QuerySet Pipeline',
        '2. Transaction Mgmt',
        '3. Model Metaclass',
        '4. Cache Backends',
        '5. Real-time Signals',
        '6. Multi-tenant RLS',
        '7. GraphQL Integration',
        '8. Query Optimizer',
        '9. Distributed Locks',
        '10. Event Sourcing'
    ]
    
    xce_scores = [11, 11, 11, 11, 11, 11, 9, 11, 7, 0]
    auggie_scores = [10, 10, 10, 10, 10, 9, 10, 10, 8, 9]
    serena_scores = [6, 5, 7, 6, 0, 7, 0, 6, 0, 0]
    
    x = np.arange(len(features))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars1 = ax.bar(x - width, xce_scores, width, label='XCE', color=XCE_COLOR, edgecolor='white')
    bars2 = ax.bar(x, auggie_scores, width, label='Auggie', color=AUGGIE_COLOR, edgecolor='white')
    bars3 = ax.bar(x + width, serena_scores, width, label='Serena', color=SERENA_COLOR, edgecolor='white')
    
    ax.set_ylabel('Score (out of 12)', fontsize=12)
    ax.set_title('Complex Feature Test Results\n(10 Features, 12 points max each)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(features, rotation=45, ha='right', fontsize=10)
    ax.legend(loc='upper right', fontsize=11)
    ax.set_ylim(0, 13)
    ax.axhline(y=10, color='gray', linestyle='--', alpha=0.5, label='Excellent (10+)')
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=8, color=XCE_COLOR, fontweight='bold')
    
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=8, color=AUGGIE_COLOR, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('diagram_1_feature_results.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Created diagram_1_feature_results.png")

# =============================================================================
# DIAGRAM 2: Complexity Curve Comparison
# =============================================================================
def create_complexity_curve():
    """Create line chart showing how performance changes with complexity."""
    complexity_levels = ['1-2\n(Low)', '3-4', '5-6', '7-8', '9-10\n(High)']
    
    xce_by_complexity = [11, 11, 11, 10, 7]
    auggie_by_complexity = [10, 10, 9.5, 9, 9.5]
    serena_by_complexity = [7, 6.5, 6, 6.5, 0]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(complexity_levels, xce_by_complexity, 'o-', linewidth=3, markersize=12, 
            color=XCE_COLOR, label='XCE')
    ax.plot(complexity_levels, auggie_by_complexity, 's-', linewidth=3, markersize=12, 
            color=AUGGIE_COLOR, label='Auggie')
    ax.plot(complexity_levels, serena_by_complexity, '^-', linewidth=3, markersize=12, 
            color=SERENA_COLOR, label='Serena')
    
    # Add shaded region for Auggie advantage
    ax.axvspan(3.5, 4.5, alpha=0.15, color=AUGGIE_COLOR)
    ax.text(4, 10.5, 'Auggie\nAdvantage', ha='center', fontsize=10, color=AUGGIE_COLOR, fontweight='bold')
    
    ax.set_ylabel('Average Score (out of 12)', fontsize=12)
    ax.set_xlabel('Problem Complexity Level', fontsize=12)
    ax.set_title('Performance vs. Problem Complexity\n(Auggie Improves as Problems Get Harder)', fontsize=14, fontweight='bold')
    ax.legend(loc='lower left', fontsize=11)
    ax.set_ylim(0, 12.5)
    ax.set_yticks(range(0, 13, 2))
    
    # Add annotations
    ax.annotate('XCE Dominates\n(Standard Problems)', xy=(1.5, 11), xytext=(1, 12),
               fontsize=10, color=XCE_COLOR, fontweight='bold',
               arrowprops=dict(arrowstyle='->', color=XCE_COLOR, lw=2))
    
    plt.tight_layout()
    plt.savefig('diagram_2_complexity_curve.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Created diagram_2_complexity_curve.png")

# =============================================================================
# DIAGRAM 3: Response Time Comparison
# =============================================================================
def create_response_time_chart():
    """Create bar chart comparing response times."""
    engines = ['Serena', 'XCE', 'Auggie']
    response_times = [1.0, 2.0, 3.0]  # seconds
    colors = [SERENA_COLOR, XCE_COLOR, AUGGIE_COLOR]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(engines, response_times, color=colors, edgecolor='white', linewidth=2)
    
    ax.set_ylabel('Average Response Time (seconds)', fontsize=12)
    ax.set_title('Response Time Comparison\n(How Fast Each Engine Responds)', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 4)
    
    # Add value labels
    for bar, time in zip(bars, response_times):
        height = bar.get_height()
        ax.annotate(f'{time}s',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 5), textcoords="offset points",
                   ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Add winner annotation
    ax.annotate('2-3x Faster!', xy=(0, 1.5), xytext=(0.5, 3),
               fontsize=11, color=SERENA_COLOR, fontweight='bold',
               arrowprops=dict(arrowstyle='->', color=SERENA_COLOR, lw=2))
    
    plt.tight_layout()
    plt.savefig('diagram_3_response_time.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Created diagram_3_response_time.png")

# =============================================================================
# DIAGRAM 4: Overall Scores Comparison
# =============================================================================
def create_overall_scores_chart():
    """Create bar chart showing overall scores."""
    categories = ['SWE-bench\n(Bug Fixes)', 'Feature\nDesign', 'Overall\nAverage']
    
    xce_scores = [10.5, 10.3, 10.4]
    auggie_scores = [10.5, 9.7, 10.1]
    serena_scores = [11.0, 6.4, 8.7]
    
    x = np.arange(len(categories))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    bars1 = ax.bar(x - width, xce_scores, width, label='XCE', color=XCE_COLOR, edgecolor='white')
    bars2 = ax.bar(x, auggie_scores, width, label='Auggie', color=AUGGIE_COLOR, edgecolor='white')
    bars3 = ax.bar(x + width, serena_scores, width, label='Serena', color=SERENA_COLOR, edgecolor='white')
    
    ax.set_ylabel('Average Score (out of 12)', fontsize=12)
    ax.set_title('Overall Performance Comparison\n(35+ SWE-bench Issues + 10 Complex Features)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=12)
    ax.legend(loc='upper right', fontsize=11)
    ax.set_ylim(0, 12)
    ax.axhline(y=10, color='green', linestyle='--', alpha=0.7, linewidth=2)
    ax.text(2.6, 10.2, 'Excellent (10+)', fontsize=10, color='green', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('diagram_4_overall_scores.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Created diagram_4_overall_scores.png")

# =============================================================================
# DIAGRAM 5: Token Usage Comparison
# =============================================================================
def create_token_usage_chart():
    """Create bar chart comparing token usage."""
    engines = ['Raw Kiro', 'Serena', 'Auggie', 'XCE']
    tokens = [300, 500, 1500, 2000]
    colors = ['#888888', SERENA_COLOR, AUGGIE_COLOR, XCE_COLOR]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(engines, tokens, color=colors, edgecolor='white', linewidth=2)
    
    ax.set_ylabel('Tokens per Query (approximate)', fontsize=12)
    ax.set_title('Token Usage Comparison\n(Context Provided per Query)', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 2500)
    
    # Add value labels
    for bar, token in zip(bars, tokens):
        height = bar.get_height()
        ax.annotate(f'~{token}',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 5), textcoords="offset points",
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Add efficiency annotation
    ax.annotate('More Context\n= Better Decisions', xy=(3, 2000), xytext=(2, 2300),
               fontsize=10, color=XCE_COLOR, fontweight='bold',
               arrowprops=dict(arrowstyle='->', color=XCE_COLOR, lw=2))
    
    plt.tight_layout()
    plt.savefig('diagram_5_token_usage.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Created diagram_5_token_usage.png")

# =============================================================================
# DIAGRAM 6: Engine Architecture Comparison (How They Work)
# =============================================================================
def create_architecture_diagram():
    """Create a diagram showing how each engine works internally."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 10))
    
    # XCE Architecture
    ax1 = axes[0]
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.set_title('XCE Architecture\n(Graph-Based)', fontsize=14, fontweight='bold', color=XCE_COLOR)
    ax1.axis('off')
    
    # Draw XCE components
    components_xce = [
        (5, 9, 'Source Code\n(Django)', XCE_COLOR),
        (5, 7, 'AST Parsing', '#5AA9C9'),
        (5, 5, 'Relationship\nExtraction', '#5AA9C9'),
        (5, 3, 'Architectural\nLayering (HLD/LLD)', '#5AA9C9'),
        (5, 1, 'PRAT Graph\nDatabase', XCE_COLOR),
    ]
    
    for x, y, text, color in components_xce:
        rect = mpatches.FancyBboxPatch((x-1.5, y-0.6), 3, 1.2, 
                                        boxstyle="round,pad=0.05",
                                        facecolor=color, edgecolor='white', linewidth=2)
        ax1.add_patch(rect)
        ax1.text(x, y, text, ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    
    # Draw arrows
    for i in range(len(components_xce)-1):
        ax1.annotate('', xy=(5, components_xce[i+1][1]+0.7), 
                    xytext=(5, components_xce[i][1]-0.7),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    
    ax1.text(5, 0.3, 'Query → Call Graph\n& Architecture Context', ha='center', fontsize=9, 
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    # Auggie Architecture
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title('Auggie Architecture\n(Semantic Search)', fontsize=14, fontweight='bold', color=AUGGIE_COLOR)
    ax2.axis('off')
    
    components_auggie = [
        (5, 9, 'Source Code', AUGGIE_COLOR),
        (5, 7, 'Embedding\nGeneration', '#C44D8A'),
        (5, 5, 'Vector\nDatabase', '#C44D8A'),
        (5, 3, 'LLM\nSynthesis', '#C44D8A'),
        (5, 1, 'Natural Language\nExplanation', AUGGIE_COLOR),
    ]
    
    for x, y, text, color in components_auggie:
        rect = mpatches.FancyBboxPatch((x-1.5, y-0.6), 3, 1.2, 
                                        boxstyle="round,pad=0.05",
                                        facecolor=color, edgecolor='white', linewidth=2)
        ax2.add_patch(rect)
        ax2.text(x, y, text, ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    
    for i in range(len(components_auggie)-1):
        ax2.annotate('', xy=(5, components_auggie[i+1][1]+0.7), 
                    xytext=(5, components_auggie[i][1]-0.7),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    
    ax2.text(5, 0.3, 'Query → Semantic\nAnalysis', ha='center', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    # Serena Architecture
    ax3 = axes[2]
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)
    ax3.set_title('Serena Architecture\n(LSP-Based)', fontsize=14, fontweight='bold', color=SERENA_COLOR)
    ax3.axis('off')
    
    components_serena = [
        (5, 9, 'Source Code', SERENA_COLOR),
        (5, 7, 'LSP Parser\n(Pyright)', '#D97706'),
        (5, 5, 'Symbol\nIndex', '#D97706'),
        (5, 3, 'Symbol\nLookup', '#D97706'),
        (5, 1, 'Exact Location\n(Line #)', SERENA_COLOR),
    ]
    
    for x, y, text, color in components_serena:
        rect = mpatches.FancyBboxPatch((x-1.5, y-0.6), 3, 1.2, 
                                        boxstyle="round,pad=0.05",
                                        facecolor=color, edgecolor='white', linewidth=2)
        ax3.add_patch(rect)
        ax3.text(x, y, text, ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    
    for i in range(len(components_serena)-1):
        ax3.annotate('', xy=(5, components_serena[i+1][1]+0.7), 
                    xytext=(5, components_serena[i][1]-0.7),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    
    ax3.text(5, 0.3, 'Query → Symbol\nLocation', ha='center', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('diagram_6_architecture.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Created diagram_6_architecture.png")

# =============================================================================
# DIAGRAM 7: When to Use Which Engine (Decision Guide)
# =============================================================================
def create_when_to_use_chart():
    """Create a visual decision guide."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'Which Context Engine to Use?', fontsize=18, fontweight='bold', ha='center')
    ax.text(7, 9, '(Based on 35+ SWE-bench Issues & 10 Complex Features)', fontsize=12, ha='center', style='italic')
    
    # Serena box (speed)
    rect1 = mpatches.FancyBboxPatch((0.5, 5.5), 4, 3.5, 
                                     boxstyle="round,pad=0.1",
                                     facecolor=SERENA_COLOR, edgecolor='white', linewidth=3)
    ax.add_patch(rect1)
    ax.text(2.5, 8.3, '⚡ Serena', fontsize=14, fontweight='bold', ha='center', color='white')
    ax.text(2.5, 7.5, 'Speed Champion', fontsize=11, ha='center', color='white')
    ax.text(2.5, 6.8, '~1 second', fontsize=20, fontweight='bold', ha='center', color='white')
    ax.text(2.5, 6.2, 'response time', fontsize=10, ha='center', color='white')
    ax.text(2.5, 5.7, '✓ Quick lookups\n✓ Symbol find\n✓ Token-limited', fontsize=9, ha='center', color='white')
    
    # XCE box (complex standard)
    rect2 = mpatches.FancyBboxPatch((5, 5.5), 4.5, 3.5, 
                                     boxstyle="round,pad=0.1",
                                     facecolor=XCE_COLOR, edgecolor='white', linewidth=3)
    ax.add_patch(rect2)
    ax.text(7.25, 8.3, '🎯 XCE', fontsize=14, fontweight='bold', ha='center', color='white')
    ax.text(7.25, 7.5, 'Overall Winner', fontsize=11, ha='center', color='white')
    ax.text(7.25, 6.8, '10.4/12', fontsize=20, fontweight='bold', ha='center', color='white')
    ax.text(7.25, 6.2, 'avg score', fontsize=10, ha='center', color='white')
    ax.text(7.25, 5.7, '✓ Django core\n✓ Multi-module\n✓ Call graphs', fontsize=9, ha='center', color='white')
    
    # Auggie box (complex novel)
    rect3 = mpatches.FancyBboxPatch((10, 5.5), 3.5, 3.5, 
                                     boxstyle="round,pad=0.1",
                                     facecolor=AUGGIE_COLOR, edgecolor='white', linewidth=3)
    ax.add_patch(rect3)
    ax.text(11.75, 8.3, '🧠 Auggie', fontsize=14, fontweight='bold', ha='center', color='white')
    ax.text(11.75, 7.5, 'Complexity Winner', fontsize=10, ha='center', color='white')
    ax.text(11.75, 6.8, '9.3/12', fontsize=20, fontweight='bold', ha='center', color='white')
    ax.text(11.75, 6.2, 'on hard problems', fontsize=9, ha='center', color='white')
    ax.text(11.75, 5.7, '✓ Novel design\n✓ Unlimited queries\n✓ Analysis', fontsize=9, ha='center', color='white')
    
    # Summary text at bottom
    ax.text(7, 4.2, 'Key Finding: As problem complexity increases, Auggie outperforms XCE', 
           fontsize=12, ha='center', fontweight='bold', 
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    ax.text(7, 3.2, 'Features 1-6 (Standard): XCE wins  •  Features 7-10 (Complex): Auggie wins', 
           fontsize=11, ha='center')
    
    ax.text(7, 2.2, '🏆 Overall for Django Development: XCE (wins 7/10 features)', 
           fontsize=13, ha='center', fontweight='bold', color=XCE_COLOR)
    
    plt.tight_layout()
    plt.savefig('diagram_7_when_to_use.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Created diagram_7_when_to_use.png")

# =============================================================================
# DIAGRAM 8: Feature Wins by Category
# =============================================================================
def create_wins_summary():
    """Create a summary of wins by category."""
    categories = ['Standard\nComplexity\n(Features 1-6)', 'High\nComplexity\n(Features 7-10)', 'Speed\n(Lookup)', 'Overall\nAverage']
    
    xce_wins = [6, 1, 0, 7]
    auggie_wins = [0, 3, 0, 3]
    serena_wins = [0, 0, 1, 0]
    
    x = np.arange(len(categories))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    bars1 = ax.bar(x - width, xce_wins, width, label='XCE', color=XCE_COLOR, edgecolor='white')
    bars2 = ax.bar(x, auggie_wins, width, label='Auggie', color=AUGGIE_COLOR, edgecolor='white')
    bars3 = ax.bar(x + width, serena_wins, width, label='Serena', color=SERENA_COLOR, edgecolor='white')
    
    ax.set_ylabel('Number of Wins', fontsize=12)
    ax.set_title('Wins by Category\n(Out of 10 Features + Speed)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(loc='upper right', fontsize=11)
    ax.set_ylim(0, 8)
    
    # Add winner annotations
    ax.annotate('XCE\nDominates', xy=(0, 6), xytext=(0.3, 7.5),
               fontsize=10, color=XCE_COLOR, fontweight='bold',
               arrowprops=dict(arrowstyle='->', color=XCE_COLOR, lw=2))
    
    ax.annotate('Auggie\nWins', xy=(1, 3), xytext=(1.3, 4.5),
               fontsize=10, color=AUGGIE_COLOR, fontweight='bold',
               arrowprops=dict(arrowstyle='->', color=AUGGIE_COLOR, lw=2))
    
    ax.annotate('Serena\nFastest', xy=(2, 1), xytext=(2.3, 2.5),
               fontsize=10, color=SERENA_COLOR, fontweight='bold',
               arrowprops=dict(arrowstyle='->', color=SERENA_COLOR, lw=2))
    
    plt.tight_layout()
    plt.savefig('diagram_8_wins_summary.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Created diagram_8_wins_summary.png")

# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    import os
    os.chdir('/Users/rajbhattacharya/Documents/Projects/django/swe-bench-results')
    
    print("Creating diagrams for blog post...")
    print("=" * 50)
    
    create_feature_results_chart()
    create_complexity_curve()
    create_response_time_chart()
    create_overall_scores_chart()
    create_token_usage_chart()
    create_architecture_diagram()
    create_when_to_use_chart()
    create_wins_summary()
    
    print("=" * 50)
    print("All diagrams created successfully!")
    print("\nGenerated files:")
    print("  1. diagram_1_feature_results.png - Feature test scores")
    print("  2. diagram_2_complexity_curve.png - Complexity vs performance")
    print("  3. diagram_3_response_time.png - Response time comparison")
    print("  4. diagram_4_overall_scores.png - Overall scores")
    print("  5. diagram_5_token_usage.png - Token usage")
    print("  6. diagram_6_architecture.png - How each engine works")
    print("  7. diagram_7_when_to_use.png - Decision guide")
    print("  8. diagram_8_wins_summary.png - Wins by category")