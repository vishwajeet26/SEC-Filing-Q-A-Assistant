from uuid import uuid4

from app.retrieval.fusion import reciprocal_rank_fusion


def test_fusion_rewards_agreement():
    a, b, c = uuid4(), uuid4(), uuid4()
    fused = reciprocal_rank_fusion([[a, b], [b, a, c]], k=60)
    ids = [chunk_id for chunk_id, _ in fused]
    # a and b appear in both lists; c only in one.
    assert set(ids[:2]) == {a, b}
    assert ids[2] == c


def test_fusion_rank_one_beats_rank_five():
    a, b = uuid4(), uuid4()
    fused = reciprocal_rank_fusion([[a, b]], k=60)
    assert fused[0][0] == a
    assert fused[0][1] > fused[1][1]


def test_empty_rankings():
    assert reciprocal_rank_fusion([[], []]) == []
