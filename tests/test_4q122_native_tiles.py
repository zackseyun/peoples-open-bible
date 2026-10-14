import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "tools/textual_restoration/acquire_4q122_native_tiles.py"
SPEC = importlib.util.spec_from_file_location("native_tiles", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PyramidTests(unittest.TestCase):
    XML = ('<TileInfo origin="TOP_LEFT" image_width="3296" image_height="3296" '
           'tile_width="512" tile_height="512">'
           '<pyramid_level/><pyramid_level/><pyramid_level/>'
           '<pyramid_level inverse_scale="1" num_tiles_x="7" num_tiles_y="7"/></TileInfo>')

    def test_expected_native_level(self):
        self.assertEqual(MODULE.inspect_pyramid(self.XML)["native_level"], 3)

    def test_reduced_level_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.inspect_pyramid(self.XML.replace('inverse_scale="1"', 'inverse_scale="2"'))

    def test_unexpected_origin_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.inspect_pyramid(self.XML.replace("TOP_LEFT", "BOTTOM_LEFT"))

    def test_preview_dimensions_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.inspect_pyramid(self.XML.replace("3296", "1200"))


if __name__ == "__main__":
    unittest.main()
