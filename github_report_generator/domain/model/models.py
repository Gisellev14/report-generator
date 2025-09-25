from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ReviewMetrics(BaseModel):
    time_to_first_review: Optional[float] = None  # in hours
    time_to_approval: Optional[float] = None  # in hours
    number_of_reviewers: int = 0
    number_of_comments: int = 0
    number_of_review_rounds: int = 0

class ContributorStats(BaseModel):
    login: str
    commits: int = 0
    additions: int = 0
    deletions: int = 0
    prs_authored: int = 0
    prs_merged: int = 0
    reviews_given: int = 0
    reviews_received: int = 0
    lead_times: List[float] = Field(default_factory=list)  # in hours, from PR creation to merge
    cycle_times: List[float] = Field(default_factory=list)  # in hours
    avg_review_time_given: Optional[float] = None  # in hours
    avg_review_time_received: Optional[float] = None  # in hours

class InitiativeStats(BaseModel):
    name: str
    pr_count: int = 0
    avg_lead_time: Optional[float] = None  # Average time from PR creation to merge
    avg_cycle_time: Optional[float] = None
    contributors: Dict[str, int] = Field(default_factory=dict)  # contributor -> contribution count

class PullRequestState(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"
    ALL = "all"

class PullRequest(BaseModel):
    number: int
    title: str
    state: PullRequestState
    author: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    comments: int = 0
    review_comments: int = 0
    commits: int = 0
    branch: str
    labels: List[str] = Field(default_factory=list)
    reviewers: List[str] = Field(default_factory=list)
    initiatives: List[str] = Field(default_factory=list)
    review_metrics: ReviewMetrics = Field(default_factory=ReviewMetrics)
    size_category: str = 'medium'  # xs, s, m, l, xl based on changes

class WeeklyMetrics(BaseModel):
    week_start: datetime
    completed_prs: int = 0
    completed_changes: int = 0
    avg_review_time: Optional[float] = None  # in hours
    avg_cycle_time: Optional[float] = None  # in hours
    active_contributors: int = 0
    total_reviews: int = 0
    total_comments: int = 0
    throughput_trend: Optional[float] = None  # positive = improving
    cycle_time_trend: Optional[float] = None  # negative = improving

class RepositoryReport(BaseModel):
    repo_name: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # General statistics
    total_commits: int = 0
    total_prs: int = 0
    total_contributors: int = 0
    languages: Dict[str, int] = Field(default_factory=dict)
    
    # PR statistics
    prs_merged: int = 0
    prs_open: int = 0
    prs_closed: int = 0
    prs: List[PullRequest] = Field(default_factory=list)
    median_lead_time: Optional[float] = None  # in hours
    median_cycle_time: Optional[float] = None  # in hours
    
    # Review statistics
    median_time_to_first_review: Optional[float] = None  # in hours
    median_time_to_approval: Optional[float] = None  # in hours
    avg_reviews_per_pr: float = 0.0
    avg_review_comments_per_pr: float = 0.0
    
    # PR size distribution
    pr_size_distribution: Dict[str, int] = Field(
        default_factory=lambda: {'xs': 0, 's': 0, 'm': 0, 'l': 0, 'xl': 0}
    )
    
    # Contributor statistics
    contributors: Dict[str, ContributorStats] = Field(default_factory=dict)
    
    # Initiative statistics
    initiatives: Dict[str, InitiativeStats] = Field(default_factory=dict)
    
    # Weekly metrics
    weekly_metrics: List[WeeklyMetrics] = Field(default_factory=list)
    
    # Velocity metrics
    avg_throughput: Optional[float] = None  # PRs per day
    max_throughput: Optional[float] = None  # PRs per day
    min_throughput: Optional[float] = None  # PRs per day
    throughput_trend: Optional[float] = None  # positive = improving
    avg_cycle_time: Optional[float] = None  # in hours
    max_cycle_time: Optional[float] = None  # in hours
    min_cycle_time: Optional[float] = None  # in hours
    cycle_time_trend: Optional[float] = None  # negative = improving
    
    # Highlights
    highlights: List[str] = Field(default_factory=list)
