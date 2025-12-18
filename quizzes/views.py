"""
Views for quizzes app.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Quiz, Question
from .serializers import (
    QuizSerializer, 
    CreateQuizSerializer
)
from .functions import create_quiz_from_url


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quiz_view(request):
    """
    Create a new quiz from YouTube URL.
    """
    serializer = CreateQuizSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        url = serializer.validated_data['url']
        quiz_data = create_quiz_from_url(url, request.user)
        
        quiz = Quiz.objects.create(
            user=request.user,
            title=quiz_data['title'],
            description=quiz_data.get('description', ''),
            video_url=url
        )
        
        for q_data in quiz_data['questions']:
            Question.objects.create(
                quiz=quiz,
                question_title=q_data['question'],
                question_options=q_data['options'],
                answer=q_data['answer']
            )
        
        serializer = QuizSerializer(quiz)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        return Response(
            {'detail': f'Error creating quiz: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_list_view(request):
    """
    Get all quizzes for the authenticated user.
    """
    quizzes = Quiz.objects.filter(user=request.user)
    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def quiz_detail_view(request, pk):
    """
    Retrieve, update, or delete a specific quiz.
    """
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user)
    
    if request.method == 'GET':
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        serializer = QuizSerializer(
            quiz, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, 
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    elif request.method == 'DELETE':
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
