from io import StringIO

from src.datastation.common.result_writer import JsonResultWriter


# Tests the JsonResultWriter class with pytest

class TestJsonResultWriter:

    # Tests that JsonResultWriter writes an empty JSON object for an empty result
    def test_writes_empty_object_for_empty_result(self):
        out_stream = StringIO()
        writer = JsonResultWriter(out_stream)
        writer.write({}, True)
        assert out_stream.getvalue() == "{}"







