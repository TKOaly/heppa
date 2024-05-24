from application import db
from application.models import Base
from application.votes.models import Approval, Veto
from sqlalchemy.sql import text

tags = db.Table('tags',
    db.Column('tag_name', db.String(50), db.ForeignKey('tag.name'), primary_key=True),
    db.Column('candidate_id', db.Integer, db.ForeignKey('candidate.id'), primary_key=True)
)

class Candidate(Base):
    name = db.Column(db.String(144), nullable=False)
    selected = db.Column(db.Boolean, nullable=False)
    url = db.Column(db.String(144), nullable=False)
    description = db.Column(db.Text())
    nominator_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    approvals = db.relationship("Approval", backref='approval', lazy=True, cascade="all, delete-orphan")
    vetoes = db.relationship("Veto", backref='veto', lazy=True, cascade="all, delete-orphan")
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
        backref=db.backref('candidates', lazy=True))

    def __init__(self, name, nominator_id, url = "", description = None):
        self.name = name
        self.selected = False
        self.url = url
        self.description = description
        self.nominator_id = nominator_id

    @staticmethod
    def find_winning_candidates():
        # Sort unvetoed candidates by approvals
        stmt = text("SELECT candidate.id, candidate.name, COUNT(approval.id) AS count "
                    "FROM Candidate "
                    "LEFT JOIN veto ON veto.candidate_id = candidate.id "
                    "LEFT JOIN approval ON approval.candidate_id = candidate.id "
                    "GROUP BY candidate.id "
                    "HAVING COUNT(veto.candidate_id) = 0 "
                    "ORDER BY count")
        query_result = db.engine.execute(stmt)

        # Select all tied for first place
        result = []
        max_votes = -1
        for row in query_result:
            votes = row[2]
            if votes > max_votes:
                result.clear()
                result.append(row[1])
                max_votes = votes
            elif votes == max_votes:
                result.append(row[1])

        return result

class Tag(db.Model):
    name = db.Column(db.String(50), primary_key=True)
