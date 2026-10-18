import { apiFetch } from "./client";
import type { ActivityPhoto } from "../types/api";

export async function listActivityPhotos(
  activityId: string,
): Promise<ActivityPhoto[]> {
  return apiFetch<ActivityPhoto[]>(`/activities/${activityId}/photos`);
}

export async function uploadActivityPhoto(
  activityId: string,
  file: File,
): Promise<ActivityPhoto> {
  const formData = new FormData();
  formData.append("file", file);

  return apiFetch<ActivityPhoto>(`/activities/${activityId}/photos`, {
    method: "POST",
    rawBody: formData,
  });
}

export async function deleteActivityPhoto(photoId: string): Promise<void> {
  return apiFetch<void>(`/photos/${photoId}`, { method: "DELETE" });
}