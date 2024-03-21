#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import esm_tools_yaml


def test_esm_tools_yaml():
    yaml = esm_tools_yaml.EsmToolsYaml()
    with open("test.yaml", "r") as user_config:
        user_config = yaml.load(user_config)
    assert user_config["name"] == "Paul Gierz"
    assert user_config["user"] == "pgierz"
    assert user_config["my_var"] == "MY_VAR"
