import { Link } from "react-router-dom";

// [Sessão 43] Página pública de Política de Privacidade.
// - Rota: /privacy (pública, sem ProtectedRoute)
// - Link de entrada: footer do AppHeader + drawer mobile + menu desktop
// - Texto: rascunho técnico cobrindo LGPD (revisar com advogado antes de publicar)
// - Última atualização: 2026-11-20

const LAST_UPDATED = "20 de novembro de 2026";
const CONTACT_EMAIL = "privacidade@rumo.app"; // [S43] trocar pelo email real do responsável

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      {/* Voltar — sem header global nesta rota, então o link é o caminho de volta */}
      <Link
        to="/activities"
        className="inline-flex items-center gap-1 text-sm text-rumo-600 hover:text-rumo-700"
      >
        ← Voltar
      </Link>

      <h1 className="mt-4 text-3xl font-semibold text-gray-900">
        Política de Privacidade
      </h1>
      <p className="mt-1 text-sm text-gray-500">
        Última atualização: {LAST_UPDATED}
      </p>

      <div className="prose prose-sm mt-6 max-w-none text-gray-700">
        <p>
          O <strong>Rumo</strong> é um aplicativo para registrar, visualizar e
          compartilhar atividades físicas ao ar livre (corrida, caminhada,
          pedalada etc.). Esta política explica quais dados coletamos, como
          usamos, com quem compartilhamos e quais são os seus direitos como
          titular, em conformidade com a{" "}
          <strong>Lei Geral de Proteção de Dados (LGPD — Lei nº 13.709/2018)</strong>.
        </p>

        <h2 className="mt-6 text-xl font-semibold text-gray-900">
          1. Quais dados coletamos
        </h2>
        <p>Coletamos apenas os dados necessários para o funcionamento do app:</p>
        <ul className="mt-2 list-disc space-y-1 pl-6">
          <li>
            <strong>Dados de cadastro:</strong> nome de usuário (username),
            e-mail e senha (armazenada com hash, nunca em texto puro).
          </li>
          <li>
            <strong>Dados de perfil (opcionais):</strong> nome completo, peso
            (kg), altura (cm) e data de nascimento. Você pode deixar em branco
            ou limpar a qualquer momento.
          </li>
          <li>
            <strong>Dados de atividades:</strong> arquivos GPX enviados por
            você (que contêm traçado geográfico, distância, tempo, elevação,
            frequência cardíaca se o arquivo tiver) e metadados derivados
            (tipo de atividade, data, duração).
          </li>
          <li>
            <strong>Dados de uso:</strong> interações sociais dentro do app
            (quem você segue, comentários, curtidas) e notificações geradas
            por essas interações.
          </li>
          <li>
            <strong>Dados técnicos:</strong> endereço IP, user-agent e logs de
            erro do servidor, usados para segurança e diagnóstico. Não usamos
            cookies de rastreamento de terceiros.
          </li>
        </ul>

        <h2 className="mt-6 text-xl font-semibold text-gray-900">
          2. Como usamos seus dados
        </h2>
        <ul className="mt-2 list-disc space-y-1 pl-6">
          <li>
            <strong>Prestação do serviço:</strong> exibir suas atividades,
            calcular estatísticas (distância total, pace, evolução semanal),
            mostrar o feed de quem você segue.
          </li>
          <li>
            <strong>Compartilhamento social:</strong> seu username, nome
            completo (se preenchido) e atividades marcadas como públicas
            ficam visíveis para outros usuários do app. Atividades privadas
            ficam visíveis apenas para você.
          </li>
          <li>
            <strong>Segurança:</strong> detectar abuso, fraude e uso indevido.
          </li>
          <li>
            <strong>Comunicação:</strong> enviar e-mails transacionais
            (recuperação de senha, confirmação de cadastro). Não enviamos
            marketing sem consentimento explícito.
          </li>
        </ul>

        <h2 className="mt-6 text-xl font-semibold text-gray-900">
          3. Base legal (LGPD)
        </h2>
        <p>Tratamos seus dados com base em:</p>
        <ul className="mt-2 list-disc space-y-1 pl-6">
          <li>
            <strong>Execução de contrato</strong> (art. 7º, V): dados
            necessários para você usar o app.
          </li>
          <li>
            <strong>Consentimento</strong> (art. 7º, I): dados opcionais de
            perfil (peso, altura, data de nascimento) e envio de e-mails de
            marketing (se você optar por receber).
          </li>
          <li>
            <strong>Legítimo interesse</strong> (art. 7º, IX): segurança,
            prevenção a fraude e melhoria do serviço.
          </li>
        </ul>

        <h2 className="mt-6 text-xl font-semibold text-gray-900">
          4. Compartilhamento com terceiros
        </h2>
        <p>
          <strong>Não vendemos seus dados.</strong> Compartilhamos apenas com
          prestadores de serviço estritamente necessários:
        </p>
        <ul className="mt-2 list-disc space-y-1 pl-6">
          <li>
            <strong>Render</strong> (hospedagem do backend) — servidores nos
            EUA. Transferência internacional coberta por cláusulas contratuais
            padrão.
          </li>
          <li>
            <strong>Vercel</strong> (hospedagem do frontend web) — servidores
            globais (edge).
          </li>
          <li>
            <strong>OpenStreetMap</strong> (tiles de mapa) — recebe apenas
            coordenadas aproximadas da área visualizada, não seus dados
            pessoais.
          </li>
        </ul>
        <p className="mt-2">
          Se no futuro usarmos outros provedores (ex.: armazenamento de
          imagens, envio de e-mail transacional), esta política será
          atualizada antes da ativação.
        </p>

        <h2 className="mt-6 text-xl font-semibold text-gray-900">
          5. Por quanto tempo guardamos
        </h2>
        <ul className="mt-2 list-disc space-y-1 pl-6">
          <li>
            <strong>Conta ativa:</strong> enquanto você mantiver a conta.
          </li>
          <li>
            <strong>Após exclusão da conta:</strong> seus dados pessoais são
            apagados em até 30 dias. Atividades podem ser mantidas de forma
            anonimizada (sem vínculo com você) para estatísticas agregadas.
          </li>
          <li>
            <strong>Logs de segurança:</strong> até 6 meses, conforme o Marco
            Civil da Internet (Lei nº 12.965/2014).
          </li>
        </ul>

        <h2 className="mt-6 text-xl font-semibold text-gray-900">
          6. Seus direitos (LGPD)
        </h2>
        <p>Você pode, a qualquer momento:</p>
        <ul className="mt-2 list-disc space-y-1 pl-6">
          <li>Confirmar a existência de tratamento dos seus dados.</li>
          <li>Acessar os dados que temos sobre você.</li>
          <li>Corrigir dados incompletos, inexatos ou desatualizados.</li>
          <li>
            Solicitar anonimização, bloqueio ou eliminação de dados
            desnecessários ou excessivos.
          </li>
          <li>Revogar o consentimento (para dados opcionais).</li>
          <li>Solicitar a portabilidade dos dados (formato CSV/GPX já disponível no app).</li>
          <li>
            Solicitar a exclusão da conta e dos dados pessoais associados.
          </li>
        </ul>
        <p className="mt-2">
          Para exercer qualquer direito, entre em contato pelo e-mail{" "}
          <a
            href={`mailto:${CONTACT_EMAIL}`}
            className="text-rumo-600 underline hover:text-rumo-700"
          >
            {CONTACT_EMAIL}
          </a>
          . Responderemos em até 15 dias.
        </p>

        <h2 className="mt-6 text-xl font-semibold text-gray-900">
          7. Segurança
        </h2>
        <p>
          Adotamos medidas técnicas e administrativas para proteger seus
          dados: senhas com hash (bcrypt), conexões HTTPS em todas as
          comunicações, controle de acesso ao banco de dados e revisão
          periódica de dependências. Nenhum sistema é 100% seguro; em caso de
          incidente que afete seus dados, notificaremos você e a ANPD nos
          prazos legais.
        </p>

        <h2 className="mt-6 text-xl font-semibold text-gray-900">
          8. Crianças e adolescentes
        </h2>
        <p>
          O Rumo não é destinado a menores de 18 anos. Não coletamos
          intencionalmente dados de crianças. Se identificarmos uma conta de
          menor, ela será removida.
        </p>

        <h2 className="mt-6 text-xl font-semibold text-gray-900">
          9. Alterações nesta política
        </h2>
        <p>
          Podemos atualizar esta política para refletir mudanças no app ou na
          legislação. A data de "última atualização" no topo indica a versão
          vigente. Mudanças materiais serão comunicadas por e-mail ou aviso
          dentro do app antes de entrarem em vigor.
        </p>

        <h2 className="mt-6 text-xl font-semibold text-gray-900">
          10. Contato
        </h2>
        <p>
          Dúvidas sobre esta política ou sobre o tratamento dos seus dados:{" "}
          <a
            href={`mailto:${CONTACT_EMAIL}`}
            className="text-rumo-600 underline hover:text-rumo-700"
          >
            {CONTACT_EMAIL}
          </a>
          .
        </p>
        <p className="mt-2 text-sm text-gray-500">
          Encarregado de Dados (DPO): a definir. Enquanto isso, o contato
          acima responde pelas solicitações.
        </p>
      </div>
    </div>
  );
}