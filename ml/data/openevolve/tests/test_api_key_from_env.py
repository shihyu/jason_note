"""
Tests for api_key ${VAR} environment variable substitution in configuration.
"""

import os
import tempfile
import unittest

from openevolve.config import Config, LLMModelConfig, _resolve_env_var


class TestEnvVarSubstitution(unittest.TestCase):
    """Tests for ${VAR} environment variable substitution in api_key fields"""

    def setUp(self):
        """Set up test environment variables"""
        self.test_env_var = "TEST_OPENEVOLVE_API_KEY"
        self.test_api_key = "test-secret-key-12345"
        os.environ[self.test_env_var] = self.test_api_key

    def tearDown(self):
        """Clean up test environment variables"""
        if self.test_env_var in os.environ:
            del os.environ[self.test_env_var]

    def test_resolve_env_var_with_match(self):
        """Test that _resolve_env_var resolves ${VAR} syntax"""
        result = _resolve_env_var(f"${{{self.test_env_var}}}")
        self.assertEqual(result, self.test_api_key)

    def test_resolve_env_var_no_match(self):
        """Test that strings without ${VAR} are returned unchanged"""
        result = _resolve_env_var("regular-api-key")
        self.assertEqual(result, "regular-api-key")

    def test_resolve_env_var_none(self):
        """Test that None is returned unchanged"""
        result = _resolve_env_var(None)
        self.assertIsNone(result)

    def test_resolve_env_var_missing_var(self):
        """Test that missing environment variable raises ValueError"""
        with self.assertRaises(ValueError) as context:
            _resolve_env_var("${NONEXISTENT_ENV_VAR_12345}")

        self.assertIn("NONEXISTENT_ENV_VAR_12345", str(context.exception))
        self.assertIn("is not set", str(context.exception))

    def test_api_key_env_var_in_model_config(self):
        """Test that api_key ${VAR} works in LLMModelConfig"""
        model_config = LLMModelConfig(name="test-model", api_key=f"${{{self.test_env_var}}}")

        self.assertEqual(model_config.api_key, self.test_api_key)

    def test_api_key_direct_value(self):
        """Test that direct api_key value still works"""
        direct_key = "direct-api-key-value"
        model_config = LLMModelConfig(name="test-model", api_key=direct_key)

        self.assertEqual(model_config.api_key, direct_key)

    def test_api_key_none(self):
        """Test that api_key can be None"""
        model_config = LLMModelConfig(name="test-model", api_key=None)

        self.assertIsNone(model_config.api_key)

    def test_api_key_env_var_in_llm_config(self):
        """Test that api_key ${VAR} works at LLM config level"""
        yaml_config = {
            "log_level": "INFO",
            "llm": {
                "api_base": "https://api.openai.com/v1",
                "api_key": f"${{{self.test_env_var}}}",
                "models": [{"name": "test-model", "weight": 1.0}],
            },
        }

        config = Config.from_dict(yaml_config)

        self.assertEqual(config.llm.api_key, self.test_api_key)
        # Models should inherit the resolved api_key
        self.assertEqual(config.llm.models[0].api_key, self.test_api_key)

    def test_api_key_env_var_per_model(self):
        """Test that api_key ${VAR} can be specified per model"""
        # Set up a second env var for testing
        second_env_var = "TEST_OPENEVOLVE_API_KEY_2"
        second_api_key = "second-secret-key-67890"
        os.environ[second_env_var] = second_api_key

        try:
            yaml_config = {
                "log_level": "INFO",
                "llm": {
                    "api_base": "https://api.openai.com/v1",
                    "models": [
                        {
                            "name": "model-1",
                            "weight": 1.0,
                            "api_key": f"${{{self.test_env_var}}}",
                        },
                        {
                            "name": "model-2",
                            "weight": 0.5,
                            "api_key": f"${{{second_env_var}}}",
                        },
                    ],
                },
            }

            config = Config.from_dict(yaml_config)

            self.assertEqual(config.llm.models[0].api_key, self.test_api_key)
            self.assertEqual(config.llm.models[1].api_key, second_api_key)
        finally:
            if second_env_var in os.environ:
                del os.environ[second_env_var]

    def test_api_key_env_var_in_evaluator_models(self):
        """Test that api_key ${VAR} works in evaluator_models"""
        yaml_config = {
            "log_level": "INFO",
            "llm": {
                "api_base": "https://api.openai.com/v1",
                "models": [{"name": "evolution-model", "weight": 1.0, "api_key": "direct-key"}],
                "evaluator_models": [
                    {
                        "name": "evaluator-model",
                        "weight": 1.0,
                        "api_key": f"${{{self.test_env_var}}}",
                    }
                ],
            },
        }

        config = Config.from_dict(yaml_config)

        self.assertEqual(config.llm.evaluator_models[0].api_key, self.test_api_key)

    def test_yaml_file_loading_with_env_var(self):
        """Test loading api_key ${VAR} from actual YAML file"""
        yaml_content = f"""
log_level: INFO
llm:
  api_base: https://api.openai.com/v1
  api_key: ${{{self.test_env_var}}}
  models:
  - name: test-model
    weight: 1.0
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            try:
                config = Config.from_yaml(f.name)
                self.assertEqual(config.llm.api_key, self.test_api_key)
            finally:
                os.unlink(f.name)

    def test_mixed_api_key_sources(self):
        """Test mixing direct api_key and ${VAR} in same config"""
        yaml_config = {
            "log_level": "INFO",
            "llm": {
                "api_base": "https://api.openai.com/v1",
                "api_key": "llm-level-direct-key",
                "models": [
                    {
                        "name": "model-with-env",
                        "weight": 1.0,
                        "api_key": f"${{{self.test_env_var}}}",
                    },
                    {
                        "name": "model-with-direct",
                        "weight": 0.5,
                        "api_key": "model-direct-key",
                    },
                ],
            },
        }

        config = Config.from_dict(yaml_config)

        self.assertEqual(config.llm.api_key, "llm-level-direct-key")
        self.assertEqual(config.llm.models[0].api_key, self.test_api_key)
        self.assertEqual(config.llm.models[1].api_key, "model-direct-key")


if __name__ == "__main__":
    unittest.main()
