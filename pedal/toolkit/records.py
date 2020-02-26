from pedal.core.commands import explain


def check_record_instance(record_instance, record_type, instance_identifier, type_identifier):
    """

    Args:
        record_instance:
        record_type:
        instance_identifier:
        type_identifier:

    Returns:

    """
    if not isinstance(record_instance, dict):
        explain("{} was not a {} because it is not a dictionary.".format(instance_identifier, type_identifier))
        return False
    for expected_key, expected_value_type in record_type.items():
        if expected_key not in record_instance:
            explain("{} was supposed to have the key `{}`, but it did not.".format(instance_identifier, expected_key))
            return False
        actual_value = record_instance[expected_key]
        # Handle nested record types
        if isinstance(expected_value_type, list):
            if not isinstance(actual_value, list):
                explain("{} was not a {} because its key `{}` did not have a list.".format(
                    instance_identifier, type_identifier, expected_key
                ))
                return False
            elif actual_value:
                actual_value = actual_value[0]
                expected_value_type = expected_value_type[0]
        if not isinstance(actual_value, expected_value_type):
            explain("{} was not a {} because its key `{}` did not have a `{}` value".format(
                instance_identifier, type_identifier, expected_key, expected_value_type.__name__
            ))
            return False
    if len(record_type) != len(record_instance):
        explain("{} had extra keys that it should not have.".format(instance_identifier))
        return False
    return True
