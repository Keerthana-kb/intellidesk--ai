
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles

from app.models.user import User
from app.models.team import Team
from app.models.team_member import TeamMember

from app.schemas.team import (
    TeamCreate,
    TeamResponse,
    TeamMemberCreate,
    TeamMemberResponse
)

from app.services.team_service import (
    create_team,
    get_organization_teams,
    get_team_by_id,
    add_team_member,
    get_team_members
)

router = APIRouter()


# =====================================
# CREATE TEAM API
# =====================================

@router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    new_team = create_team(
        db=db,
        organization_id=current_user.organization_id,
        team_data=team_data
    )

    return TeamResponse(
        id=str(new_team.id),
        name=new_team.name,
        description=new_team.description,
        created_at=new_team.created_at
    )


# =====================================
# VIEW ALL ORGANIZATION TEAMS API
# =====================================

@router.get("/", response_model=list[TeamResponse])
def get_all_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "support_engineer")
    )
):
    teams = get_organization_teams(
        db=db,
        organization_id=current_user.organization_id
    )

    return [
        TeamResponse(
            id=str(team.id),
            name=team.name,
            description=team.description,
            created_at=team.created_at
        )
        for team in teams
    ]


# =====================================
# VIEW TEAM DETAILS API
# =====================================

@router.get("/{team_id}", response_model=TeamResponse)
def get_team_details(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "support_engineer")
    )
):
    try:
        team_uuid = uuid.UUID(team_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid team ID"
        )

    team = get_team_by_id(
        db=db,
        team_id=team_uuid,
        organization_id=current_user.organization_id
    )

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    return TeamResponse(
        id=str(team.id),
        name=team.name,
        description=team.description,
        created_at=team.created_at
    )


# =====================================
# ADD TEAM MEMBER API
# =====================================

@router.post(
    "/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED
)
def add_member_to_team(
    team_id: str,
    member_data: TeamMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    try:
        team_uuid = uuid.UUID(team_id)
        user_uuid = uuid.UUID(member_data.user_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid team ID or user ID"
        )

    team = get_team_by_id(
        db=db,
        team_id=team_uuid,
        organization_id=current_user.organization_id
    )

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    support_engineer = db.query(User).filter(
        User.id == user_uuid,
        User.organization_id == current_user.organization_id,
        User.role == "support_engineer",
        User.is_active == True
    ).first()

    if not support_engineer:
        raise HTTPException(
            status_code=404,
            detail="Active support engineer not found"
        )

    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team.id,
        TeamMember.user_id == support_engineer.id
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=409,
            detail="User is already a member of this team"
        )

    new_member = add_team_member(
        db=db,
        team_id=team.id,
        user=support_engineer
    )

    return TeamMemberResponse(
        id=str(new_member.id),
        team_id=str(new_member.team_id),
        user_id=str(new_member.user_id),
        user_name=support_engineer.full_name,
        email=support_engineer.email,
        joined_at=new_member.joined_at
    )


# =====================================
# VIEW TEAM MEMBERS API
# =====================================

@router.get(
    "/{team_id}/members",
    response_model=list[TeamMemberResponse]
)
def get_members_of_team(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "support_engineer")
    )
):
    try:
        team_uuid = uuid.UUID(team_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid team ID"
        )

    team = get_team_by_id(
        db=db,
        team_id=team_uuid,
        organization_id=current_user.organization_id
    )

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    members = get_team_members(
        db=db,
        team_id=team.id
    )

    return [
        TeamMemberResponse(
            id=str(member.id),
            team_id=str(member.team_id),
            user_id=str(member.user_id),
            user_name=user_name,
            email=email,
            joined_at=member.joined_at
        )
        for member, user_name, email in members
    ]
