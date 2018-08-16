import pytest
from source import (
    Teacher, Student, Quiz,
    Question, Class
)


@pytest.fixture
def teacher():
    return Teacher(name="Jon Snow", designation="HOD")


@pytest.fixture
def student_one():
    return Student(name="Tyrion")


@pytest.fixture
def student_two():
    return Student(name="Jaime")


@pytest.fixture
def python_questions():
    question1 = Question(
        "which is the Python's sorting algorithm?",
        ["Jonsort", "Timsort", "Reeksort"]
    )

    question2 = Question(
        "which is immutable?",
        ["lists", "tuples"]
    )

    question3 = Question(
        "One of the following is a valid way to execute python modules",
        ["execfile(path_to_file)", "os.execute(path_to_file)"]
    )
    return [question1, question2, question3]


@pytest.fixture
def python_quiz(python_questions):
    return Quiz("Python", python_questions)


@pytest.fixture
def python_quiz_with_set_answers(python_quiz):
    python_quiz.questions[0].set_answer(1)
    python_quiz.questions[1].set_answer(1)
    python_quiz.questions[2].set_answer(0)
    return python_quiz


@pytest.fixture
def python_full_answered_quiz(
    student_one, python_quiz_with_set_answers
):
    quiz = python_quiz_with_set_answers
    student_one.receive_quiz(quiz)

    q1, q2, q3 = quiz.questions
    q1.select_option(1)
    q2.select_option(1)
    q3.select_option(0)

    return quiz


@pytest.fixture
def python_partial_answered_quiz(
    student_one, python_quiz_with_set_answers
):
    quiz = python_quiz_with_set_answers
    student_one.receive_quiz(quiz)

    q1, q2, q3 = quiz.questions
    q1.select_option(1)
    q2.select_option(1)

    return quiz


@pytest.fixture
def lfc_questions():
    question1 = Question(
        "what is the name of LFC's home field?",
        ["Goodison Park", "Etihad stadium", "Anfield"]
    )

    question2 = Question(
        "how many European cups have LFC won?",
        [6, 5, 3]
    )

    question3 = Question(
        "when was the last time LFC won a trophy?",
        [2006, 2004, 2000]
    )
    return [question1, question2, question3]


@pytest.fixture
def lfc_quiz(lfc_questions):
    return Quiz("LFC", lfc_questions)


@pytest.fixture
def lfc_quiz_with_set_answers(lfc_quiz):
    lfc_quiz.questions[0].set_answer(2)
    lfc_quiz.questions[1].set_answer(1)
    lfc_quiz.questions[2].set_answer(0)

    return lfc_quiz


@pytest.fixture
def lfc_full_answered_quiz(
    student_one, lfc_quiz_with_set_answers
):
    quiz = lfc_quiz_with_set_answers
    student_one.receive_quiz(quiz)

    q1, q2, q3 = quiz.questions
    q1.select_option(2)
    q2.select_option(1)
    q3.select_option(0)

    return quiz


@pytest.fixture
def class_one(teacher, student_one, student_two):
    return Class(6, teacher, [student_one, student_two])


def test_teacher_has_name_and_designation(teacher):
    assert teacher.name == "Jon Snow"
    assert teacher.designation == "HOD"


def test_class_has_level_teacher_students(class_one):
    assert class_one.level == 6
    assert len(class_one.students) == 2
    assert class_one.teacher is not None


def test_student_has_id_name(student_one):
    assert bool(student_one.id)
    assert student_one.name == "Tyrion"


def test_teacher_can_create_quiz(teacher, python_quiz):
    questions = python_quiz.questions
    subject = python_quiz.subject
    quiz = teacher.create_quiz(subject, questions)
    assert isinstance(quiz, Quiz)


def test_created_quiz_contains_questions(teacher, python_quiz):
    questions = python_quiz.questions
    subject = python_quiz.subject
    quiz = teacher.create_quiz(subject, questions)
    assert len(quiz.questions) == 3
    assert all([
        isinstance(question, Question)
        for question in quiz.questions
    ])


def test_questions_are_multiple_choice(teacher, python_quiz):
    questions = python_quiz.questions
    subject = python_quiz.subject
    quiz = teacher.create_quiz(subject, questions)
    assert all([
        len(question.options) > 0
        for question in quiz.questions
    ])


def test_student_can_be_assigned_quiz(teacher, python_quiz, student_one):
    teacher.assign_quiz(python_quiz, student_one)
    assert len(student_one.pending_quizzes) == 1


def test_student_can_answer_question(student_one, python_questions):
    question = python_questions[0]
    student_one.answer_question(question, 1)
    assert question.is_answered() is True


def test_teacher_can_set_question_answer(teacher, python_questions):
    question = python_questions[0]
    teacher.set_question_answer(question, 1)
    assert question.is_answer_set() is True


def test_student_quiz_partial_submissions(
    python_partial_answered_quiz, student_one
):
    student_one.submit_quiz(python_partial_answered_quiz)
    assert python_partial_answered_quiz.is_completed is False


def test_student_quiz_full_submission(
    teacher, python_full_answered_quiz, student_one
):
    student_one.submit_quiz(python_full_answered_quiz)
    assert python_full_answered_quiz.is_completed is True


def test_submitted_quiz_can_be_graded(
    teacher, python_full_answered_quiz, student_one
):
    student_one.submit_quiz(python_full_answered_quiz)
    teacher.grade_quiz(python_full_answered_quiz)
    assert python_full_answered_quiz.grade == 3


def test_unsubmitted_quiz_cannot_be_graded(
    teacher, python_full_answered_quiz, student_one
):
    response = teacher.grade_quiz(python_full_answered_quiz)
    assert response == "Quiz has not been submitted for grading"


def test_teacher_can_calculate_student_total_grade(
    teacher, student_one, lfc_full_answered_quiz,
    python_full_answered_quiz
):
    student_one.submit_quiz(python_full_answered_quiz)
    student_one.submit_quiz(lfc_full_answered_quiz)

    teacher.grade_quiz(python_full_answered_quiz)
    teacher.grade_quiz(lfc_full_answered_quiz)

    teacher.calculate_student_grade(student_one)
    assert student_one.total_grade == 6
