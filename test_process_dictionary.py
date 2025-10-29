
import unittest
import os
import subprocess
import json

class TestProcessDictionary(unittest.TestCase):

    def setUp(self):
        """Set up for the test."""
        self.output_path = "dictionary_data_clean.json"
        # Ensure the output file from a previous run is removed.
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_script_produces_valid_json_with_known_entry(self):
        """
        Tests that the script runs and produces a JSON file containing a known,
        simple entry. This test is designed to be a basic validation, acknowledging
        that perfect parsing of the entire PDF is not guaranteed.
        """
        # Run the script
        try:
            subprocess.run(
                ["python3", "process_dictionary.py"],
                check=True,
                capture_output=True,
                text=True,
                timeout=300
            )
        except subprocess.CalledProcessError as e:
            self.fail(f"process_dictionary.py failed with error:\\n{e.stderr}")
        except subprocess.TimeoutExpired:
            self.fail("process_dictionary.py timed out.")

        # Verify the output file was created and is not empty
        self.assertTrue(os.path.exists(self.output_path), "Output file was not created.")
        self.assertTrue(os.path.getsize(self.output_path) > 0, "Output file is empty.")

        # Load the JSON data and verify its contents
        with open(self.output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertIsInstance(data, list, "JSON output is not a list.")
        self.assertGreater(len(data), 0, "JSON output is an empty list.")

        # Check for a simple, single-line entry that is likely to be parsed correctly.
        expected_entry = {
            "indonesian": "Batuk",
            "arabic": "لعس"
        }
        self.assertIn(expected_entry, data, "A specific, simple entry was not found in the output.")

    def tearDown(self):
        """Clean up after the test."""
        # Clean up the generated file after the test run.
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

if __name__ == '__main__':
    unittest.main()
