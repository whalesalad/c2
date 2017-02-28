
def fancy_list_join(value):
    return_string = []

    for key,item in enumerate(value):
        if len(value) == 1:
            return_string.append(item)
            break
        if len(value) == 2 and (key == (len(value) - 1)):
            return_string.append(' and %s' % item)
            break
        if (len(value) > 2) and (key == (len(value) - 1)):
            return_string.append(' and ')
        elif key != 0:
            return_string.append(', ')

        return_string.append(item)

    return "".join(return_string)