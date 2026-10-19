import { useActivitySearch } from "../hooks/useActivitySearch";
import { ActivityCard } from "./ActivityCard";

interface ActivityResultsProps {
  /** Termo já debounced (o debounce vive no SearchPage, não aqui). */
  query: string;
}

/**
 * Resultados da busca de atividades.
 *
 * Diferente do UserResults: não renderizo link externo — o ActivityCard
 * já é o <Link> pro detalhe. Passo `activity` + `author` como props
 * separadas porque é o contrato do componente (não aceita FeedItem
 * direto, e não vale a pena mudar o card só pra busca).
 */
export function ActivityResults({ query }: ActivityResultsProps) {
  const { data, isPending, isError, error } = useActivitySearch(query);
  const tooShort = query.trim().length < 2;

  if (tooShort) {
    return (
      <p className="text-sm text-gray-500">
        Digite ao menos 2 caracteres para buscar.
      </p>
    );
  }

  if (isPending) {
    return <p className="text-sm text-rumo-400">Buscando…</p>;
  }

  if (isError) {
    return (
      <p className="text-sm text-red-600">
        Erro ao buscar:{" "}
        {error instanceof Error ? error.message : "tente novamente"}
      </p>
    );
  }

  if (!data || data.length === 0) {
    return (
      <p className="text-sm text-gray-500">Nenhuma atividade encontrada.</p>
    );
  }

  return (
    <div className="space-y-3">
      {data.map((item) => (
        <ActivityCard key={item.id} activity={item} author={item.author} />
      ))}
    </div>
  );
}