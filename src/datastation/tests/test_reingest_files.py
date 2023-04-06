import logging
from unittest.mock import patch, mock_open
from datastation.scripts.reingest_files import reingest_dataset_files, get_pids_to_scan

def test_reingest_files_should_call_reingest_dataset_files():
    pid = 'doi:10.5072/DAR/CCRDM7'

    with patch('datastation.dv_api.DataverseAPI') as mock:
        mock.get_dataset_files.return_value = [dict(dataFile=dict(id=file_id)) for file_id in range(1, 5)]

        def mocked_reingest_file(file_id):
            if file_id == '1':
                return {'message': 'Tabular ingest is not supported for this file type (id: 4, type: image/jpeg)'}
            elif file_id == '2':
                return {'message': 'Skipping tabular ingest of the file machine_sensor_values_2023-01-09T12 22 13.604751Z.csv, because of the size limit (set to 1 bytes); '}
            else:
                return {'message': 'Datafile %s queued for ingest' % file_id}
            
        mock.reingest_file.side_effect = mocked_reingest_file

        reingest_dataset_files(mock, pid, 0)

        mock.get_dataset_files.assert_called_with(pid)
        mock.reingest_file.assert_any_call('1')
        mock.reingest_file.assert_any_call('2')
        mock.reingest_file.assert_any_call('3')
        mock.reingest_file.assert_any_call('4')

        mock.get_dataset_locks.assert_any_call(pid)
        
        assert mock.get_dataset_locks.call_count == 5
    
def test_get_pids_to_scan_returns_nonempty_pids():
    pid = 'doi:10.5072/DAR/CCRDM7'
    result = get_pids_to_scan(pid, None)
    assert result[0] == pid

def test_get_pids_to_scan_returns_nonempty_pids():
    pid = ' '
    result = get_pids_to_scan(pid, None)
    assert len(result) == 0

def test_get_pids_to_scan_returns_nonempty_pids():
    with patch('builtins.open', mock_open(read_data='pid1\npid2\n\n   \n')) as mock_file:
        result = get_pids_to_scan(None, 'test.txt')

    assert len(result) == 2

def test_get_pids_to_scan_uses_pid_argument_if_provided():
    with patch('builtins.open', mock_open(read_data='pid1\npid2\n\n   \n')) as mock_file:
        result = get_pids_to_scan('pid0', 'test.txt')

    assert result[0] == 'pid0'

