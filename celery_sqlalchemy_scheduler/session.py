# coding=utf-8
"""SQLAlchemy session."""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from kombu.utils.compat import register_after_fork

ModelBase = declarative_base()


@contextmanager
def session_cleanup(session):
    try:
        yield
    except Exception:
        # 发生异常则回滚
        session.rollback()
        raise
    finally:
        # 无论是否发生异常都关闭连接
        session.close()


def _after_fork_cleanup_session(session):
    session._after_fork()


class SessionManager(object):
    """Manage SQLAlchemy sessions."""

    def __init__(self):
        self._engines = {}
        self._sessions = {}
        self.forked = False
        self.prepared = False
        if register_after_fork is not None:
            register_after_fork(self, _after_fork_cleanup_session)

    def _after_fork(self):
        self.forked = True

    def get_engine(self, dburi, **kwargs):
        if self.forked:
            try:
                return self._engines[dburi]
            except KeyError:
                engine = self._engines[dburi] = create_engine(dburi, **kwargs)
                return engine
        else:
            return create_engine(dburi, poolclass=NullPool)
            # return create_engine(dburi)

    def create_session(self, dburi, short_lived_sessions=False, **kwargs):
        engine = self.get_engine(dburi, **kwargs)
        if self.forked:
            if short_lived_sessions or dburi not in self._sessions:
                self._sessions[dburi] = sessionmaker(bind=engine)
            return engine, self._sessions[dburi]
        else:
            return engine, sessionmaker(bind=engine)

    def prepare_models(self, engine):
        """准备models"""
        if not self.prepared:
            ModelBase.metadata.create_all(engine)
            self.prepared = True

    def session_factory(self, dburi, **kwargs):
        """session工厂"""
        engine, session = self.create_session(dburi, **kwargs)
        self.prepare_models(engine)
        return session()
