import json
from pathlib import Path

import pytest

import juge
from skill import charger_prompt_skill, construire_demande

RACINE = Path(__file__).resolve().parent.parent

REPONSE_JUGE = json.dumps({c: {"note": 4, "justification": "ok"} for c in juge.CRITERES})

ATTENDU = {"piege": "test", "doit_contenir": ["a"], "ne_doit_pas_contenir": ["b"]}


def test_prompt_skill_sans_entete_et_avec_exemples():
    prompt = charger_prompt_skill(RACINE / "skill" / "compte-rendu-agile")
    assert not prompt.startswith("---")
    assert "Règles d'or" in prompt
    assert "Exemple 2" in prompt


def test_demande_contient_la_transcription():
    assert "<transcription>\nbonjour\n</transcription>" in construire_demande("bonjour")


def test_chaque_transcription_a_ses_attendus():
    for fichier in (RACINE / "data" / "transcriptions").glob("*.txt"):
        attendu = json.loads((RACINE / "data" / "attendus" / f"{fichier.stem}.json").read_text(encoding="utf-8"))
        assert attendu["doit_contenir"] and attendu["ne_doit_pas_contenir"] and attendu["piege_court"]


def test_json_entoure_de_texte(monkeypatch):
    monkeypatch.setattr(juge, "appeler_llm", lambda *a, **k: "Voici mon avis : " + REPONSE_JUGE + " Fin.")
    notes, justifications = juge.juger({}, "t", ATTENDU, "cr")
    assert notes == {c: 4 for c in juge.CRITERES}


def test_notes_ramenees_entre_1_et_5(monkeypatch):
    reponse = json.dumps({c: {"note": 9, "justification": ""} for c in juge.CRITERES})
    monkeypatch.setattr(juge, "appeler_llm", lambda *a, **k: reponse)
    notes, _ = juge.juger({}, "t", ATTENDU, "cr")
    assert set(notes.values()) == {5}


def test_juge_redemande_si_reponse_illisible(monkeypatch):
    reponses = iter(["pas du json", REPONSE_JUGE])
    monkeypatch.setattr(juge, "appeler_llm", lambda *a, **k: next(reponses))
    notes, _ = juge.juger({}, "t", ATTENDU, "cr")
    assert notes["fidelite"] == 4


def test_juge_abandonne_apres_deux_echecs(monkeypatch):
    monkeypatch.setattr(juge, "appeler_llm", lambda *a, **k: "toujours pas")
    with pytest.raises(RuntimeError):
        juge.juger({}, "t", ATTENDU, "cr")
