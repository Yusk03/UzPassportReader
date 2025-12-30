from pydantic import BaseModel, Field
from typing import Literal, Union, Dict, Any


DATE_RE = r"^\d{2}\.\d{2}\.\d{4}$"


class DocumentBaseResult(BaseModel):
    raw: list[str]

    surname: str | None = Field(examples=["ABDULBOQIYEV"])
    given_name: str | None = Field(examples=["FARRUX"])
    patronymic: str | None = Field(examples=["ABDULLO O'G'LI"])

    date_of_birth: str | None = Field(
        pattern=DATE_RE,
        examples=["03.04.2005"],
    )

    sex: Literal["M", "F"] | None

    date_of_issue: str | None = Field(
        pattern=DATE_RE,
        examples=["11.11.2024"],
    )
    date_of_expiry: str | None = Field(
        pattern=DATE_RE,
        examples=["10.11.2034"],
    )

    card_number: str | None = Field(
        examples=["AD1234567"],
        description="Document number",
    )

    place_of_birth: str | None = Field(examples=["NORIN TUMANI"])
    authority: str | None = Field(examples=["IIV 14242"])



class IdCardResult(DocumentBaseResult):
    personal_number: str | None = Field(
        description="Personal number",
        examples=["51111055950034"],
    )

    # qr: str | None
    # mrz: Dict[str, Any] | None
    

class PassportResult(DocumentBaseResult):
    authority: str | None = Field(examples=["MIA 33222"])


class OcrBaseResponse(BaseModel):
    status: Literal["ok"]
    document_type: str



class IdCardResponse(OcrBaseResponse):
    document_type: Literal["id_card"]
    result: IdCardResult


class PassportResponse(OcrBaseResponse):
    document_type: Literal["passport"]
    result: PassportResult


OcrResponse = Union[IdCardResponse, PassportResponse]
