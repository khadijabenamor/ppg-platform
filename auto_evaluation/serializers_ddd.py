from rest_framework import serializers


class QuestionDDDSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    question_type = serializers.CharField()
    question_text = serializers.CharField()
    options = serializers.ListField()
    correct_answer = serializers.CharField()
    explanation = serializers.CharField(allow_blank=True)
    points = serializers.IntegerField()
    order = serializers.IntegerField()


class QuizDDDSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    course_id = serializers.CharField()
    difficulty = serializers.CharField()
    created_by_id = serializers.IntegerField(allow_null=True)
    is_ai_generated = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    questions = QuestionDDDSerializer(many=True)


class FlashcardDDDSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    course_id = serializers.CharField()
    question = serializers.CharField()
    answer = serializers.CharField()
    tags = serializers.ListField()
    created_by_id = serializers.IntegerField(allow_null=True)
    is_ai_generated = serializers.BooleanField()
    is_reviewed = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class QuizAttemptDDDSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    quiz_id = serializers.IntegerField()
    score = serializers.IntegerField()
    total_points = serializers.IntegerField()
    percentage = serializers.FloatField()
    answers = serializers.DictField()
    started_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(allow_null=True)


class StudentProgressDDDSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    course_id = serializers.CharField()
    total_quizzes = serializers.IntegerField()
    completed_quizzes = serializers.IntegerField()
    total_score = serializers.IntegerField()
    average_score = serializers.FloatField()
    streak_days = serializers.IntegerField()
    last_activity = serializers.DateField(allow_null=True)


# Alias for backwards compatibility
QuizSerializer = QuizDDDSerializer
FlashcardSerializer = FlashcardDDDSerializer
QuizAttemptSerializer = QuizAttemptDDDSerializer
StudentProgressSerializer = StudentProgressDDDSerializer