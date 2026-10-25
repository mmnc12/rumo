"""
Testes do bloco de calorias.

Cobre:
- `_estimate_calories` (pura, determinística) — todos os tipos de MET,
  fallback de tipo, duração zero/None, arredondamento, fallback de peso
  inválido (negativo, zero, None) e clamp de kcal negativo via MET
  corrompido (monkeypatch).
- `_get_user_weight_kg` — peso definido no banco, peso null → fallback 70.
- Integração: upload de GPX e FIT via rota real, verificando que
  `activity.calories` é int e > 0.
"""

import pytest
from sqlalchemy import update

from app.models.user import User
from app.services.activity_service import (
    _DEFAULT_WEIGHT_KG,
    _MET_BY_TYPE,
    _MET_DEFAULT,
    _estimate_calories,
    _get_user_weight_kg,
)


# ===== _estimate_calories — unit puro =====

@pytest.mark.parametrize(
    "activity_type", ["run", "walk", "cycle", "hike", "swim", "other"]
)
def test_estimate_calories_uses_correct_met_per_type(activity_type: str):
    """Cada tipo usa o MET definido em _MET_BY_TYPE."""
    weight_kg = 70.0
    duration_s = 3600
    expected_met = _MET_BY_TYPE[activity_type]
    expected = round(expected_met * weight_kg * 1.0)
    assert _estimate_calories(activity_type, duration_s, weight_kg) == expected


def test_estimate_calories_unknown_type_uses_default_met():
    """Tipo desconhecido cai no _MET_DEFAULT."""
    expected = round(_MET_DEFAULT * 70.0 * 1.0)
    assert _estimate_calories("synchronized_swimming", 3600, 70.0) == expected


def test_estimate_calories_none_type_uses_default_met():
    """activity_type None também cai no default (não explode)."""
    expected = round(_MET_DEFAULT * 70.0 * 1.0)
    assert _estimate_calories(None, 3600, 70.0) == expected


def test_estimate_calories_zero_duration_returns_none():
    """Duração 0 → None (não faz sentido calcular kcal sem tempo)."""
    assert _estimate_calories("run", 0, 70.0) is None


def test_estimate_calories_none_duration_returns_none():
    """Duração ausente → None."""
    assert _estimate_calories("run", None, 70.0) is None


def test_estimate_calories_negative_duration_returns_none():
    """Duração negativa → None (edge case defensivo)."""
    assert _estimate_calories("run", -10, 70.0) is None


def test_estimate_calories_rounds_to_int():
    """Retorno é sempre int, arredondado."""
    result = _estimate_calories("run", 1800, 70.0)
    assert isinstance(result, int)
    assert result == 343


def test_estimate_calories_negative_weight_falls_back_to_default():
    """Peso negativo é inválido → cai no _DEFAULT_WEIGHT_KG."""
    expected = round(_MET_BY_TYPE["run"] * _DEFAULT_WEIGHT_KG * 1.0)
    assert _estimate_calories("run", 3600, -70.0) == expected


def test_estimate_calories_zero_weight_falls_back_to_default():
    """Peso 0 (falsy) também cai no fallback."""
    expected = round(_MET_BY_TYPE["run"] * _DEFAULT_WEIGHT_KG * 1.0)
    assert _estimate_calories("run", 3600, 0.0) == expected


def test_estimate_calories_none_weight_falls_back_to_default():
    """Peso None → fallback."""
    expected = round(_MET_BY_TYPE["run"] * _DEFAULT_WEIGHT_KG * 1.0)
    assert _estimate_calories("run", 3600, None) == expected


def test_estimate_calories_clamps_negative_kcal(monkeypatch):
    """Clamp em 0 defende contra MET negativo (regressão no dicionário)."""
    monkeypatch.setitem(_MET_BY_TYPE, "run", -9.8)
    result = _estimate_calories("run", 3600, 70.0)
    assert result == 0


def test_estimate_calories_weight_is_float():
    """Peso pode vir como Decimal (Asyncpg + Numeric) — deve aceitar float()."""
    assert _estimate_calories("run", 3600, 65.5) == 642


# ===== _get_user_weight_kg — precisa do banco =====

@pytest.mark.asyncio
async def test_get_user_weight_kg_returns_configured_weight(db_session, test_user):
    """Se o usuário tem weight_kg definido, retorna como float.

    loop_scope="session" força o teste a rodar no mesmo loop da fixture
    db_session. Sem isso, o pytest-asyncio 0.25 cria um loop por teste
    e o asyncpg estoura "attached to a different loop".
    """
    from decimal import Decimal

    await db_session.execute(
        update(User)
        .where(User.id == test_user.id)
        .values(weight_kg=Decimal("72.50"))
    )
    await db_session.commit()

    weight = await _get_user_weight_kg(db_session, test_user.id)
    assert isinstance(weight, float)
    assert weight == 72.5


@pytest.mark.asyncio
async def test_get_user_weight_kg_falls_back_when_null(db_session, test_user):
    """Peso null (usuário não preencheu) → _DEFAULT_WEIGHT_KG."""
    await db_session.execute(
        update(User).where(User.id == test_user.id).values(weight_kg=None)
    )
    await db_session.commit()

    weight = await _get_user_weight_kg(db_session, test_user.id)
    assert weight == _DEFAULT_WEIGHT_KG


# ===== Integração: upload de GPX e FIT via rota =====

@pytest.mark.asyncio
async def test_upload_gpx_sets_calories(client, sample_gpx_bytes, db_session):
    """Upload de GPX deve preencher calories com int > 0."""
    response = await client.post(
        "/activities/upload",
        files={"file": ("sample_run.gpx", sample_gpx_bytes, "application/gpx+xml")},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["calories"] is not None
    assert isinstance(data["calories"], int)
    assert data["calories"] > 0


@pytest.mark.asyncio
async def test_upload_fit_sets_calories(client, sample_fit_bytes, db_session):
    """Upload de FIT deve preencher calories com int > 0."""
    response = await client.post(
        "/activities/upload",
        files={"file": ("sample_run.fit", sample_fit_bytes, "application/vnd.garmin.fit")},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["calories"] is not None
    assert isinstance(data["calories"], int)
    assert data["calories"] > 0
