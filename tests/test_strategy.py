from raceops.strategy import recommend_strategy

def test_old_soft_tyre_recommends_pit():
    result=recommend_strategy({"tyre_age":16,"tyre_compound":"SOFT","tyre_temp_c":95})
    assert result["recommended_action"] == "PIT_SOON"

def test_safety_car_recommends_pit_now():
    result=recommend_strategy({"tyre_age":2,"tyre_compound":"MEDIUM","tyre_temp_c":90},active_incident="SAFETY_CAR")
    assert result["recommended_action"] == "PIT_NOW"

def test_hot_tyre_monitor():
    result=recommend_strategy({"tyre_age":2,"tyre_compound":"HARD","tyre_temp_c":110})
    assert result["recommended_action"] == "MONITOR"

def test_confidence_in_range():
    result=recommend_strategy({"tyre_age":2,"tyre_compound":"MEDIUM","tyre_temp_c":90})
    assert 0 <= result["confidence"] <= 1
