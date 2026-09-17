"""Exercise the Ignition script with mocked Gateway APIs; no network required."""

import copy
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import zipfile


PACKAGE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = PACKAGE_DIR / "ignition_to_waterly"
SCRIPT = PROJECT_DIR / "ignition/script-python/waterly/code.py"
PATHS = [
    "[default]Process/TankLevel",
    "[default]DailyTotals/DailyRuntime",
    "[default]DailyTotals/DailyStarts",
]
NOW = 1800000000


class WaterlySubmissionTests(unittest.TestCase):
    def setUp(self):
        self.good = object()
        self.logger = Mock()
        self.system = ModuleType("system")
        self.system.util = SimpleNamespace(
            getLogger=Mock(return_value=self.logger), jsonEncode=json.dumps
        )
        self.system.tag = SimpleNamespace(readBlocking=Mock(side_effect=self.read_tags))
        self.system.net = SimpleNamespace(httpPost=Mock(return_value="OK"))
        values_module = ModuleType("com.inductiveautomation.ignition.common.model.values")
        values_module.QualityCode = SimpleNamespace(Good=self.good)
        with patch.dict(sys.modules, {
            "system": self.system,
            values_module.__name__: values_module,
        }):
            spec = importlib.util.spec_from_file_location("waterly_under_test", SCRIPT)
            self.waterly = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.waterly)
        # Different results on consecutive calls expose any per-tag clock reads.
        self.clock = Mock(side_effect=[NOW + 0.875, NOW + 86400.875])
        self.waterly.time = SimpleNamespace(time=self.clock)
        self.read_values = []

    def read_tags(self, paths):
        self.read_values = [
            SimpleNamespace(
                value=8.5 + index,
                quality=self.good,
                timestamp=SimpleNamespace(time=1700000000123 + index * 1000),
            )
            for index, _ in enumerate(paths)
        ]
        return self.read_values

    def payload(self):
        return json.loads(self.system.net.httpPost.call_args.args[2])

    def test_legacy_path_list_keeps_source_timestamps_and_request_shape(self):
        self.waterly.sendDataToWaterly(PATHS[:2])
        expected_paths = PATHS[:2] + self.waterly.system_tags
        self.system.tag.readBlocking.assert_called_once_with(expected_paths)
        body = self.payload()
        self.assertEqual(body, {
            "device": {"id": "<WATERLY_DEVICE_ID>", "type": "Ignition"},
            "timestamp": NOW,
            "tags": [
                {"name": path, "value": str(8.5 + index),
                 "last_change_timestamp": 1700000000 + index}
                for index, path in enumerate(expected_paths)
            ],
        })
        for tag in body["tags"]:
            self.assertIsInstance(tag["last_change_timestamp"], int)
        request = self.system.net.httpPost.call_args.args
        self.assertEqual(request[0], self.waterly.waterly_api_url)
        self.assertEqual(request[1], "application/json")
        self.assertEqual(request[7]["x-waterly-connect-token"], "<WATERLY_DEVICE_TOKEN>")
        self.clock.assert_called_once_with()

    def test_single_legacy_string_path(self):
        self.waterly.sendDataToWaterly(PATHS[0])
        self.system.tag.readBlocking.assert_called_once_with([PATHS[0]] + self.waterly.system_tags)
        self.assertEqual(self.payload()["tags"][0]["last_change_timestamp"], 1700000000)

    def test_dictionary_options_default_to_false(self):
        self.waterly.sendDataToWaterly([
            {"tag_name": PATHS[0]},
            {"tag_name": PATHS[1], "send_now_time": False},
        ])
        self.assertEqual(
            [tag["last_change_timestamp"] for tag in self.payload()["tags"][:2]],
            [1700000000, 1700000001],
        )

    def test_single_dictionary_can_opt_in(self):
        self.waterly.sendDataToWaterly({"tag_name": PATHS[1], "send_now_time": True})
        self.assertEqual(self.payload()["tags"][0]["last_change_timestamp"], NOW)
        self.clock.assert_called_once_with()

    def test_mixed_configuration_reuses_one_now_for_multiple_opted_in_tags(self):
        tags = [
            PATHS[0],
            {"tag_name": PATHS[1], "send_now_time": True},
            {"tag_name": PATHS[2], "send_now_time": True},
            {"tag_name": "[default]Process/Pressure", "send_now_time": False},
            {"tag_name": "[default]Process/Flow"},
        ]
        self.waterly.sendDataToWaterly(tags, send_now_time_all=False)
        self.assertEqual(
            [tag["last_change_timestamp"] for tag in self.payload()["tags"]],
            [1700000000, NOW, NOW, 1700000003, 1700000004,
             1700000005, 1700000006, 1700000007],
        )
        self.assertEqual(self.payload()["timestamp"], NOW)
        self.clock.assert_called_once_with()

    def test_global_override_applies_to_every_tag_including_system_tags(self):
        self.waterly.sendDataToWaterly([
            PATHS[0],
            {"tag_name": PATHS[1], "send_now_time": False},
            {"tag_name": PATHS[2], "send_now_time": True},
            {"tag_name": "[default]Process/Pressure"},
        ], send_now_time_all=True)
        body = self.payload()
        self.assertEqual(len(body["tags"]), 4 + len(self.waterly.system_tags))
        self.assertTrue(all(tag["last_change_timestamp"] == NOW for tag in body["tags"]))
        self.clock.assert_called_once_with()

    def test_full_paths_are_read_and_sent_unchanged_in_both_modes(self):
        paths = ["[Example Provider]Process/Tank Level", "[default]DailyTotals/D\u00e9bit"]
        self.waterly.sendDataToWaterly([
            {"tag_name": paths[0]},
            {"tag_name": paths[1], "send_now_time": True},
        ])
        self.system.tag.readBlocking.assert_called_once_with(paths + self.waterly.system_tags)
        self.assertEqual([tag["name"] for tag in self.payload()["tags"][:2]], paths)
        for tag in self.payload()["tags"]:
            self.assertEqual(set(tag), {"name", "value", "last_change_timestamp"})

    def test_repeated_daily_observations_get_fresh_now_without_mutating_configuration(self):
        tags = [PATHS[0], {"tag_name": PATHS[1], "send_now_time": True}]
        original = copy.deepcopy(tags)
        self.waterly.sendDataToWaterly(tags)
        first = self.payload()
        self.waterly.sendDataToWaterly(tags)
        second = self.payload()
        self.assertEqual(tags, original)
        self.assertEqual(first["tags"][0], second["tags"][0])
        self.assertEqual(first["tags"][1]["value"], second["tags"][1]["value"])
        self.assertEqual(first["tags"][1]["last_change_timestamp"], NOW)
        self.assertEqual(second["tags"][1]["last_change_timestamp"], NOW + 86400)
        self.assertEqual(len(second["tags"]), 2 + len(self.waterly.system_tags))
        self.assertEqual(self.clock.call_count, 2)

    def test_omitted_tags_still_submit_system_tags(self):
        self.waterly.sendDataToWaterly()
        self.system.tag.readBlocking.assert_called_once_with(self.waterly.system_tags)
        self.assertEqual([tag["name"] for tag in self.payload()["tags"]], self.waterly.system_tags)
        self.clock.assert_called_once_with()

    def test_bad_quality_is_skipped_without_shifting_tag_settings(self):
        def read_with_bad_quality(paths):
            values = self.read_tags(paths)
            values[0].quality = object()
            return values

        self.system.tag.readBlocking.side_effect = read_with_bad_quality
        self.waterly.sendDataToWaterly([
            {"tag_name": PATHS[0], "send_now_time": True},
            {"tag_name": PATHS[1], "send_now_time": False},
            {"tag_name": PATHS[2], "send_now_time": True},
        ])
        submitted = self.payload()["tags"]
        self.assertNotIn(PATHS[0], [tag["name"] for tag in submitted])
        self.assertEqual(submitted[0]["name"], PATHS[1])
        self.assertEqual(submitted[0]["last_change_timestamp"], 1700000001)
        self.assertEqual(submitted[1]["name"], PATHS[2])
        self.assertEqual(submitted[1]["last_change_timestamp"], NOW)

    def test_http_errors_still_log_failure(self):
        self.system.net.httpPost.side_effect = RuntimeError("example HTTP failure")
        self.waterly.sendDataToWaterly(PATHS[0], send_now_time_all=True)
        self.logger.error.assert_called_once_with("Error posting to WaterlyConnect: example HTTP failure")
        self.logger.info.assert_not_called()


class ProjectExportTests(unittest.TestCase):
    def test_downloadable_project_matches_checked_in_source(self):
        files = {path.relative_to(PROJECT_DIR).as_posix(): path.read_bytes()
                 for path in PROJECT_DIR.rglob("*")
                 if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"}
        with zipfile.ZipFile(PACKAGE_DIR / "ignition_to_waterly.zip") as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(sorted(archive.namelist()), sorted(files))
            for name, contents in files.items():
                self.assertEqual(archive.read(name), contents, name)


if __name__ == "__main__":
    unittest.main()
