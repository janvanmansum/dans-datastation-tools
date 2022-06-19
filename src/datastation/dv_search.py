
# for iteration example see: https://guides.dataverse.org/en/5.6/api/search.html#iteration
# in a lot of cases we just want the pids and handle further processing elsewhere
# would be nice if we could make the 'paging' logic into a generic solution 'process_search'?
from datastation.dv_api import search


def get_dataset_pids_from_search(server_url, subtree):
    """
    Retrieve dataset pids from search results
    :param server_url:
    :param subtree:
    :return:
    """
    pids = []
    # pagination
    rows = 100
    start = 0
    page = 1
    condition = True  # emulate do-while
    while condition:
        result = search(server_url, subtree, start, rows)
        total_count = result['total_count']
        print("=== Page", page, "===")
        print("start:", start, " total:", total_count)
        for i in result['items']:
            # process/filter the result items, the dataset
            print("- ", i['global_id'], "(" + i['name'] + ")")
            # note that we only want the pids, it's not optimal with the use of resources
            # would be nice if the search API allowed specifying that we only want the pids (GraphQL like)
            pids.append(i['global_id'])
        start = start + rows
        page += 1
        condition = start < total_count
    return pids

