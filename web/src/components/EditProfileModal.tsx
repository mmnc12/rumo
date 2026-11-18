import { useEffect, useMemo, useRef, useState } from "react";

import { ApiError } from "../api/client";
import { useUpdateMe } from "../hooks/useProfile";
import type { UpdateMePayload } from "../api/auth";
import type { UserResponse } from "../types/api";

/**
 * [Sessão 41] Modal de edição do próprio perfil (paridade web do
 * mobile/lib/pages/edit_profile_page.dart da S39).
 *
 * Consome PUT /users/me (backend S39, commit 9d52470):
 *   body: { weight_kg?: float(0,500), height_cm?: float(0,300), full_name?: str(≤120) }
 *   response: UserResponse (mesmo shape do /auth/me)
 *
 * Semântica de "não mandou" vs "mandou null" (backend usa exclude_unset):
 * - campo AUSENTE do body → não toca no banco
 * - campo = null          → limpa o campo
 * - campo com valor       → atualiza
 *
 * O modal só envia os campos que o usuário MUDOU ou LIMPOU. Campo
 * intocado (valor atual == valor inicial) NÃO vai no body. Campo que o
 * usuário acionou "Limpar" vai como `null` explícito. Botão Salvar
 * desabilitado se nada mudou, se algum campo está inválido, ou se o
 * submit está em andamento.
 *
 * Validação client-side espelha o backend (S39): weight_kg in (0, 500),
 * height_cm in (0, 300), full_name ≤ 120.
 *
 * birth_date FICA FORA do escopo (UserUpdate do backend não aceita).
 * email/username também (rotas próprias, chave única).
 *
 * O `user` que o modal recebe via prop vem do useAuth() no ProfilePage.
 * Após o save, o useUpdateMe já faz auth.setUser(updated) +
 * invalidateQueries(["users", updated.id]) (S40) — reabrir o modal na
 * mesma sessão mostra os valores novos sem reload (S40a).
 */
interface EditProfileModalProps {
  open: boolean;
  onClose: () => void;
  current: UserResponse;
}

/**
 * Formata number pra string "limpa": null → "", inteiro → "80",
 * senão → "80.5". Mesma lógica do _formatNumber do mobile.
 */
function formatNumber(value: number | null): string {
  if (value === null) return "";
  if (Number.isInteger(value)) return value.toString();
  return value.toString();
}

/**
 * Parser tolerante: aceita "80", "80.5", "80,5" (PT-BR). Retorna null
 * se vazio ou inválido.
 */
function parseNumber(raw: string): number | null {
  const trimmed = raw.trim().replace(",", ".");
  if (trimmed === "") return null;
  const n = Number(trimmed);
  return Number.isFinite(n) ? n : null;
}

export function EditProfileModal({
  open,
  onClose,
  current,
}: EditProfileModalProps) {
  const updateMe = useUpdateMe();
  const weightRef = useRef<HTMLInputElement>(null);

  // Valores iniciais (recalculados ao abrir, via useEffect abaixo).
  const initialWeight = useMemo(
    () => formatNumber(current.weight_kg),
    [current.weight_kg]
  );
  const initialHeight = useMemo(
    () => formatNumber(current.height_cm),
    [current.height_cm]
  );
  const initialFullName = useMemo(
    () => current.full_name ?? "",
    [current.full_name]
  );

  // Estado dos campos — pré-preenchidos, resetados ao abrir.
  const [weightInput, setWeightInput] = useState<string>(initialWeight);
  const [heightInput, setHeightInput] = useState<string>(initialHeight);
  const [fullNameInput, setFullNameInput] =
    useState<string>(initialFullName);

  // "Limpar" foi acionado nos numéricos? Se sim, manda `null` explícito.
  const [clearWeight, setClearWeight] = useState<boolean>(false);
  const [clearHeight, setClearHeight] = useState<boolean>(false);

  // Erro de API no submit (rede/HTTP). Erros de validação são derivados.
  const [formError, setFormError] = useState<string | null>(null);

  // [Sessão 41] Reset ao abrir. Isso garante que reabrir o modal na
  // mesma sessão mostre o estado ATUAL do backend (que o useUpdateMe
  // atualizou via setUser) — não os valores congelados do primeiro mount.
  useEffect(() => {
    if (!open) return;
    setWeightInput(initialWeight);
    setHeightInput(initialHeight);
    setFullNameInput(initialFullName);
    setClearWeight(false);
    setClearHeight(false);
    setFormError(null);
  }, [open, initialWeight, initialHeight, initialFullName]);

  // [Sessão 41] Foco no primeiro campo ao abrir.
  useEffect(() => {
    if (!open) return;
    // requestAnimationFrame garante que o input já está no DOM.
    const id = window.requestAnimationFrame(() => {
      weightRef.current?.focus();
    });
    return () => window.cancelAnimationFrame(id);
  }, [open]);

  // [Sessão 41] Trava o scroll do body enquanto o modal está aberto.
  useEffect(() => {
    if (!open) return;
    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = original;
    };
  }, [open]);

  // [Sessão 41] Esc fecha (só quando não está salvando — evita cancelar
  // no meio de um PUT em andamento).
  useEffect(() => {
    if (!open) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape" && !updateMe.isPending) {
        onClose();
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, updateMe.isPending, onClose]);

  // ===== Validação derivada (render-time) =====
  const weightError: string | null = (() => {
    if (clearWeight) return null;
    const v = parseNumber(weightInput);
    if (v === null) return null; // vazio = não toca (ausente)
    if (v <= 0 || v >= 500) return "Peso deve estar entre 0 e 500 kg";
    return null;
  })();

  const heightError: string | null = (() => {
    if (clearHeight) return null;
    const v = parseNumber(heightInput);
    if (v === null) return null;
    if (v <= 0 || v >= 300) return "Altura deve estar entre 0 e 300 cm";
    return null;
  })();

  const fullNameError: string | null = (() => {
    if (fullNameInput.trim().length > 120) {
      return "Nome deve ter no máximo 120 caracteres";
    }
    return null;
  })();

  const hasError = !!(weightError || heightError || fullNameError);

  // ===== "Mudou alguma coisa?" =====
  const weightChanged =
    clearWeight || weightInput.trim() !== initialWeight;
  const heightChanged =
    clearHeight || heightInput.trim() !== initialHeight;
  const fullNameChanged = fullNameInput.trim() !== initialFullName;
  const hasChanged = weightChanged || heightChanged || fullNameChanged;

  const canSubmit =
    open && hasChanged && !hasError && !updateMe.isPending;

  // ===== Build do payload =====
  // Mesma semântica do _buildBody do mobile:
  // - clearWeight true      → weight_kg: null
  // - não limpo + mudou     → weight_kg: valor (se parseável)
  // - não limpo + igual     → ausente
  // - full_name mudou       → valor, ou null se apagou tudo
  function buildPayload(): UpdateMePayload {
    const payload: UpdateMePayload = {};

    if (clearWeight) {
      payload.weight_kg = null;
    } else if (weightInput.trim() !== initialWeight) {
      const v = parseNumber(weightInput);
      if (v !== null) payload.weight_kg = v;
    }

    if (clearHeight) {
      payload.height_cm = null;
    } else if (heightInput.trim() !== initialHeight) {
      const v = parseNumber(heightInput);
      if (v !== null) payload.height_cm = v;
    }

    if (fullNameChanged) {
      const trimmed = fullNameInput.trim();
      payload.full_name = trimmed === "" ? null : trimmed;
    }

    return payload;
  }

  function handleSubmit() {
    if (!canSubmit) return;
    const payload = buildPayload();
    if (Object.keys(payload).length === 0) {
      // Nada mudou de fato (pode acontecer se o usuário editou e voltou
      // ao valor inicial). Fecha sem request — idempotente.
      onClose();
      return;
    }
    setFormError(null);
    updateMe.mutate(payload, {
      onSuccess: () => {
        onClose();
      },
      onError: (err) => {
        if (err instanceof ApiError) {
          if (typeof err.detail === "string") {
            setFormError(err.detail);
          } else {
            setFormError(`Falha ao salvar (HTTP ${err.status}).`);
          }
        } else {
          setFormError("Falha ao salvar. Verifique sua conexão.");
        }
      },
    });
  }

  if (!open) return null;

  const saving = updateMe.isPending;

  return (
    <div
      role="presentation"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={() => {
        if (!saving) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-profile-title"
        className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <h2
          id="edit-profile-title"
          className="text-lg font-semibold text-gray-900"
        >
          Editar perfil
        </h2>
        <p className="mt-1 text-xs text-gray-500">
          Atualize seus dados. Campos vazios não são alterados.
        </p>

        <div className="mt-4 space-y-4">
          {/* ===== Peso ===== */}
          <div>
            <label
              htmlFor="edit-profile-weight"
              className="block text-sm font-medium text-gray-700"
            >
              Peso (kg)
            </label>
            <div className="mt-1 flex items-center gap-2">
              <input
                id="edit-profile-weight"
                ref={weightRef}
                type="text"
                inputMode="decimal"
                value={weightInput}
                onChange={(e) => {
                  setWeightInput(e.target.value);
                  if (clearWeight) setClearWeight(false);
                }}
                disabled={saving || clearWeight}
                placeholder="Ex.: 75.5"
                className={`w-full rounded-md border px-3 py-2 text-sm text-gray-900 disabled:bg-gray-100 ${
                  weightError
                    ? "border-red-500"
                    : "border-gray-300"
                }`}
              />
              {clearWeight ? (
                <button
                  type="button"
                  onClick={() => {
                    setClearWeight(false);
                    setWeightInput(initialWeight);
                  }}
                  disabled={saving}
                  className="whitespace-nowrap rounded-md border border-gray-300 bg-white px-3 py-2 text-xs font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50"
                >
                  Desfazer
                </button>
              ) : (
                current.weight_kg !== null && (
                  <button
                    type="button"
                    onClick={() => {
                      setClearWeight(true);
                      setWeightInput("");
                    }}
                    disabled={saving}
                    className="whitespace-nowrap rounded-md border border-gray-300 bg-white px-3 py-2 text-xs font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50"
                  >
                    Limpar
                  </button>
                )
              )}
            </div>
            {weightError && (
              <p className="mt-1 text-xs text-red-600">{weightError}</p>
            )}
          </div>

          {/* ===== Altura ===== */}
          <div>
            <label
              htmlFor="edit-profile-height"
              className="block text-sm font-medium text-gray-700"
            >
              Altura (cm)
            </label>
            <div className="mt-1 flex items-center gap-2">
              <input
                id="edit-profile-height"
                type="text"
                inputMode="decimal"
                value={heightInput}
                onChange={(e) => {
                  setHeightInput(e.target.value);
                  if (clearHeight) setClearHeight(false);
                }}
                disabled={saving || clearHeight}
                placeholder="Ex.: 180"
                className={`w-full rounded-md border px-3 py-2 text-sm text-gray-900 disabled:bg-gray-100 ${
                  heightError
                    ? "border-red-500"
                    : "border-gray-300"
                }`}
              />
              {clearHeight ? (
                <button
                  type="button"
                  onClick={() => {
                    setClearHeight(false);
                    setHeightInput(initialHeight);
                  }}
                  disabled={saving}
                  className="whitespace-nowrap rounded-md border border-gray-300 bg-white px-3 py-2 text-xs font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50"
                >
                  Desfazer
                </button>
              ) : (
                current.height_cm !== null && (
                  <button
                    type="button"
                    onClick={() => {
                      setClearHeight(true);
                      setHeightInput("");
                    }}
                    disabled={saving}
                    className="whitespace-nowrap rounded-md border border-gray-300 bg-white px-3 py-2 text-xs font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50"
                  >
                    Limpar
                  </button>
                )
              )}
            </div>
            {heightError && (
              <p className="mt-1 text-xs text-red-600">{heightError}</p>
            )}
          </div>

          {/* ===== Nome completo ===== */}
          <div>
            <label
              htmlFor="edit-profile-full-name"
              className="block text-sm font-medium text-gray-700"
            >
              Nome completo
            </label>
            <input
              id="edit-profile-full-name"
              type="text"
              value={fullNameInput}
              onChange={(e) => setFullNameInput(e.target.value)}
              disabled={saving}
              maxLength={120}
              placeholder="Como você quer aparecer"
              className={`mt-1 w-full rounded-md border px-3 py-2 text-sm text-gray-900 disabled:bg-gray-100 ${
                fullNameError
                  ? "border-red-500"
                  : "border-gray-300"
              }`}
            />
            {fullNameError && (
              <p className="mt-1 text-xs text-red-600">{fullNameError}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              E-mail e username não são editáveis por aqui — têm fluxos
              próprios.
            </p>
          </div>
        </div>

        {formError && (
          <p className="mt-4 text-xs text-red-600">{formError}</p>
        )}

        <div className="mt-6 flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="rounded-lg bg-rumo-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-rumo-600 disabled:opacity-50"
          >
            {saving ? "Salvando…" : "Salvar"}
          </button>
        </div>
      </div>
    </div>
  );
}