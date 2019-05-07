# TODO: categorise better?


def CompareMatrices(mat1, mat2, tol):
    """
    This will check whether the entires are pair-wise close enough (within tol)
    """
    # just going to assume they are the same size...
    for i in range(len(mat1)):
        for j in range(len(mat1)):
            if abs(mat1[i][j] - mat2[i][j]) > tol:
                return False
    return True


def ContinuousCompare(lst, tol):
    """
    Takes a list of tuples, and each element is compared to the next one
    Any tuple that changes has the index of it returned
    """
    changing_indices = set()
    last_tup = None
    # iterate over all the tuples
    for i in range(len(lst)):
        # if it's the first entry, we just want to assign it and move onto the
        # next iteration
        if i == 0:
            last_tup = lst[i]
            continue
        else:
            tup = lst[i]
        # remove the indices already found to change so we don't keep testing
        # them
        indices_left_to_check = set(range(len(tup))) - changing_indices
        for j in indices_left_to_check:
            if (tup[j] - last_tup[j]).magnitude > tol:
                # if it changes, add it to the list
                changing_indices.add(j)
        last_tup = tup
    return changing_indices


def getParentRefScene(obj):
    """
    Returns the parent reference scene for the provided object.
    This is determined by whether the object has a parent at any point that is
    a reference node.
    """
    if obj.parent is None:
        return None
    if obj.parent.NMSNode_props.node_types == 'Reference':
        return obj.parent
    else:
        return getParentRefScene(obj.parent)