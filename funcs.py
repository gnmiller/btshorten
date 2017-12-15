from random import randint
def rand_digits( n ):
    """Generate a string with n random digits 0-9 Leading 0s aren't truncated."""
    out = ""
    count = 0
    for i in range( 0, n ):
        print( i )
        out = out+"{}".format(randint(0,9))
    return out

