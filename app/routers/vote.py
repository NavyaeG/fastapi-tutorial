from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter
from .. import schema,database,models,oauth2

from sqlalchemy.orm import Session
router=APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/",status_code=status.HTTP_201_CREATED)
def vote_for_post(Vote: schema.Vote, db: Session=Depends(database.get_db),current_user: int=Depends(oauth2.get_current_user)):
    post=db.query(models.Post).filter(models.Post.id==Vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {Vote.post_id} does not exist")
    vote_query=db.query(models.Vote).filter(models.Vote.post_id==Vote.post_id,models.Vote.user_id==current_user.id)
    found_vote=vote_query.first()
    if(Vote.dir==1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"user {current_user.id} has already voted on post {Vote.post_id}")
        new_vote=models.Vote(post_id=Vote.post_id,user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message":"successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="vote does not exist")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return{"message":"successfully deleted vote"}