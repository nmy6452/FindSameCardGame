from random import randint

import bcrypt

from minigame.utils.form import RegisterForm, FindPasswordForm
from minigame.utils.database import account_register, account_exist, account_confirm, get_account_by_email, account_is_confirmed, account_update_password
from minigame.utils.email import confirm_token, generate_confirmation_token, send_validate_email

from flask import Blueprint, session, url_for, redirect, request, render_template, flash, jsonify

signup = Blueprint('signup', __name__, url_prefix='/')


@signup.route('/register')
def register():
    """
    회원 가입 페이지를 렌더링하는 함수
    :return: 회원 가입 페이지 템플릿
    """
    # 이미 로그인이 된 상태라면, 다시 메인 페이지로 돌려 보냄.
    if 'loggedIn' in session:
        return redirect(url_for('main.main_page'))

    # 맨 처음 접속할 경우 GET 메소드로 요청이 오므로, 로그인 템플릿 제공
    form = RegisterForm(request.form)
    return render_template("register.html", form=form)

@signup.route('/find-password')
def find_password():
    """
    패스워드 찾기 페이지를 렌더링하는 함수
    :return: 패스워드 찾기 페이지 템플릿
    """
    # 이미 로그인이 된 상태라면, 다시 메인 페이지로 돌려 보냄.
    if 'loggedIn' in session:
        return redirect(url_for('main.main_page'))

    # 맨 처음 접속할 경우 GET 메소드로 요청이 오므로, 패스워드 찾기 템플릿 제공
    form = FindPasswordForm(request.form)
    return render_template("find-password.html", form=form)


@signup.route('/register/validation', methods=['POST'])
def register_check_vaild():
    """
    회원 가입 요청을 처리하는 함수
    :return:
    """
    # 회원 가입 전용 FlaskForm 객체인 RegisterForm 생성
    form = RegisterForm(request.form)
    # 먼저, form 에 아이디와 비밀번호가 전부 적혔는지를 먼저 체크함.
    if form.validate():
        # form에서 받아온 ID, PW, Email 정보를 저장함.
        username = form.username.data
        password = form.password.data
        email = form.email.data

        # 먼저, 해당 계정이 이미 인증되었는지를 체크해야 함.
        if account_is_confirmed(email):
            return jsonify(result='fail', errcode='002', status=200)
        else:
            # 만약 계정을 처음 생성하려고 시도했다면, DB에 새롭게 정보를 적재시킴.
            # 인증 URL이 만료된 케이스의 경우 정보를 적재하지 않고 인증 메일 전송.
            if not account_exist(username):
                password = (bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())).decode('utf-8')
                account_register(username, password, email)

            # email을 포함하여 새로운 랜덤 난수 토큰을 생성하고, 이를 url에 할당시킴.
            token = generate_confirmation_token(email)
            confirm_url = url_for('signup.confirm_verify_email', token=token, _external=True)
            html = render_template('email.html', confirm_url=confirm_url)
            subject = "FindSamePicture 미니게임 계정 인증"

            # 제목, html 템플릿, url을 전달하여 사용자에게 인증 메일을 전송함.
            send_validate_email(email, subject, html)
            return jsonify(result='success', status=200)

    return jsonify(result='fail', errcode='001', status=200)

@signup.route('/register/<token>')
def confirm_verify_email(token):
    """
    이메일 인증을 처리하는 함수
    :param token:
    :return:
    """
    email = confirm_token(token)
    # 이메일 기간 만료 시 False 리턴, 이를 체크하여 회원 가입 페이지로 보냄.
    if not email:
        flash('URL 인증 기간이 만료되었습니다. 처음부터 진행해주세요.')
        return redirect(url_for('signup.register'))

    if account_is_confirmed(email):
        flash('이미 인증이 완료된 계정입니다. 로그인을 해주세요.')
        return redirect(url_for('account.login'))
    else:
        account_confirm(email)
        flash("가입이 완료되었습니다. 생성된 계정으로 로그인하세요.")
        return redirect(url_for('account.login'))

    return redirect(url_for('main.mypage'))

@signup.route('/register/password', methods=['POST'])
def register_find_password():
    """
    패스워드 찾기 요청을 처리하는 함수
    :return:
    """
    # 패스워드 찾기 FlaskForm 객체인 FindPasswordForm 생성
    form = FindPasswordForm(request.form)
    # 먼저, form에 정상적인 이메일이 적혔는지를 먼저 체크함.
    if form.validate():
        # form에서 받아온 Email 정보를 저장함.
        email = form.email.data

        user = get_account_by_email(email)
        if user is None or user.isConfirmed == False:
            # 만약 등록되지 않았거나 인증되지 않은 계정의 경우 애러 코드 반환
            return jsonify(result='fail', errcode='003', status=200)
        else:
            # email을 포함하여 새로운 랜덤 난수 토큰을 생성하고, 이를 url에 할당시킴.
            token = generate_confirmation_token(email)
            confirm_url = url_for('signup.confirm_find_password', token=token, _external=True)
            html = render_template('find-pasword-email.html', confirm_url=confirm_url)
            subject = "FindSamePicture 미니게임 패스워드 찾기 인증"

            # 제목, html 템플릿, url을 전달하여 사용자에게 인증 메일을 전송함.
            send_validate_email(email, subject, html)
            return jsonify(result='success', status=200)

    return jsonify(result='fail', errcode='001', status=200)

@signup.route('/password/<token>')
def confirm_find_password(token):
    """
    패스워드 인증을 처리하는 함수
    :param token:
    :return:
    """
    email = confirm_token(token)
    # 이메일 기간 만료 시 False 리턴, 이를 체크하여 회원 가입 페이지로 보냄.
    if not email:
        flash('URL 인증 기간이 만료되었습니다. 처음부터 진행해주세요.')
        return redirect(url_for('signup.register'))

    # 토큰이 유효하면 재설정 폼을 보여줌. 폼은 password 필드를 포함하고
    # POST로 '/password/<token>/reset'에 제출되어야 함.
    return render_template('reset-password.html', token=token, email=email)

@signup.route('/password/<token>/reset', methods=['POST'])
def reset_password(token):
    """
    비밀번호 재설정 처리. 토큰으로 이메일 확인 후 새로운 비밀번호로 바로 갱신.
    AJAX 요청이면 JSON, 일반 폼 제출이면 로그인 페이지로 리다이렉트.
    """
    email = confirm_token(token)
    if not email:
        flash('URL 인증 기간이 만료되었습니다. 처음부터 진행해주세요.')
        return redirect(url_for('signup.register'))

    # 폼 또는 JSON으로부터 새 비밀번호 수신
    new_password = request.form.get('password') or (request.get_json(silent=True) or {}).get('password')
    if not new_password:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(result='fail', errcode='001', status=200)
        flash('비밀번호를 입력해주세요.')
        return redirect(url_for('signup.confirm_find_password', token=token))

    # 비밀번호 해시화 및 DB 업데이트
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    account_update_password(email, hashed)

    # 성공 처리: AJAX이면 JSON, 아니면 로그인 페이지로 이동
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(result='success', url=url_for('account.login'), status=200)
    flash('패스워드가 변경되었습니다. 로그인하세요.')
    return redirect(url_for('account.login'))