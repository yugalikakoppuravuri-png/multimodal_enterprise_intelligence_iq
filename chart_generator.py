"""
Interactive Enterprise Data Visualization Generator
Provides both modern executive light theme and dark theme charts
matching the InsightAI dashboard design.
"""

from typing import Dict, List, Any, Optional
import plotly.graph_objects as go


class EnterpriseChartGenerator:
    """Generates styled Plotly visualizations for InsightAI enterprise dashboard."""

    LIGHT_LAYOUT = dict(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#1e293b", family="Inter, -apple-system, sans-serif"),
        margin=dict(l=30, r=20, t=40, b=30),
        xaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0", tickfont=dict(size=11, color="#64748b")),
        yaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0", tickfont=dict(size=11, color="#64748b"))
    )

    @classmethod
    def create_revenue_comparison_bar(cls) -> go.Figure:
        """
        Creates the 'Revenue Comparison (Q2 vs Q3 2024)' grouped bar chart
        from Panel 3 of the InsightAI dashboard.
        """
        categories = ["Total Revenue", "Domestic", "International"]
        q2_vals = [15.8, 10.4, 5.4]
        q3_vals = [11.1, 8.2, 2.9]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Q2',
            x=categories,
            y=q2_vals,
            marker_color='#2563eb',  # Royal Blue
            text=[f"${v:.1f}M" for v in q2_vals],
            textposition='auto',
            textfont=dict(size=10, color='#ffffff')
        ))

        fig.add_trace(go.Bar(
            name='Q3',
            x=categories,
            y=q3_vals,
            marker_color='#f97316',  # Orange
            text=[f"${v:.1f}M" for v in q3_vals],
            textposition='auto',
            textfont=dict(size=10, color='#ffffff')
        ))

        fig.update_layout(
            barmode='group',
            title=dict(text="Revenue Comparison (Q2 vs Q3 2024)", font=dict(size=13, color='#0f172a', family='Inter')),
            yaxis_title="Revenue ($ Millions)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            height=260,
            **cls.LIGHT_LAYOUT
        )
        return fig

    @classmethod
    def create_market_factors_donut(cls) -> go.Figure:
        """
        Creates the 'Market Factors Contribution' donut chart
        from Panel 3 of the InsightAI dashboard.
        """
        labels = ["Competition", "Customer Preference", "Economic Slowdown", "Supply Chain"]
        values = [35, 25, 20, 20]
        colors = ["#2563eb", "#f97316", "#10b981", "#eab308"]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.45,
            marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
            textinfo='percent',
            textfont=dict(size=11, color='#ffffff'),
            hoverinfo='label+percent'
        )])

        fig.update_layout(
            title=dict(text="Market Factors Contribution", font=dict(size=13, color='#0f172a', family='Inter')),
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=10, color='#475569')),
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(family="Inter, -apple-system, sans-serif"),
            height=240
        )
        return fig

    @classmethod
    def create_mini_q2_q3_chart(cls) -> go.Figure:
        """Creates the compact Q2 vs Q3 Revenue mini-bar in chat visual summary."""
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Q2", "Q3"],
            y=[15.8, 11.1],
            marker_color=["#2563eb", "#f97316"],
            text=["$15.8M", "$11.1M"],
            textposition='inside',
            textfont=dict(color='#ffffff', size=9)
        ))

        fig.add_annotation(
            x="Q3",
            y=11.1,
            text="-12.4%",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowcolor="#ef4444",
            ax=0,
            ay=-25,
            font=dict(color="#ef4444", size=10, family='Inter')
        )

        fig.update_layout(
            title=dict(text="Q2 vs Q3 Revenue", font=dict(size=11, color='#1e293b')),
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            height=130,
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        return fig

    @classmethod
    def create_mini_donut_chart(cls) -> go.Figure:
        """Creates the compact Market Factors Impact mini-donut in chat visual summary."""
        labels = ["Competition", "Preference", "Slowdown", "Supply"]
        values = [35, 25, 20, 20]
        colors = ["#2563eb", "#f97316", "#10b981", "#eab308"]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.45,
            marker=dict(colors=colors),
            textinfo='none',
            hoverinfo='label+percent'
        )])

        fig.update_layout(
            title=dict(text="Market Factors Impact", font=dict(size=11, color='#1e293b')),
            showlegend=False,
            margin=dict(l=5, r=5, t=30, b=5),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            height=130
        )
        return fig

    @classmethod
    def create_quarterly_revenue_chart(cls) -> go.Figure:
        return cls.create_revenue_comparison_bar()

    @classmethod
    def create_regional_breakdown_chart(cls) -> go.Figure:
        return cls.create_revenue_comparison_bar()

    @classmethod
    def create_revenue_variance_waterfall(cls) -> go.Figure:
        return cls.create_market_factors_donut()
