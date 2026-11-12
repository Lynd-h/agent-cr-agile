import os

from anthropic import Anthropic
from openai import OpenAI

_clients = {}


def _client_anthropic():
    if "anthropic" not in _clients:
        _clients["anthropic"] = Anthropic()
    return _clients["anthropic"]


def _client_openai(config_modele):
    base_url = config_modele.get("base_url")
    cle_env = config_modele.get("cle_env", "OPENAI_API_KEY")
    cle = os.environ.get(cle_env) if cle_env else "pas-de-cle"
    if cle_env and not cle:
        raise RuntimeError(f"Variable d'environnement {cle_env} absente")
    identifiant = (base_url, cle_env)
    if identifiant not in _clients:
        _clients[identifiant] = OpenAI(api_key=cle, base_url=base_url)
    return _clients[identifiant]


def appeler_llm(config_modele, prompt_systeme, message, temperature=None, max_tokens=2000):
    fournisseur = config_modele["fournisseur"]
    modele = config_modele["modele"]
    temperature = config_modele.get("temperature", temperature)
    max_tokens = config_modele.get("max_tokens", max_tokens)

    if fournisseur == "anthropic":
        options = {"max_tokens": max_tokens}
        if temperature is not None:
            options["temperature"] = temperature
        reponse = _client_anthropic().messages.create(
            model=modele,
            system=prompt_systeme,
            messages=[{"role": "user", "content": message}],
            **options,
        )
        return "".join(bloc.text for bloc in reponse.content if bloc.type == "text").strip()

    if fournisseur in ("openai", "openai_compatible"):
        options = {}
        if fournisseur == "openai":
            options["max_completion_tokens"] = max_tokens
        else:
            options["max_tokens"] = max_tokens
        if temperature is not None:
            options["temperature"] = temperature
        if config_modele.get("format_json"):
            options["response_format"] = {"type": "json_object"}
        reponse = _client_openai(config_modele).chat.completions.create(
            model=modele,
            messages=[
                {"role": "system", "content": prompt_systeme},
                {"role": "user", "content": message},
            ],
            **options,
        )
        return (reponse.choices[0].message.content or "").strip()

    raise ValueError(f"Fournisseur inconnu : {fournisseur}")
