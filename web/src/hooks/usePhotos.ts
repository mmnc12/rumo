import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  deleteActivityPhoto,
  listActivityPhotos,
  uploadActivityPhoto,
} from "../api/photos";

export const photosKeys = {
  all: ["photos"] as const,
  list: (activityId: string) => [...photosKeys.all, "list", activityId] as const,
};

export function useActivityPhotos(activityId: string | undefined) {
  return useQuery({
    queryKey: photosKeys.list(activityId ?? ""),
    queryFn: () => listActivityPhotos(activityId!),
    enabled: !!activityId,
    staleTime: 30_000,
    retry: 1,
    refetchOnWindowFocus: false,
  });
}

export function useUploadPhoto(activityId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => uploadActivityPhoto(activityId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: photosKeys.list(activityId),
      });
    },
  });
}

export function useDeletePhoto(activityId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (photoId: string) => deleteActivityPhoto(photoId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: photosKeys.list(activityId),
      });
    },
  });
}