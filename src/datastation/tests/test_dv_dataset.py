import logging
from unittest.mock import patch
from datastation.dv_dataset import FileReingester

def test_FileReingester_should_call_dataset_locks():
    logging.basicConfig()
    logger = logging.getLogger('dv_dataset')
    logger.setLevel(logging.DEBUG)

    with patch('datastation.dv_dataset.DataverseRequestManager') as mock:
        mock.get_dataset_files.return_value = [dict(dataFile=dict(id=file_id)) for file_id in range(1, 5)]

        def mocked_reingest_file(file_id):
            if file_id == '1':
                return {'message': 'Tabular ingest is not supported for this file type (id: 4, type: image/jpeg)'}
            elif file_id == '2':
                return {'message': 'Skipping tabular ingest of the file machine_sensor_values_2023-01-09T12 22 13.604751Z.csv, because of the size limit (set to 1 bytes); '}
            else:
                return {'message': 'Datafile %s queued for ingest' % file_id}
            
        mock.reingest_file.side_effect = mocked_reingest_file
        reingester = FileReingester(mock, logger, 0)
        reingester.reingest_dataset_tabular_files('doi:10.5072/DAR/CCRDM7')

        mock.get_dataset_files.assert_called_with('doi:10.5072/DAR/CCRDM7')
        mock.reingest_file.assert_any_call('1')
        mock.reingest_file.assert_any_call('2')
        mock.reingest_file.assert_any_call('3')
        mock.reingest_file.assert_any_call('4')

        mock.get_dataset_locks.assert_any_call('doi:10.5072/DAR/CCRDM7')
        
        assert mock.get_dataset_locks.call_count == 2
    

def test_FileReingester_should_wait_for_locks_to_resolve():
    logger = logging.getLogger('test_dv_dataset')

    with patch('datastation.dv_dataset.DataverseRequestManager') as mock:
        mock.get_dataset_files.return_value = [dict(dataFile=dict(id=1))]
        mock.reingest_file.return_value = {'message': 'Datafile 1 queued for ingest'}
        mock.get_dataset_locks.side_effect = [
            [{'info': 'Lock 1'}],
            [{'info': 'Lock 1'}],
            []
        ]
            
        reingester = FileReingester(mock, logger, 0)
        reingester.reingest_dataset_tabular_files('doi:10.5072/DAR/CCRDM7')

        mock.get_dataset_files.assert_called_with('doi:10.5072/DAR/CCRDM7')
        mock.reingest_file.assert_any_call('1')
        mock.get_dataset_locks.assert_any_call('doi:10.5072/DAR/CCRDM7')
        
        # 3 calls to get_dataset_locks because the first two calls return a lock
        assert mock.get_dataset_locks.call_count == 3
    

