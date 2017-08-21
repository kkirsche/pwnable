def color(string, color=None):
    """
    Change text color for the Linux terminal.

    This method courtesy of Empire Project:
    https://github.com/EmpireProject/EmPyre/blob/master/lib/common/helpers.py#L222
    """

    attr = []
    # bold
    attr.append('1')

    if color:
        if color.lower() == "red":
            attr.append('31')
        elif color.lower() == "yellow":
            attr.append('33')
        elif color.lower() == "green":
            attr.append('32')
        elif color.lower() == "blue":
            attr.append('34')
        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

    else:
        if string.startswith("[!]"):
            attr.append('31')
            return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
        elif string.startswith("[+]"):
            attr.append('32')
            return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
        elif string.startswith("[*]"):
            attr.append('34')
            return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
        else:
            return string

def get_config(conn, fields):
    """
    Helper to pull common database config information outside of the
    normal menu execution.
    Fields should be comma separated.
        i.e. 'version,install_path'
    """

    cur = conn.cursor()
    cur.execute("SELECT {fields} FROM config".format(fields=fields))
    results = cur.fetchone()
    cur.close()

    return results
