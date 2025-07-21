from purrgress.plog.cleanup import tidy_day

def test_tidy_merge_and_sort():
    node = {
        "sessions": [
            {"task": "A", "tags": ["x"], "moods": ["happy"], "spans": ["12:30-13:00"]},
            {"task": "A", "tags": ["x"], "moods": ["tired"], "spans": ["11:00-11:30"]},
        ]
    }
    clean = tidy_day(node)
    sess = clean["sessions"][0]
    assert sess["spans"] == ["11:00-11:30", "12:30-13:00"]
    assert sess["moods"] == ["happy", "tired"]
