from application.auth.models import User
from application.api.models import APICandidate, APISelected
from application.candidates.models import Candidate

def parse_candidate(candidate: Candidate) -> APICandidate:
    return APICandidate(
        name = candidate.name,
        url = candidate.url,
        description = candidate.description,
        nominator = User.query.get(candidate.nominator_id).name,
        approvals = [User.query.get(approval.voter_id).name for approval in candidate.approvals],
        vetoes = [User.query.get(veto.voter_id).name for veto in candidate.vetoes],
        tags = [tag.name for tag in candidate.tags]
    )

def parse_candidates(candidates):
    return [parse_candidate(raw_candidate) for raw_candidate in candidates]

def parse_selected(candidate: Candidate) -> APISelected:
    return APISelected(
        name = candidate.name,
        description = candidate.description,
        url = candidate.url,
        nominator = User.query.get(candidate.nominator_id).name,
        tags = [tag.name for tag in candidate.tags],
        time_selected = candidate.date_modified
    )

def parse_selections(candidates):
    return [parse_selected(raw_candidate) for raw_candidate in candidates]
