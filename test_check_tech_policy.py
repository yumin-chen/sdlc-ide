import unittest
from unittest.mock import patch, mock_open
from check_tech_policy import (
    Dependency,
    Config,
    DependencyParser,
    PolicyEnforcer,
    Report,
    main
)
import json
import toml
from datetime import datetime, timedelta
import io
import xml.etree.ElementTree as ET

class TestTechPolicyScript(unittest.TestCase):

    def test_dependency_equality(self):
        d1 = Dependency("lib-a", "1.0", "python")
        d2 = Dependency("lib-a", "1.0", "python")
        d3 = Dependency("lib-b", "1.0", "python")
        self.assertEqual(d1, d2)
        self.assertNotEqual(d1, d3)

    def test_config_loading_and_exceptions(self):
        config_data = {
            "diversity_threshold": 0.8,
            "exceptions": [
                {"dependency": "lib-a", "ecosystem": "python", "expires_on": "2099-01-01"},
                {"dependency": "lib-b", "ecosystem": "java", "expires_on": None}
            ]
        }
        with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
            config = Config("policy_config.json")
            self.assertEqual(config.diversity_threshold, 0.8)
            self.assertEqual(len(config.exceptions), 2)

            dep_a = Dependency("lib-a", "1.0", "python")
            dep_c = Dependency("lib-c", "1.0", "python")
            self.assertIsNotNone(config.get_active_exception(dep_a))
            self.assertIsNone(config.get_active_exception(dep_c))

    def test_java_parser_with_dep_management(self):
        pom_xml = """
<project>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.example</groupId>
                <artifactId>lib-managed</artifactId>
                <version>2.0</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>lib-managed</artifactId>
        </dependency>
    </dependencies>
</project>
        """
        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=pom_xml)):
            deps = DependencyParser.parse_java_dependencies()
            self.assertEqual(len(deps), 1)
            self.assertEqual(deps[0].version, "2.0")

    @patch('sys.exit')
    @patch('check_tech_policy.Report.write_json')
    @patch('check_tech_policy.DependencyParser.load_all')
    def test_main_flow(self, mock_load_all, mock_write_json, mock_exit):
        mock_load_all.return_value = [
            Dependency("lib-a", "1.0", "python", license="MIT"), # Should pass
            Dependency("lib-b", "1.0", "python", license="non-osi"), # Should fail but be excepted
            Dependency("lib-c", "1.0", "java", vendor_specific=True), # Should fail
            Dependency("lib-d", "1.0", "nodejs", implementations=1), # Should warn
        ]

        config_data = {"exceptions": [{"dependency": "lib-b", "ecosystem": "python", "expires_on": None}]}

        with patch('builtins.open', mock_open(read_data=json.dumps(config_data))) as mock_file:
            # We need to provide a value for sys.argv
            with patch('sys.argv', ['check_tech_policy.py']):
                main()

        # Verify exit code is 1 due to violations
        mock_exit.assert_called_with(1)

        # Verify JSON report was written
        self.assertTrue(mock_write_json.called)

if __name__ == '__main__':
    unittest.main()
