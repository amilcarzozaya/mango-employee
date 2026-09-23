import json
import pytest

from mango_cli.chain import (
    extract_handoff, extract_receipt, validate_handoff, validate_receipt,
    HandoffError
)

CONTRACT={
    "version":"1.0",
    "required_fields":["handoff_version","from_skill","to_skill","query_id","mode","entity","primary_query","intent","audience","geography","angle","proof_required","constraints"],
    "receipt_fields":["from_skill","to_skill","query_id","status"]
}

def handoff():
    return {
        "handoff_version":"1.0",
        "from_skill":"category-search-system",
        "to_skill":"linkedin-search-visibility",
        "query_id":"Q-017",
        "mode":"single_post",
        "entity":"Amílcar Zozaya + MANGO Employee",
        "primary_query":"¿Cómo crear un agente de IA para una empresa?",
        "intent":"how_to",
        "audience":"Operaciones",
        "geography":"México / LATAM",
        "angle":"Diseña sistemas, no sólo prompts.",
        "proof_required":["metodología"],
        "constraints":{"preserve_primary_query":True,"publish_gate_required":True}
    }

def test_extract_and_validate_handoff():
    h=handoff()
    text="before\nBEGIN_MANGO_HANDOFF\n"+json.dumps(h,ensure_ascii=False)+"\nEND_MANGO_HANDOFF\nafter"
    parsed=extract_handoff(text)
    assert validate_handoff(parsed,"category-search-system","linkedin-search-visibility",CONTRACT)["query_id"]=="Q-017"

def test_handoff_rejects_lineage_mutation():
    h=handoff(); h["to_skill"]="other-skill"
    with pytest.raises(HandoffError):
        validate_handoff(h,"category-search-system","linkedin-search-visibility",CONTRACT)

def test_handoff_rejects_primary_query_permission_relaxation():
    h=handoff(); h["constraints"]["preserve_primary_query"]=False
    with pytest.raises(HandoffError):
        validate_handoff(h,"category-search-system","linkedin-search-visibility",CONTRACT)

def test_receipt_must_preserve_query_id():
    h=handoff()
    receipt={"from_skill":"category-search-system","to_skill":"linkedin-search-visibility","query_id":"Q-999","status":"resolved"}
    with pytest.raises(HandoffError):
        validate_receipt(receipt,h,"category-search-system","linkedin-search-visibility",CONTRACT)

def test_extract_receipt():
    receipt={"from_skill":"category-search-system","to_skill":"linkedin-search-visibility","query_id":"Q-017","status":"resolved"}
    text="BEGIN_MANGO_HANDOFF_RECEIPT\n"+json.dumps(receipt)+"\nEND_MANGO_HANDOFF_RECEIPT"
    assert extract_receipt(text)["query_id"]=="Q-017"
