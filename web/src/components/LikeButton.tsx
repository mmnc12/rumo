import { useActivityLikes, useToggleLike } from "../hooks/useSocial";

export function LikeButton({ activityId }: { activityId: string }) {
  const { data, isLoading } = useActivityLikes(activityId);
  const toggleLike = useToggleLike(activityId);

  const liked = data?.liked_by_me ?? false;
  const count = data?.count ?? 0;

  function handleClick() {
    toggleLike.mutate(liked);
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={isLoading || toggleLike.isPending}
      aria-label={liked ? "Remover like" : "Curtir"}
      className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-medium transition disabled:opacity-50 ${
        liked
          ? "border-rumo-500 bg-rumo-50 text-rumo-600"
          : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
      }`}
    >
      <HeartIcon filled={liked} />
      <span>
        {count} {count === 1 ? "kudo" : "kudos"}
      </span>
    </button>
  );
}

function HeartIcon({ filled }: { filled: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill={filled ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={filled ? 0 : 2}
      className="h-4 w-4"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
      />
    </svg>
  );
}