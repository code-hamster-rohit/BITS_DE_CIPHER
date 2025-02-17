from fastapi import APIRouter
from models.upload_data_models import UploadData
from config.connection import client
from bson import ObjectId

router = APIRouter()

@router.post('/upload_qna')
async def upload_question(upload_data: UploadData):
    with client.start_session() as session:
        try:
            session.start_transaction()
            client['2025']['QNA'].insert_one({'_id': ObjectId(), 'question_number': upload_data.question_number, 'answer': upload_data.answer, 'rate_of_reduction': upload_data.rate_of_reduction, 'base_score': upload_data.base_score, 'rate_change_factor': upload_data.rate_change_factor, 'hint_1': upload_data.hint_1, 'hint_1_timedelta': upload_data.hint_1_timedelta, 'hint_2': upload_data.hint_2, 'hint_2_timedelta': upload_data.hint_2_timedelta}, session=session)
            session.commit_transaction()
            return {'message': 'Question uploaded successfully'}
        except Exception as e:
            session.abort_transaction()
            return {'message': str(e)}