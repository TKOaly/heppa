from application import db
from application.models import Base

from sqlalchemy.sql import text

class User(Base):

    __tablename__ = "account"

    name = db.Column(db.String(144), nullable=False)
    username = db.Column(db.String(144), nullable=False)
    password = db.Column(db.String(144), nullable=False)

    nominations = db.relationship("Candidate", backref='account', lazy=True, cascade="all, delete-orphan")
    approvals = db.relationship("Approval", cascade="all, delete-orphan")
    vetoes = db.relationship("Veto", cascade="all, delete-orphan")

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password
  
    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    # Currently roles are not used for anything
    def roles(self):
        if self.username == "admin":
            return ["ADMIN"]
        else:
            return []
    
    @staticmethod
    def is_valid_username(username: str) -> bool:
        return len(username) > 1

    # Find the number of users with active votes
    @staticmethod
    def how_many_voters():
        stmt = text("SELECT COUNT(DISTINCT account.id) "
                    "FROM account "
                    "LEFT JOIN veto ON account.id = veto.voter_id "
                    "LEFT JOIN approval ON account.id = approval.voter_id "
                    "WHERE (approval.voter_id IS NOT NULL) OR (veto.voter_id IS NOT NULL)")

        query_result = db.session.execute(stmt)

        row = query_result.first()
        if row == None:
            return 0
        else:
            return row[0]