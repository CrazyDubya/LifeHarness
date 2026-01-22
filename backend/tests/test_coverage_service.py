"""Unit tests for coverage service."""
import pytest
from app.services.coverage_service import (
    get_coverage_slice,
    update_coverage
)
from app.models.coverage import CoverageGrid


def test_get_coverage_slice_no_coverage(db_session, test_user):
    """Test getting coverage slice when no coverage exists."""
    result = get_coverage_slice(
        db_session, 
        test_user.id, 
        ["20s"], 
        ["work_career"]
    )
    assert isinstance(result, dict)
    assert "20s" in result
    assert result["20s"]["work_career"] == 0


def test_get_coverage_slice_with_data(db_session, test_user):
    """Test getting coverage slice with existing data."""
    # Create some coverage data
    coverage = CoverageGrid(
        user_id=test_user.id,
        time_bucket="30s",
        topic_bucket="friendships",
        score=45
    )
    db_session.add(coverage)
    db_session.commit()
    
    result = get_coverage_slice(
        db_session,
        test_user.id,
        ["30s"],
        ["friendships"]
    )
    assert result["30s"]["friendships"] == 45


def test_update_coverage_creates_new(db_session, test_user):
    """Test that update_coverage creates new coverage entry."""
    update_coverage(
        db_session, 
        test_user.id, 
        "30s", 
        ["friendships"], 
        25
    )
    
    coverage = db_session.query(CoverageGrid).filter_by(
        user_id=test_user.id,
        time_bucket="30s",
        topic_bucket="friendships"
    ).first()
    
    assert coverage is not None
    assert coverage.score == 25


def test_update_coverage_increments_existing(db_session, test_user):
    """Test that update_coverage increments existing coverage."""
    # Create initial coverage
    initial = CoverageGrid(
        user_id=test_user.id,
        time_bucket="40s",
        topic_bucket="health_body",
        score=10
    )
    db_session.add(initial)
    db_session.commit()
    
    # Update it
    update_coverage(
        db_session, 
        test_user.id, 
        "40s", 
        ["health_body"], 
        20
    )
    
    coverage = db_session.query(CoverageGrid).filter_by(
        user_id=test_user.id,
        time_bucket="40s",
        topic_bucket="health_body"
    ).first()
    
    assert coverage.score == 30  # 10 + 20


def test_coverage_score_caps_at_100(db_session, test_user):
    """Test that coverage scores don't exceed 100."""
    # Start with 90
    initial = CoverageGrid(
        user_id=test_user.id,
        time_bucket="20s",
        topic_bucket="work_career",
        score=90
    )
    db_session.add(initial)
    db_session.commit()
    
    # Try to add 50 more
    update_coverage(
        db_session, 
        test_user.id, 
        "20s", 
        ["work_career"], 
        50
    )
    
    coverage = db_session.query(CoverageGrid).filter_by(
        user_id=test_user.id,
        time_bucket="20s",
        topic_bucket="work_career"
    ).first()
    
    # Should be capped at 100
    assert coverage.score == 100


