

def hash_dict(dictionary):
    # NOTE: If we have a recursive dictionary, we have bigger problems.
    return hash(frozenset(
        [(key, hash_dict(value) if isinstance(value, dict) else value)
         for key, value in dictionary.items()]))


def hash_event_data(event):
    """
    Hashes event such that two events would match if all their data minus
    timestamp information and uuid's are the same.
    """
    # TODO: We should not be excluding pathspec and other source attributes when
    # we produce parser specific actions.
    excluded_attributes = {
        'display_name', 'filename', 'inode', 'pathspec', 'store_index', 'parser',
        'store_number', 'tag', 'timestamp', 'timestamp_desc', 'uuid'}

    event_dict = {}
    for name, value in event.GetAttributes():
        if name not in excluded_attributes:
            event_dict[name] = value

    return hash_dict(event_dict)
