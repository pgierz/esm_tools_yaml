#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import pytest

import esm_tools_yaml

TESTING_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE = f"{TESTING_DIR}/test.yaml"
FENCE_TEST_FILE = f"{TESTING_DIR}/fence_test.yaml"


@pytest.fixture
def insert_test_vars_into_env():
    os.environ["MY_VAR"] = "MY_VAR"
    os.environ["USER"] = "pgierz"
    os.environ["TESTING_VAR"] = "12345"


@pytest.fixture
def esm_tools_yaml_constructor():
    yaml_instance = esm_tools_yaml.EsmToolsYaml()
    return yaml_instance


@pytest.fixture
def user_config(esm_tools_yaml_constructor, insert_test_vars_into_env):
    yaml_instance = esm_tools_yaml_constructor
    with open(TEST_FILE, "r") as user_config:
        user_config = yaml_instance.load(user_config)
    return user_config


@pytest.fixture
def postprocessed_user_config(user_config):
    postprocesser = esm_tools_yaml.EsmToolsYamlPostprocessor()
    finished_config = postprocesser(user_config)
    return finished_config


@pytest.fixture
def fence_config(esm_tools_yaml_constructor):
    yaml_instance = esm_tools_yaml_constructor
    with open(FENCE_TEST_FILE, "r") as fence_config:
        fence_config = yaml_instance.load(fence_config)
    return fence_config


@pytest.fixture
def postprocessed_fence_config(fence_config):
    postprocesser = esm_tools_yaml.EsmToolsYamlPostprocessor()
    finished_config = postprocesser(fence_config)
    return finished_config


def test_basic_variable(user_config):
    assert user_config["person"]["name"] == "Paul Gierz"
    assert user_config["general"]["my_var"] == "MY_VAR"


def test_shell_variable(user_config):
    assert user_config["person"]["user"] == "pgierz"


def test_env_variable(user_config):
    assert user_config["general"]["test_env_var"] == "12345"
    assert user_config["general"]["test_env_var2"] == "12345"


def test_fence_expand(postprocessed_fence_config):
    assert "my_a_in_streams" in postprocessed_fence_config["all_vars"]
