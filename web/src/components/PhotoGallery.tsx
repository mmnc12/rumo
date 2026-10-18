import { useState } from "react";

import type { ActivityPhoto } from "../types/api";

interface PhotoGalleryProps {
  photos: ActivityPhoto[];
  canDelete?: boolean;
  onDelete?: (photoId: string) => void;
}

export function PhotoGallery({
  photos,
  canDelete = false,
  onDelete,
}: PhotoGalleryProps) {
  const [lightbox, setLightbox] = useState<ActivityPhoto | null>(null);

  if (photos.length === 0) return null;

  return (
    <>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {photos.map((photo) => (
          <div key={photo.id} className="group relative">
            <button
              type="button"
              onClick={() => setLightbox(photo)}
              className="block w-full overflow-hidden rounded-lg bg-gray-100"
            >
              <img
                src={photo.url}
                alt="Foto da atividade"
                className="h-32 w-full object-cover transition group-hover:scale-105"
                loading="lazy"
              />
            </button>
            {canDelete && onDelete && (
              <button
                type="button"
                onClick={() => onDelete(photo.id)}
                className="absolute right-1 top-1 rounded-full bg-black/60 px-2 py-1 text-xs text-white opacity-0 transition group-hover:opacity-100"
                aria-label="Remover foto"
              >
                ✕
              </button>
            )}
          </div>
        ))}
      </div>

      {lightbox && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
          onClick={() => setLightbox(null)}
        >
          <img
            src={lightbox.url}
            alt="Foto da atividade"
            className="max-h-full max-w-full rounded-lg"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}