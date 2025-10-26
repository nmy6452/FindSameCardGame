from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Players(Base):
    """
    플레이어의 기본 정보를 담는 테이블 모델
    플레이어의 ID, 비밀번호, 이메일, 생성 날짜, 인증 여부 등을 저장함.
    """
    __tablename__ = 'cgt_players'

    id = Column(String, primary_key=True)
    password = Column("password", String)
    email = Column("email", String, unique=True)
    createdDtm = Column("created_dtm", DateTime)
    isConfirmed = Column("is_confirmed", Boolean)

    # 관계 설정 (선택)
    best = relationship("PlayerBest", back_populates="player", uselist=False)
    static = relationship("PlayerStatic", back_populates="player", uselist=False)


class PlayerBest(Base):
    """
    플레이어의 최고 기록 정보를 담는 테이블 모델
    플레이어의 최고 점수, 최고 스테이지, 최고 기록 달성 날짜 등을 저장함.
    """
    __tablename__ = 'cgt_player_best'

    id = Column(Integer, primary_key=True)
    playerId = Column("player_id", String, ForeignKey('cgt_players.id'))
    bestScore = Column("best_score", Integer)
    bestStage = Column("best_stage", Integer)
    bestScoreDate = Column("best_score_date", DateTime)

    player = relationship("Players", back_populates="best")


class PlayerStatic(Base):
    """
    플레이어의 통계 정보를 담는 테이블 모델
    플레이어의 총 경험치, 총 레벨 등을 저장함.
    """
    __tablename__ = 'cgt_player_static'

    id = Column(Integer, primary_key=True)
    playerId = Column("player_id",String, ForeignKey('cgt_players.id'))
    totalExp = Column("total_exp", Integer)
    totalLevel = Column("total_level", Integer)

    player = relationship("Players", back_populates="static")
