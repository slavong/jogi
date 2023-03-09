from pytest import mark

from jogi.schema.dump import _get_object_name_condition, _get_object_type_condition


@mark.parametrize(
    "types, expected",
    [
        ("", "1=1"),
        (["TABLE"], "object_type IN ('TABLE')"),
        (["view"], "object_type IN ('VIEW')"),
        (["Materialized View"], "object_type IN ('MATERIALIZED VIEW')"),
        (["a", "b", "c"], "object_type IN ('A','B','C')"),
    ],
)
def test_get_object_type_condition(types, expected):
    result = _get_object_type_condition(types)
    assert result == expected


@mark.parametrize(
    "names, expected",
    [
        ("", "1=1"),
        (["DUMMY%"], "object_name LIKE 'DUMMY%' ESCAPE '\\'"),
        (["NO WILDCARD"], "object_name LIKE 'NO WILDCARD' ESCAPE '\\'"),
        (["a", "b"], "object_name LIKE 'a' ESCAPE '\\'\n" " OR object_name LIKE 'b' ESCAPE '\\'"),
    ],
)
def test_get_object_name_condition(names, expected):
    result = _get_object_name_condition(names)
    assert result == expected
