from fastapi import Depends, status, HTTPException, Response, APIRouter
from sqlalchemy.orm import Session
from ..schemas.vote import Vote
from ..schemas.user import UserOut
from .. import database, models, oauth2

""" ToDo: Create Skeleton CLI """

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: Vote,
    db: Session = Depends(database.get_db),
    current_user: UserOut = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {vote.post_id} does not exist",
        )

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"user {current_user.id} has already voted on post {vote.post_id}",
            )
        new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id)
        db.add(new_vote)
        db.commit()
        return {"message": "succesfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote does not exist"
            )

        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "successfully deleted vote"}


"""
    Path = /vote
    The user extracted from the JWT token
    The body will contain the id of the post the user is voting on as well as the direction of the vote
    {
        post_id: 1234,
        vote_dir:0
    } 
    A cote direction of 1 means we want to add a vote, a driection of 0 means we want do delete a vote (like twitter,instagram etc.)
"""
