from typing import Union
from flask import current_app

import os
import bcrypt
import datetime

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from minigame.utils.models import Players, PlayerBest, PlayerStatic


def connect():
    db_url = os.getenv('DB_URL')
    # db_name = os.getenv('DB_NAME')
    # db_password = os.getenv('DB_PASSWORD')

    if not db_url:
        raise ValueError("DB_URL 환경 변수가 설정되지 않았습니다.")

    # SQLAlchemy 엔진 생성
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    return engine, session


# 여기서부터는 계정과 관련된 함수들을 작성하는 파트 (계정이 존재하는지에 대한 여부, 로그인 적합성 판별 여부)


def account_exist(player_id: str) -> bool:
    # MySQL 의 Data 를 Dict 형태로 반환 시키는 DictCursor 사용
    engine, session = connect()
    try:
        user = session.query(Players).filter(Players.id == player_id).first()
        return user is not None
    finally:
        session.close()


def account_login(player_id: str, player_pw: str) -> tuple[bool, str]:
    engine, session = connect()
    try:
        # ORM으로 사용자 조회
        user = session.query(Players).filter(Players.id == player_id).first()

        # 1) 계정 존재 여부
        if not user:
            return False, '003'

        # 2) 인증 여부
        if not user.isConfirmed:
            return False, '004'

        # 3) 비밀번호 검증
        check_password = bcrypt.checkpw(player_pw.encode('utf-8'), user.password.encode('utf-8'))
        if check_password:
            return True, '000'
        else:
            return False, '002'
    finally:
        session.close()


def account_register(player_id: str, player_pw: str, email: str) -> None:
    engine, session = connect()
    try:
        # 새롭게 입력받은 정보를 정리하여 INSERT 로 계정을 추가함.
        new_user = Players(
            id=player_id,
            password=player_pw,
            email=email,
            isConfirmed=False
        )
        session.add(new_user)
        session.commit()
    finally:
        session.close()


def account_is_confirmed(email: str) -> bool:
    """
    특정 계정이 활성화 되어 있는지 확인
    :param email: 확인하고자 하는 계정의 이메일 주소
    :return: 활성화 여부 (True / False)
    """
    engine, session = connect()
    try:
        user = session.query(Players).filter(Players.email == email).first()
        if user:
            return user.isConfirmed
        return False
    finally:
        session.close()


def account_confirm(email: str) -> None:
    """
    특정 계정을 활성화 상태로 변경
    :param email: 활성화 하고자 하는 계정의 이메일 주소
    :return:
    """
    today = datetime.datetime.now()
    confirm_date = today.strftime('%Y-%m-%d')
    print(confirm_date)

    engine, session = connect()
    try:
        # 새롭게 입력받은 정보를 정리하여 UPDATE 로 값을 변경함.
        user = session.query(Players).filter(Players.email == email).first()
        if user:
            user.playerJoinDate = confirm_date
            user.isConfirmed = True

            # playerstatic 및 playerbest 테이블에 해당 유저의 playerID 추가
            new_static = PlayerStatic(playerId=user.id)
            new_best = PlayerBest(playerId=user.id)
            session.add(new_static)
            session.add(new_best)

            session.commit()
    finally:
        session.close()


def account_change_password(player_id: str, player_pw: str) -> None:
    """
    특정 계정의 비밀번호를 변경하는 함수
    :param player_id: 변경하고자 하는 유저 ID
    :param player_pw: 변경하고자 하는 새로운 비밀번호
    :return:
    """
    engine, session = connect()
    try:
        session.query(Players).filter(Players.id == player_id).update({
            Players.password: player_pw
        })
        session.commit()
    finally:
        session.close()


# 여기서부터는 스코어와 관련된 함수들을 작성하는 파트 (score, rank, leaderboard)
# 현재 해당 유저의 최고 점수와 최고 스테이지를 불러오는 함수
def get_user_score(player_id: str) -> dict:
    """
    현재 해당 계정의 최고 점수와 최고 스테이지를 불러오는 함수
    :param player_id:
    :return:
    """
    engine, session = connect()
    try:
        user_best = session.query(PlayerBest).filter(PlayerBest.playerlist_playerID == player_id).first()
        if user_best:
            return {
                'bestScore': user_best.bestScore,
                'bestStage': user_best.bestStage
            }
    finally:
        session.close()


# 현재 해당 유저의 최고 점수와 최고 스테이지, 기록 일자를 DB에 추가하는 함수
def update_user_score(player_id: str, best_score: int, best_stage: int) -> None:
    """
    현재 해당 계정의 최고 점수와 최고 스테이지, 기록 일자를 DB에 추가하는 함수
    :param player_id: 계정 ID
    :param best_score: 최고 점수
    :param best_stage: 최고 스테이지
    :return:
    """
    today = datetime.datetime.now()
    best_score_date = today.strftime('%Y-%m-%d')

    engine, session = connect()
    try:
        session.query(PlayerBest).filter(PlayerBest.playerId == player_id).update({
            PlayerBest.bestScore: best_score,
            PlayerBest.bestStage: best_stage,
            PlayerBest.bestScoreDate: best_score_date
        })
        session.commit()
    finally:
        session.close()


# 현재 해당 유저의 전체 등수를 받아오는 함수
def get_user_rank(player_id: str) -> dict:
    """
    현재 해당 계정의 전체 등수를 받아오는 함수
    :param player_id: 계정 ID
    :return: 등수 정보 [ranking]
    """
    engine, session = connect()
    try:
        user_rank = session.query(
            PlayerBest,
            func.rank().over(order_by=PlayerBest.bestScore.desc()).label('ranking')
        ).subquery()

        result = session.query(user_rank.c.ranking).filter(user_rank.c.playerId == player_id).first()
        if result:
            return {'ranking': result.ranking}
    finally:
        session.close()


def get_user_percent(player_id: str) -> dict:
    """
    현재 해당 계정의 상위 퍼센트를 받아오는 함수
    :param player_id: 계정 ID
    :return: 상위 퍼센트 정보 [percent]
    """
    engine, session = connect()
    try:
        total_players = session.query(func.count(PlayerBest.playerId)).scalar()
        user_best = session.query(PlayerBest).filter(PlayerBest.playerId == player_id).first()

        if user_best:
            higher_ranked = session.query(func.count(PlayerBest.playerId)).filter(
                PlayerBest.bestScore > user_best.bestScore
            ).scalar()

            percent = (higher_ranked / total_players) * 100 if total_players > 0 else 0
            return 100 - percent
    finally:
        session.close()


def get_leaderboard() -> dict:
    """
    현재 전체 사용자의 랭킹 정보를 받아오는 함수 (상위 10명)
    :return: 랭킹 정보 리스트 [{'rank', 'playerID', 'bestScore', 'bestStage', 'bestScoreDate}, ...]
    """
    engine, session = connect()
    try:
        leaderboard = session.query(
            PlayerBest,
            func.rank().over(order_by=PlayerBest.bestScore.desc()).label('rank')
        ).order_by(PlayerBest.bestScore.desc()).limit(10).all()

        result = []
        for entry in leaderboard:
            result.append({
                'rank': entry.rank,
                'playerID': entry.PlayerBest.playerId,
                'bestScore': entry.PlayerBest.bestScore,
                'bestStage': entry.PlayerBest.bestStage,
                'bestScoreDate': entry.PlayerBest.bestScoreDate
            })
        return result
    finally:
        session.close()


# 여기서부터는 레벨과 관련된 함수를 기입하는 곳 (레벨 업 여부, 현재 보유 경험치 및 레벨 체크)
def get_user_levelexp(player_id: str) -> Union[dict, bool]:
    """
    현재 해당 계정이 보유한 경험치의 수량을 얻어오는 함수.
    :param player_id: 계정 ID
    :return: 보유한 경험치 수량 Dict / False (유저 정보가 없을 경우)
    """
    engine, session = connect()
    try:
        user_static = session.query(PlayerStatic).filter(PlayerStatic.playerId == player_id).first()
        if user_static:
            return {
                'totalGetExp': user_static.totalGetExp,
                'totalLevel': user_static.totalLevel
            }
    finally:
        session.close()


def set_user_levelexp(player_id: str, exp: int, level: int) -> None:
    """
    특정 계정에 특정한 수량의 경험치와 레벨을 DB에 적용시키는 함수.
    :param player_id: 계정 ID
    :param exp: 경험치 수량
    :param level: 레벨 수량
    :return:
    """
    engine, session = connect()
    try:
        session.query(PlayerStatic).filter(PlayerStatic.playerId == player_id).update({
            PlayerStatic.totalGetExp: exp,
            PlayerStatic.totalLevel: level
        })
        session.commit()
    finally:
        session.close()


# 여기서부터는 유저의 개인 정보에 대한 함수 (가입 일자, 이메일, 최고 점수 등)
def user_profile_info(player_id: str) -> dict:
    """
    특정 계정의 프로필 정보를 불러오는 함수
    :param player_id:  계정 ID
    :return:
    """
    engine, session = connect()
    try:
        user = session.query(
            Players.email,
            Players.createdDtm,
            PlayerBest.bestScore,
            PlayerBest.bestStage,
            PlayerStatic.totalGetExp,
            PlayerStatic.totalLevel
        ).join(PlayerBest, Players.id == PlayerBest.playerId
               ).join(PlayerStatic, Players.id == PlayerStatic.playerId
                      ).filter(Players.id == player_id).first()

        if user:
            return {
                'playerEmail': user.email,
                'playerJoinDate': user.createdDtm,
                'bestScore': user.bestScore,
                'bestStage': user.bestStage,
                'totalGetExp': user.totalGetExp,
                'totalLevel': user.totalLevel
            }
    finally:
        session.close()