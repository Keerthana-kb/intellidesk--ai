
from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.user import User


def create_team(db: Session, organization_id, team_data):
    new_team = Team(
        organization_id=organization_id,
        name=team_data.name,
        description=team_data.description
    )

    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    return new_team


def get_organization_teams(db: Session, organization_id):
    return db.query(Team).filter(
        Team.organization_id == organization_id
    ).order_by(
        Team.created_at.desc()
    ).all()


def get_team_by_id(db: Session, team_id, organization_id):
    return db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == organization_id
    ).first()


def add_team_member(db: Session, team_id, user):
    new_member = TeamMember(
        team_id=team_id,
        user_id=user.id
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member


def get_team_members(db: Session, team_id):
    return db.query(
        TeamMember,
        User.full_name,
        User.email
    ).join(
        User,
        TeamMember.user_id == User.id
    ).filter(
        TeamMember.team_id == team_id
    ).all()
