import awkward as ak

def unzip_records(records):
    return {field: array for field, array in zip(records.fields, ak.unzip(records))}

def merge_records(*records, depth_limit=1):
    merged = dict()
    for record in records:
        merged.update( unzip_records(record) )
    return ak.zip(merged, depth_limit=depth_limit)

def variable_collection(records, prefix, sep="", keepname=False):
    collection_branches = list(
        filter(lambda branch: branch.startswith(prefix+sep), records.fields))
    branches = records[collection_branches]
    if keepname: return branches

    branches = {
        field.replace(prefix+sep,""):branches[field]
        for field in collection_branches
    }
    return ak.zip(branches, depth_limit=1)

def cumand(masks):
    for i in range(1, len(masks)):
        masks[i] = masks[i] & masks[i-1]
    return masks
