from fastapi import APIRouter
from config.connection import client

router = APIRouter()

@router.post('/leaderboard')
async def leaderboard():
    with client.start_session() as session:
        try:
            session.start_transaction()
            all_user_scores = client['2025']['USER_SCORE'].find({}, session=session)
            leaderboard = {}
            for user_score in all_user_scores:
                if user_score['email'] in leaderboard:
                    leaderboard[user_score['email']] += user_score['score']
                else:
                    leaderboard[user_score['email']] = user_score['score']
            sorted_leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True))
            session.commit_transaction()
            return {'message': 'Leaderboard fetched successfully', 'leaderboard': sorted_leaderboard}
        except Exception as e:
            session.abort_transaction()
            return {'message': str(e)}