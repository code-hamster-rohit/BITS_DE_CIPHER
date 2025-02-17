from config.connection import client

def calculate_score(question_number: int, session):
    total_number_of_correct_submission_in_question = client['2025']['USER_ANSWER'].count_documents({'question_number': question_number}, session=session)
    question_data = client['2025']['QNA'].find_one({'question_number': question_number}, session=session)
    rate_of_reduction, base_score, rate_change_factor = question_data['rate_of_reduction'], question_data['base_score'], question_data['rate_change_factor']
    score = base_score - total_number_of_correct_submission_in_question * rate_of_reduction
    new_rate_of_reduction = rate_of_reduction + rate_change_factor
    client['2025']['QNA'].update_one({'question_number': question_number}, {'$set': {'rate_of_reduction': new_rate_of_reduction}}, session=session)
    return score