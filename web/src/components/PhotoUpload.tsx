import { useRef } from "react";

import { useUploadPhoto } from "../hooks/usePhotos";

interface PhotoUploadProps {
  activityId: string;
}

export function PhotoUpload({ activityId }: PhotoUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const upload = useUploadPhoto(activityId);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      upload.mutate(file);
      e.target.value = "";
    }
  };

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleChange}
        className="hidden"
      />
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={upload.isPending}
        className="rounded-lg bg-rumo-500 px-4 py-2 text-sm font-medium text-white hover:bg-rumo-600 disabled:opacity-50"
      >
        {upload.isPending ? "Enviando..." : "+ Adicionar foto"}
      </button>
      {upload.isError && (
        <p className="mt-2 text-sm text-red-600">
          {(upload.error as Error)?.message ?? "Erro no upload"}
        </p>
      )}
    </div>
  );
}