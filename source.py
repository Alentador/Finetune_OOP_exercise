import uuid


class Teacher:
    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.designation = kwargs["designation"]

    def create_quiz(self, subject, questions):
        quiz = Quiz(subject, questions)
        return quiz

    def assign_quiz(self, quiz, student):
        student.receive_quiz(quiz)
        return self

    def withdraw_quiz(self, quiz, student):
        student.remove_quiz(quiz)
        return self

    def grade_quiz(self, quiz):
        return quiz.get_grade()

    def set_question_answer(self, question, answer):
        question.set_answer(answer)
        return self

    def calculate_student_grade(self, student):
        return student.get_total_grade()


class Student:
    def __init__(self, name):
        self.id = uuid.uuid4()
        self.name = name
        self.pending_quizzes = []
        self.completed_quizzes = []

    def __str__(self):
        return f"<{self.name}>"

    def __eq__(self, other):
        return isinstance(other, Student) and self.id == other.id

    # a student answers a question
    def answer_question(self, question, choice):
        question.select_option(choice)
        return self

    # a student receives quiz
    def receive_quiz(self, quiz):
        self.pending_quizzes.append(quiz)
        return self

    # remove quiz from a student's pending quizzes
    def remove_quiz(self, quiz):
        try:
            self.pending_quizzes.remove(quiz)
        except ValueError as err:
            raise Exception("Quiz does not exist for student") from err
        return self

    # submit quiz
    def submit_quiz(self, quiz):
        if quiz.submit().is_completed:
            try:
                self.pending_quizzes.remove(quiz)
                self.completed_quizzes.append(quiz)
            except ValueError as err:
                raise Exception("Quiz does not exist for student") from err
        return self

    # Check if there is any pending quiz
    def no_pending_quiz(self):
        return not self.pending_quizzes and self.completed_quizzes

    # get the total grade of a student
    def get_total_grade(self):
        if self.no_pending_quiz():
            print("All quizzes are completed by student")
            total_grade = 0
            for quiz in self.completed_quizzes:
                total_grade += quiz.grade
            self.total_grade = total_grade
            return self.total_grade
        else:
            return (
                f"The student has {len(self.pending_quizzes)} quizzes pending"
            )


class Quiz:
    """
    Assumption: Each question carries only one point
    """
    def __init__(self, subject, questions=[]):
        self.subject = subject
        self.quiz_id = uuid.uuid4()
        self.questions = questions

    def __str__(self):
        return f"<{self.subject} quiz>"

    def __eq__(self, other):
        return isinstance(other, Quiz) and self.quiz_id == other.quiz_id

    # grade quiz
    def get_grade(self):
        grade = 0
        if hasattr(self, "is_completed"):
            if not self.is_completed:
                answered_questions = self.get_answered_questions()
            else:
                answered_questions = self.questions
            for question in answered_questions:
                if question.is_answer_correct():
                    grade += 1
            self.grade = grade
            return self.grade
        else:
            return "Quiz has not been submitted for grading"

    # get all total no of questions in quiz
    def get_question_count(self):
        return len(self.questions)

    # add a question to quiz
    def add_question(self, question):
        self.questions.append(question)

    # remove a question from quiz
    def remove_question(self, index):
        try:
            del self.questions[index]
        except IndexError as err:
            raise Exception(
                f"There are only {self.get_question_count()} questions in quiz"
            ) from err

    # get answered questions
    def get_answered_questions(self):
        return [
            question for question in self.questions
            if question.is_answered()
        ]

    # set is_completed to False to show partial submission
    # or to True to show full submission
    def submit(self):
        iter = [
            question.is_answered() for
            question in self.questions
        ]
        self.is_completed = all(iter)
        return self


class Question:
    def __init__(self, question, options=[]):
        self.question_text = question
        self.options = options
        self.choice_index = None
        self.__answer = None

    def __str__(self):
        return f"""
        <question: {self.question_text}>
        <options: {self.options}>
        """

    # add a new option to question (for teachers)
    def add_option(self, option):
        if isinstance(option, list):
            self.options.extend(option)
        else:
            self.options.append(option)
        return self

    # choose an option as answer (for student)
    def select_option(self, index):
        self.choice_index = index
        return self

    # get all options
    def get_options(self):
        return self.options.copy()

    # remove an option (for teachers)
    def remove_option(self, option):
        try:
            if isinstance(option, int):
                del self.options[option]
            elif isinstance(option, str):
                self.options.remove(option)
        except BaseException as err:
            raise Exception(
                "Option does not exist for question"
            ) from err
        return self

    # get the option a student selects as answer
    def get_choice(self):
        return self.options[self.choice_index]

    # set an option as the correct answer (for teachers)
    def set_answer(self, answer_index):
        self.__answer = answer_index
        return self

    # check if the correct answer is set by teacher
    def is_answer_set(self):
        return bool(self.__answer)

    # check if the chosen answer is the correct answer
    def is_answer_correct(self):
        if self.choice_index is not None and self.__answer is not None:
            return self.choice_index == self.__answer

    # check if an answer has been chosen by student
    def is_answered(self):
        return self.choice_index is not None


class Class:
    """
    Assumption: Several teachers teach a class but a
    particular teacher manages the class. He/She calculates
    total grades from all quizzes and rate the student
    """
    def __init__(self, level, teacher, students=[]):
        self.students = students
        self.level = level
        self.teacher = teacher

    def __str__(self):
        return f"<Class {self.level}> <{len(self.students)} students>"

    def add_student(self, student):
        self.students.append(student)

    def remove_student(self, student):
        try:
            self.students.remove(student)
        except ValueError as err:
            raise Exception(
                f"Student is not in class {self.level}"
            ) from err
