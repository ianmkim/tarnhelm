import numpy as np

dtype_scheme_dict = ["int64", "int32", "float16", "float32", "float64"]

def encode_1d(arr):
    assert len(arr.shape) <= 1
    dtype_ind = dtype_scheme_dict.index(str(arr.dtype))
    as_bytes = arr.tobytes()
    as_bytes = bytes(chr(dtype_ind), 'ascii') + as_bytes
    return as_bytes

def decode_1d(as_bytes):
    dtype = int(as_bytes[0])
    assert dtype >= 0 and dtype < len(dtype_scheme_dict)
    arr = np.frombuffer(as_bytes[1:], dtype=dtype_scheme_dict[dtype])
    return arr

