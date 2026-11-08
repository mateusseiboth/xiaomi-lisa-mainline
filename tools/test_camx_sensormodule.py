import unittest

from camx_sensormodule import c_table, c_tables, tables


def node(name, size=4):
    return {"name": name, "type": 0, "size": size, "id": 0}


class TablesTest(unittest.TestCase):
    def test_names_the_tables_after_the_gain_functions(self):
        nodes = [node("realToRegGain", 1), node("regToRealGain", 1)]
        for _ in range(4):
            nodes += [node("regSetting", 40), node("slaveAddr"), node("registerData")]
        nodes += [node("initSettings", 12), node("regSetting", 40)]
        labels = [label for _, _, label in tables(nodes)]
        self.assertEqual(labels, ["streamOn", "streamOff", "groupHoldOn",
                                  "groupHoldOff", "initSettings"])


class CTableTest(unittest.TestCase):
    def test_drops_chip_id_writes(self):
        out = c_table([(0x0000, 0x7309, 2, 2, 0), (0x6028, 0x4000, 2, 2, 0)], "init")
        self.assertNotIn("0x0000", out)
        self.assertIn("{ CCI_REG16(0x6028), 0x4000 },", out)

    def test_uses_the_data_width(self):
        out = c_table([(0x0bcc, 0x00, 2, 1, 0)], "init")
        self.assertIn("{ CCI_REG8(0x0bcc), 0x0000 },", out)

    def test_marks_delays(self):
        out = c_table([(0x6010, 0x0001, 2, 2, 5000)], "reset")
        self.assertIn("/* driver must wait 5000 us here */", out)

    def test_wraps_in_named_array(self):
        out = c_table([], "s5kgw3_init")
        self.assertTrue(out.startswith("static const struct cci_reg_sequence s5kgw3_init[] = {"))
        self.assertTrue(out.endswith("};"))


class CTablesTest(unittest.TestCase):
    def test_names_mode_tables_by_size(self):
        tables = [("init", [(0x6028, 0x4000, 2, 2, 0)]),
                  ("mode1", [(0x034c, 0x1220, 2, 2, 0), (0x034e, 0x0d90, 2, 2, 0)])]
        out = c_tables("s5kgw3", tables)
        self.assertIn("s5kgw3_init[]", out)
        self.assertIn("s5kgw3_4640x3472_mode[]", out)


if __name__ == "__main__":
    unittest.main()
