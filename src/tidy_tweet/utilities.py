from typing import Dict, Any, List


def add_mappings(to_extend: Dict[Any, List], addition: Dict[Any, List]):
    """
    Appends all the mappings for each table from `addition` into `to_extend`.
    """
    for table in addition.keys():
        if table not in to_extend:
            to_extend[table] = []

        to_extend[table].extend(addition[table])
