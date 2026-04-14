import random

from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import (
    Student,
    Group,
    Lab,
    LabFile,
    Question,
    Attempt,
    Answer,
    LabPassword,
    FileQuestionAnswer
)
from app.security import generate_watermark_hash
from datetime import datetime

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    groups = Group.query.all()
    return render_template("public/index.html", groups=groups)


@public_bp.route("/start", methods=["POST"])
def start():
    last = request.form["last_name"].strip()
    first = request.form["first_name"].strip()
    group_id = request.form.get("group_id")
    password = request.form["password"].strip().upper()

    # 1. Ищем пароль варианта
    lp = LabPassword.query.filter_by(password=password).first()

    # Список групп нужен для рендера страницы ошибки, если что-то пойдет не так
    all_groups = Group.query.all()

    if not lp:
        return render_template(
            "public/index.html",
            groups=all_groups,
            error="Неверный пароль варианта",
        )

    # Получаем саму лабораторную работу
    lab = Lab.query.get(lp.lab_id)

    # --- НОВАЯ ПРОВЕРКА: ДОСТУП ГРУППЫ ---
    # Проверяем, привязана ли выбранная студентом группа к этой лабораторной
    if group_id:
        selected_group_id = int(group_id)
        # Получаем список ID разрешенных групп
        allowed_group_ids = [g.id for g in lab.groups]

        if selected_group_id not in allowed_group_ids:
            return render_template(
                "public/index.html",
                groups=all_groups,
                error="Эта работа недоступна для выбранной группы",
            )
    # -------------------------------------

    # Проверка дедлайнов (перенес выше, до создания студента)
    now = datetime.now()  # Или datetime.utcnow(), в зависимости от настроек вашего сервера
    if lab.start_at and lab.start_at > now:
        return render_template("public/index.html", groups=all_groups, error="Время выполнения работы еще не наступило")

    if lab.deadline_at and now > lab.deadline_at:
        return render_template("public/index.html", groups=all_groups, error="Срок сдачи работы истек")

    # 2. Ищем или создаём студента
    student_query = Student.query.filter_by(
        last_name=last,
        first_name=first,
    )
    if group_id:
        student_query = student_query.filter_by(group_id=group_id)

    student = student_query.first()
    if not student:
        student = Student(
            last_name=last,
            first_name=first,
            group_id=group_id if group_id else None,
        )
        db.session.add(student)
        db.session.commit()

    lab_file = LabFile.query.get(lp.file_id)

    # 3. Создаём попытку
    attempt = Attempt(
        student_id=student.id,
        lab_id=lab.id,
        password_id=lp.id,
        ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        started_at=datetime.utcnow(),
    )
    db.session.add(attempt)
    db.session.flush()  # flush, чтобы получить attempt.id до коммита

    # ЛОГИКА ВЫБОРА ВОПРОСОВ
    all_questions = Question.query.filter_by(lab_id=lab.id).all()
    selected_questions = []

    if lab.is_test and lab.questions_count > 0:
        # Если это КР и задано кол-во вопросов, берем случайные
        count = min(len(all_questions), lab.questions_count)
        selected_questions = random.sample(all_questions, count)
    else:
        # Иначе (ЛР) берем все вопросы
        selected_questions = all_questions

    # Создаем пустые ответы
    for q in selected_questions:
        empty_answer = Answer(
            attempt_id=attempt.id,
            question_id=q.id,
            answer_text="",
            is_correct=False
        )
        db.session.add(empty_answer)

    db.session.commit()

    return render_template(
        "public/questions.html",
        attempt=attempt,
        lab_file=lab_file,
        questions=selected_questions,
        lab=lab
    )


@public_bp.route("/finish/<int:attempt_id>", methods=["POST"])
def finish(attempt_id):
    attempt = Attempt.query.get_or_404(attempt_id)
    
    # ===== ЗАЩИТА ОТ ПОВТОРНОЙ ОТПРАВКИ =====
    # Если попытка уже была завершена (finished_at заполнено),
    # то студент вернулся назад и пытается пройти заново
    if attempt.finished_at is not None:
        # Создаем новую попытку вместо перезаписи старой
        
        # Получаем данные из старой попытки
        old_student_id = attempt.student_id
        old_lab_id = attempt.lab_id
        old_password_id = attempt.password_id
        
        # Создаем новую попытку
        new_attempt = Attempt(
            student_id=old_student_id,
            lab_id=old_lab_id,
            password_id=old_password_id,
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            started_at=datetime.utcnow(),
        )
        db.session.add(new_attempt)
        db.session.flush()
        
        # Получаем вопросы из старой попытки
        old_question_ids = [answer.question_id for answer in attempt.answers]
        
        # Создаем пустые ответы для новой попытки с теми же вопросами
        for q_id in old_question_ids:
            empty_answer = Answer(
                attempt_id=new_attempt.id,
                question_id=q_id,
                answer_text="",
                is_correct=False
            )
            db.session.add(empty_answer)
        
        db.session.commit()
        
        # Теперь работаем с новой попыткой
        attempt = new_attempt
    # ========================================
    
    lab_file_id = attempt.password.file_id
    correct_map = {
        fqa.question_id: fqa.correct_answer
        for fqa in FileQuestionAnswer.query.filter_by(lab_file_id=lab_file_id)
    }

    score = 0
    results_list = []

    # Итерируемся по УЖЕ СОЗДАННЫМ (в start) ответам этой попытки
    # Это гарантирует, что студент отвечает только на выданные ему вопросы
    for answer_record in attempt.answers:
        q = answer_record.question

        # Получаем ответ студента из формы
        ans_text = request.form.get(f"q{q.id}", "").strip()
        correct_text = (correct_map.get(q.id) or "").strip()

        is_correct = ans_text.lower() == correct_text.lower()

        if is_correct:
            score += 1
            results_list.append(['correct', q.text])
        else:
            results_list.append(['wrong', q.text])

        # Обновляем запись в БД
        answer_record.answer_text = ans_text
        answer_record.is_correct = is_correct

    attempt.score = score
    attempt.finished_at = datetime.utcnow()
    attempt.watermark_hash = generate_watermark_hash(attempt)
    db.session.commit()

    return render_template("public/finish.html", attempt=attempt, answers=results_list)
