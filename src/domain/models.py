from dataclasses import dataclass

@dataclass
class User:
    uid: int
    name: str
    role: str
    psw: str

@dataclass
class SessionInf:
    cid: int
    sessionNo: int
