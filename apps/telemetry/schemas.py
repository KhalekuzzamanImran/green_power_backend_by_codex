from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel, ValidationError


class TelemetryMessage(BaseModel):
    device_id: str | None = Field(default=None)
    topic: str
    timestamp: str
    payload: dict[str, Any]

    model_config = ConfigDict(extra="forbid")


class RTDataPayload(BaseModel):
    ua: float
    ub: float
    uc: float
    ia: float
    ib: float
    time: str
    isend: str
    ic: float
    uab: float
    ubc: float
    uca: float
    pa: float
    pb: float
    pc: float
    zyggl: float
    qa: float
    qb: float
    qc: float
    zwggl: float
    sa: float
    sb: float
    sc: float
    zszgl: float
    pfa: float
    pfb: float
    pfc: float
    zglys: float
    f: float
    u0: float
    u_plus: float = Field(alias="uplus")
    u_minus: float = Field(alias="uminus")
    i0: float
    i_plus: float = Field(alias="iplus")
    i_minus: float = Field(alias="iminus")
    uxja: float
    uxjb: float
    uxjc: float
    ixja: float
    ixjb: float
    ixjc: float
    unb: float
    inb: float
    pdm: float
    qdm: float
    sdm: float

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class EnergyNowPayload(BaseModel):
    time: int | float
    isend: int | float
    zygsz: float
    fygsz: float
    zwgsz: float
    fwgsz: float
    zyjsz: float
    fyjsz: float
    zyfsz: float
    fyfsz: float
    zypsz: float
    fypsz: float
    zyvsz: float
    fyvsz: float
    zydvsz: float
    fydvsz: float
    zy6sz: float
    fy6sz: float
    dmpmax: float
    dmpmaxoct: float
    dmsmax: float
    dmsmaxoct: float
    uathd: float
    ubthd: float
    ucthd: float
    iathd: float
    ibthd: float
    icthd: float
    uaxbl3: float
    ubxbl3: float
    ucxbl3: float
    iaxbl3: float
    ibxbl3: float
    icxbl3: float
    uaxbl5: float
    ubxbl5: float
    ucxbl5: float
    iaxbl5: float
    ibxbl5: float
    icxbl5: float
    uaxbl7: float
    ubxbl7: float
    ucxbl7: float
    iaxbl7: float
    ibxbl7: float
    icxbl7: float
    iaxb3: float
    ibxb3: float
    icxb3: float
    iaxb5: float
    ibxb5: float
    icxb5: float
    iaxb7: float
    ibxb7: float
    icxb7: float

    model_config = ConfigDict(extra="forbid")


class EnvironmentPayload(BaseModel):
    pm1_0_ug_m3: float
    pm2_5_ug_m3: float
    pm10_0_ug_m3: float
    hum_percent: float
    temp_1_c: float
    dp_c: float

    model_config = ConfigDict(extra="forbid")


class GeneratorPayload(RootModel[dict[str, float | int | str]]):
    pass


class GeneratorDataModel(BaseModel):
    timestamp: int = Field(..., ge=0, description="Unix timestamp in milliseconds")
    payload: GeneratorPayload

    def model_dump(self, *args, **kwargs):
        base = super().model_dump(*args, **kwargs)
        return {"timestamp": base["timestamp"], **base["payload"]}

    @classmethod
    def from_flat_dict(cls, data: dict[str, float | int | str]):
        payload = dict(data)
        ts = payload.pop("timestamp", None)
        return cls(timestamp=ts, payload=GeneratorPayload(payload))


def validate_message(message: dict) -> None:
    msg = TelemetryMessage.model_validate(message)
    _validate_device_id(msg)
    _validate_payload(msg.topic, msg.payload)


def _validate_device_id(message: TelemetryMessage) -> None:
    return


def _validate_payload(topic: str, payload: dict[str, Any]) -> None:
    if topic == "MQTT_RT_DATA":
        RTDataPayload.model_validate(payload)
        return
    if topic == "MQTT_ENY_NOW":
        EnergyNowPayload.model_validate(payload)
        return
    if topic == "MQTT_DAY_DATA":
        GeneratorPayload.model_validate(payload)
        return
    if topic == "MQTT_ENY_FRZ":
        GeneratorPayload.model_validate(payload)
        return
    if topic == "CCCL/PURBACHAL/ENV_01":
        EnvironmentPayload.model_validate(payload)
        return
    if topic == "CCCL/PURBACHAL/ENM_01":
        GeneratorPayload.model_validate(payload)
        return
