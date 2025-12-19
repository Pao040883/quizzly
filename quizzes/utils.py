"""
Utility functions for quizzes app.
"""


def create_question_in_db(quiz, q_data):
    """
    Create a single question for a quiz.

    Args:
        quiz: Quiz model instance
        q_data: Dictionary with question, options, answer keys
    """
    from .models import Question
    Question.objects.create(
        quiz=quiz,
        question_title=q_data['question'],
        question_options=q_data['options'],
        answer=q_data['answer']
    )


def create_quiz_in_db(user, quiz_data, url):
    """
    Create quiz and questions in database.

    Args:
        user: User model instance
        quiz_data: Dictionary with title, description, questions
        url: YouTube video URL string

    Returns:
        Quiz: Created quiz model instance
    """
    from .models import Quiz
    quiz = Quiz.objects.create(
        user=user,
        title=quiz_data['title'],
        description=quiz_data.get('description', ''),
        video_url=url
    )
    for q_data in quiz_data['questions']:
        create_question_in_db(quiz, q_data)
    return quiz
