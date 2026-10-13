import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useUploadGpx } from "../hooks/useActivities";
import { AppHeader } from "../components/AppHeader";

const MAX_SIZE_MB = 20;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

function isGpx(file: File): boolean {
  return file.name.toLowerCase().endsWith(".gpx");
}

export default function UploadPage() {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const mutation = useUploadGpx();

  function validateAndUpload(file: File) {
    setLocalError(null);
    if (!isGpx(file)) {
      setLocalError("Formato não suportado. Envie um arquivo .gpx.");
      return;
    }
    if (file.size > MAX_SIZE_BYTES) {
      setLocalError(`Arquivo muito grande. Limite: ${MAX_SIZE_MB} MB.`);
      return;
    }
    mutation.mutate(
      { file },
      {
        onSuccess: () => navigate("/activities"),
      }
    );
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) validateAndUpload(file);
  }

  function handleDragOver(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(true);
  }

  function handleDragLeave(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
  }

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) validateAndUpload(file);
    // reseta pra permitir reupload do mesmo arquivo
    e.target.value = "";
  }

  const apiError =
    mutation.error instanceof ApiError
      ? typeof mutation.error.detail === "string"
        ? mutation.error.detail
        : JSON.stringify(mutation.error.detail)
      : mutation.error?.message ?? null;

  const errorMessage = localError ?? apiError;
  const isUploading = mutation.isPending;

  return (
    <>
      <AppHeader />

      <div className="mx-auto max-w-2xl px-4 py-10">
        <h1 className="mb-2 text-2xl font-semibold text-gray-900">
          Enviar atividade
        </h1>
        <p className="mb-8 text-sm text-gray-500">
          Arraste um arquivo <code className="font-mono">.gpx</code> ou clique
          para escolher. Distância, pace e elevação são calculados
          automaticamente.
        </p>

        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !isUploading && inputRef.current?.click()}
          className={[
            "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed px-6 py-16 text-center transition",
            isDragging
              ? "border-rumo-500 bg-rumo-50"
              : "border-gray-300 bg-white hover:border-rumo-400 hover:bg-gray-50",
            isUploading ? "pointer-events-none opacity-60" : "",
          ].join(" ")}
        >
          {isUploading ? (
            <>
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-rumo-500 border-t-transparent" />
              <p className="text-sm text-gray-600">Enviando e processando…</p>
            </>
          ) : (
            <>
              <div className="text-4xl">📁</div>
              <p className="text-base font-medium text-gray-900">
                {isDragging ? "Solte o arquivo aqui" : "Arraste seu .gpx aqui"}
              </p>
              <p className="text-xs text-gray-500">
                ou clique para escolher • máx. {MAX_SIZE_MB} MB
              </p>
            </>
          )}
        </div>

        <input
          ref={inputRef}
          type="file"
          accept=".gpx,application/gpx+xml"
          hidden
          onChange={handleInputChange}
        />

        {errorMessage && (
          <div className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {errorMessage}
          </div>
        )}
      </div>
    </>
  );
}