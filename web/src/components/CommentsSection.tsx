import { useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import {
  useComments,
  useCreateComment,
  useDeleteComment,
} from "../hooks/useSocial";
import { formatRelativeDate } from "../lib/format";
import type { Comment } from "../types/api";

export function CommentsSection({ activityId }: { activityId: string }) {
  const { user } = useAuth();
  const { data: comments, isLoading } = useComments(activityId);
  const createComment = useCreateComment(activityId);
  const [draft, setDraft] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const content = draft.trim();
    if (!content) return;
    createComment.mutate(content, {
      onSuccess: () => setDraft(""),
    });
  }

  return (
    <section>
      <h2 className="text-sm font-semibold text-gray-700 mb-3">
        Comentários {comments ? `(${comments.length})` : ""}
      </h2>

      {/* Formulário */}
      {user && (
        <form onSubmit={handleSubmit} className="mb-4">
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Escreva um comentário…"
            maxLength={500}
            rows={2}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:border-rumo-500 focus:outline-none focus:ring-1 focus:ring-rumo-500"
          />
          <div className="mt-2 flex items-center justify-between">
            <span className="text-xs text-gray-400">{draft.length}/500</span>
            <button
              type="submit"
              disabled={!draft.trim() || createComment.isPending}
              className="rounded-lg bg-rumo-500 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-rumo-600 disabled:opacity-50"
            >
              {createComment.isPending ? "Enviando…" : "Comentar"}
            </button>
          </div>
          {createComment.isError && (
            <p className="mt-1 text-xs text-red-600">
              Erro ao comentar. Tente de novo.
            </p>
          )}
        </form>
      )}

      {/* Lista */}
      {isLoading && <p className="text-sm text-gray-500">Carregando…</p>}

      {comments && comments.length === 0 && (
        <p className="text-sm text-gray-500">
          Nenhum comentário ainda. Seja o primeiro!
        </p>
      )}

      {comments && comments.length > 0 && (
        <ul className="space-y-3">
          {comments.map((c) => (
            <CommentRow
              key={c.id}
              comment={c}
              canDelete={user?.id === c.author.id}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

function CommentRow({
  comment,
  canDelete,
}: {
  comment: Comment;
  canDelete: boolean;
}) {
  const deleteComment = useDeleteComment(comment.activity_id);

  function handleDelete() {
    if (!confirm("Apagar este comentário?")) return;
    deleteComment.mutate(comment.id);
  }

  return (
    <li className="rounded-lg bg-white shadow-sm p-3">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 text-sm">
            <Link
              to={`/users/${comment.author.id}`}
              className="font-medium text-gray-800 hover:text-rumo-600"
            >
              @{comment.author.username}
            </Link>
            <span className="text-xs text-gray-400">
              {formatRelativeDate(comment.created_at)}
            </span>
          </div>
          <p className="mt-1 whitespace-pre-wrap text-sm text-gray-700">
            {comment.content}
          </p>
        </div>

        {canDelete && (
          <button
            type="button"
            onClick={handleDelete}
            disabled={deleteComment.isPending}
            className="shrink-0 text-xs text-gray-400 hover:text-red-600 disabled:opacity-50"
            aria-label="Apagar comentário"
          >
            {deleteComment.isPending ? "…" : "Apagar"}
          </button>
        )}
      </div>
    </li>
  );
}