from datetime import datetime
import time


def batch_process(pids, process_action_func, logging_dir='.', delay=0.1):
    """
    Simple for-loop processing on each dataset with the PID in the list, which is also available completely into memory.
    No multi-threading, no streaming no chaining, just plain and simple one thing at a time in a loop.

    Args:
        pids (list): List of dataset pids to process
        process_action_func (function): Function that gets called with the pid as parameter, use lambda if you have more params
        logging_dir (path): Location where the process log files will be written
        delay (float): Number of seconds the processing should wait before doing another step, helps keep the server happy!
    """
    # NOTE: maybe use logging for this next file writing?
    timestamp_str = '_' + datetime.now().strftime("%Y%m%d_%H%M%S")
    mutated_dataset_pids_file = open(logging_dir + '/pids_processed'
                                     + timestamp_str + '.txt', 'w')

    num_pids = len(pids)  # we read all pids in memory and know how much we have
    print("Start batch processing on {} datasets".format(num_pids))
    # Note that the following output is not useful when we have a lambda, maybe we could use getsource from inspect?
    print("For each dataset it will use action: {}".format(process_action_func.__name__))
    num = 0
    for pid in pids:
        num += 1
        # show progress, by count numbers etc.
        # note that we could use the 'rich' library to do fancy terminal stuf!
        print("[{} of {}] Processing dataset with pid: {}".format(num, num_pids, pid))
        try:
            mutated = process_action_func(pid)
            # log the pids for datatsets that are changed, which might need publishing...
            if mutated:
                mutated_dataset_pids_file.write(pid + '\n')
                mutated_dataset_pids_file.flush()
        except Exception as e:
            print("Stop processing because of an exception:  {}".format(e))
            break  # bail out, but maybe we can make an setting for doing as-much-as-possible and continue
        # be nice and give the server time to recover from our request and serve others...
        if delay > 0 and num < num_pids:
            print("Sleeping for {} seconds...".format(delay))
            time.sleep(delay)
    print("Done processing {} datasets".format(num_pids))
