from little_api.config import Config


def test_set_get_item():
    config = Config()
    config["Secret"] = "secret"
    assert config["Secret"] == "secret"


def test_delete_item():
    config = Config()
    config["foo"] = 1
    assert config["foo"]
    del config["foo"]
    assert config.get("foo") is None


def test_len_and_iter():
    config = Config()
    values = [("name", "fred"), ("age", 23)]
    for key, value in values:
        config[key] = value

    assert len(config) == len(values)
    for key, value in values:
        assert config[key] == value
