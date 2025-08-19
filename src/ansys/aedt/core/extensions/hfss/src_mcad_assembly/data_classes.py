from typing import Union

from pydantic import BaseModel


class AedtInfo(BaseModel):
    version: str = ""
    port: int
    aedt_process_id: Union[int, None]
    student_version: bool = False