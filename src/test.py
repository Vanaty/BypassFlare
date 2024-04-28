import bypassflare_service as f
from dtos import V1RequestBase
req = V1RequestBase({"cmd":"request.get","url":"https://tronpick.io"})
rep = f.controller_v1_endpoint(req)
print(rep)
