from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..infrastructure import GitHubClient
from ..domain import ReportGenerator

from ..infrastructure.visualization import (
    create_pr_size_chart,
    create_review_time_chart,
    create_contributor_heatmap,
)
from ..domain.service.velocity import create_velocity_charts

app = FastAPI(title="GitHub Report Generator API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ReportRequest(BaseModel):
    repo_name: str
    days: Optional[int] = 30
    github_token: Optional[str] = None


class ReportResponse(BaseModel):
    report: Dict
    charts: Dict[str, Dict]


@app.get("/")
async def root():
    return {
        "name": "GitHub Report Generator API",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.post("/api/report")
async def generate_report(request: ReportRequest) -> ReportResponse:
    try:
        # Initialize GitHub client
        client = GitHubClient(token=request.github_token)

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)

        # Get repository data
        prs = client.get_pull_requests(
            request.repo_name, start_date=start_date, end_date=end_date
        )
        contributor_stats = client.get_contributor_stats(request.repo_name)
        languages = client.get_repository_languages(request.repo_name)

        # Generate report
        report_gen = ReportGenerator()
        report = report_gen.generate_report(
            repo_name=request.repo_name,
            prs=prs,
            period_start=start_date,
            period_end=end_date,
            contributor_stats=contributor_stats,
            languages=languages,
        )

        # Generate chart data
        size_chart = create_pr_size_chart(report)
        review_chart = create_review_time_chart(report)
        activity_chart = create_contributor_heatmap(report)
        throughput_chart, cycle_chart = create_velocity_charts(report)

        # Convert charts to JSON
        charts = {
            "size_distribution": size_chart.to_dict(),
            "review_times": review_chart.to_dict(),
            "contributor_activity": activity_chart.to_dict(),
            "throughput": throughput_chart.to_dict(),
            "cycle_times": cycle_chart.to_dict(),
        }

        return ReportResponse(report=report.model_dump(), charts=charts)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
