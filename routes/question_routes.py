from fastapi import APIRouter
from models.auth_models import Token
from utils.scoring import calculate_score
from models.question_models import Answer
from config.connection import client
from datetime import datetime
from bson import ObjectId
import os

router = APIRouter()

@router.post('/question')
async def questions(token: Token):
    with client.start_session() as session:
        try:
            session.start_transaction()
            user = client['2025']['USER_INFO'].find_one({'password': token.token}, session=session)
            if user:
                users_latest_question_number = client['2025']['USER_QUESTION_NUMBER'].find_one({'email': user['email']}, session=session)
                latest_question_number = users_latest_question_number['latest_question_number']
                if latest_question_number > client['2025']['QNA'].count_documents({}, session=session):
                    session.commit_transaction()
                    return {'question_image_url': '', 'over': True}
                else:
                    question_image_url = os.getenv('QUESTION_IMAGE_PATH').format(latest_question_number)
                    session.commit_transaction()
                    return {'question_image_url': question_image_url, 'over': False}
            else:
                session.commit_transaction()
                return {'message': 'Invalid token'}
        except Exception as e:
            session.abort_transaction()
            return {'message': str(e)}
    client.close()

@router.post('/answer')
async def answer(answer: Answer):
    with client.start_session() as session:
        try:
            session.start_transaction()
            answer.answer = answer.answer.lower()
            user = client['2025']['USER_INFO'].find_one({'password': answer.token}, session=session)
            if user:
                users_latest_question_number = client['2025']['USER_QUESTION_NUMBER'].find_one({'email': user['email']}, session=session)
                client['2025'][user['email']].insert_one({'_id': ObjectId(), 'email': user['email'], 'question_number': users_latest_question_number['latest_question_number'], 'answer': answer.answer, 'timestamp': datetime.now()}, session=session)
                if users_latest_question_number['latest_question_number'] > client['2025']['QNA'].count_documents({}, session=session):
                    session.commit_transaction()
                    return {'message': 'Quiz over', 'over': True}
                else:
                    correct_answer = client['2025']['QNA'].find_one({'question_number': int(users_latest_question_number['latest_question_number'])}, session=session)['answer']
                    if answer.answer == correct_answer:
                        score = calculate_score(users_latest_question_number['latest_question_number'], session=session)
                        client['2025']['USER_SCORE'].insert_one({'_id': ObjectId(), 'email': user['email'], 'question_number': users_latest_question_number['latest_question_number'], 'score': score, 'timestamp': datetime.now()}, session=session)
                        client['2025']['USER_ANSWER'].insert_one({'_id': ObjectId(), 'email': user['email'], 'question_number': users_latest_question_number['latest_question_number'],'answer': answer.answer, 'timestamp': datetime.now()}, session=session)
                        client['2025']['USER_QUESTION_NUMBER'].update_one({'email': user['email']}, {'$inc': {'latest_question_number': 1}}, session=session)
                        session.commit_transaction()
                        return {'message': 'Correct answer', 'correct': True}
                    else:
                        session.commit_transaction()
                        return {'message': 'Incorrect answer', 'correct': False}
            else:
                session.commit_transaction()
                return {'message': 'Invalid token'}
        except Exception as e:
            session.abort_transaction()
            return {'message': str(e)}
    client.close()

@router.post('/hint/{hint_number}')
async def hint(hint_number: int, token: Token):
    with client.start_session() as session:
        try:
            session.start_transaction()
            user = client['2025']['USER_INFO'].find_one({'password': token.token}, session=session)
            if user:
                users_latest_question_number = client['2025']['USER_QUESTION_NUMBER'].find_one({'email': user['email']}, session=session)
                if users_latest_question_number['latest_question_number'] > client['2025']['QNA'].count_documents({}, session=session):
                    session.commit_transaction()
                    return {'message': 'Quiz over', 'active': False, 'hint': ''}
                else:
                    time_of_submission_of_users_latest_question = client['2025']['USER_ANSWER'].find_one({'email': user['email'], 'question_number': ((users_latest_question_number['latest_question_number'] - 1) or 1)}, session=session)['timestamp']
                    question_data = client['2025']['QNA'].find_one({'question_number': users_latest_question_number['latest_question_number']}, session=session)
                    hint, hint_timedelta = question_data['hint_' + str(hint_number)], question_data['hint_' + str(hint_number) + '_timedelta']
                    time_remaining = (datetime.now() - time_of_submission_of_users_latest_question).total_seconds()
                    if time_remaining < hint_timedelta:
                        remaining_seconds = int(hint_timedelta - time_remaining)
                        days, remainder = divmod(remaining_seconds, 86400)
                        hours, remainder = divmod(remainder, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        session.commit_transaction()
                        return {'message': f'Hint {hint_number} will be active in {days} days {hours} hours {minutes} minutes {seconds} seconds', 'active': False, 'hint': ''}
                    else:
                        session.commit_transaction()
                        return {'message': f'Hint {hint_number} is now active', 'active': True, 'hint': hint}
            else:
                session.commit_transaction()
                return {'message': 'Invalid token'}
        except Exception as e:
            session.abort_transaction()
            return {'message': str(e)}
    client.close()