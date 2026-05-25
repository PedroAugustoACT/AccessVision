export type StepId = 'extract' | 'enhance' | 'describe' | 'build' | 'done';
export type StepStatus = 'pending' | 'active' | 'done' | 'error';

export interface Step {
  id: StepId;
  label: string;
  status: StepStatus;
  detail?: string;
}

interface ProgressStepsProps {
  steps: Step[];
  progress: number; // 0–100
}

const STEP_ICONS: Record<StepStatus, React.ReactNode> = {
  pending: (
    <span className="w-6 h-6 rounded-full border-2 border-gov-dark-gray bg-transparent flex items-center justify-center" aria-hidden="true" />
  ),
  active: (
    <span className="w-6 h-6 rounded-full border-2 border-gov-blue flex items-center justify-center" aria-hidden="true">
      <span className="w-2.5 h-2.5 rounded-full bg-gov-blue animate-pulse" />
    </span>
  ),
  done: (
    <span className="w-6 h-6 rounded-full bg-gov-green flex items-center justify-center" aria-hidden="true">
      <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
      </svg>
    </span>
  ),
  error: (
    <span className="w-6 h-6 rounded-full bg-gov-red flex items-center justify-center" aria-hidden="true">
      <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
      </svg>
    </span>
  ),
};

export function ProgressSteps({ steps, progress }: ProgressStepsProps) {
  const isDone = steps.every((s) => s.status === 'done');
  const hasError = steps.some((s) => s.status === 'error');
  // assertive quando concluído ou com erro para anuncio imediato por leitores de tela
  const liveMode = isDone || hasError ? 'assertive' : 'polite';

  return (
    <div className="w-full" role="status" aria-live={liveMode} aria-label="Progresso do processamento">
      {/* Barra de progresso */}
      <div className="mb-5">
        <div
          className="h-2 w-full rounded-full bg-gray-200 overflow-hidden"
          role="progressbar"
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Progresso: ${progress}%`}
        >
          <div
            className="h-full rounded-full bg-gov-blue transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="mt-1 text-right text-xs text-gov-dark-gray font-medium">{progress}%</p>
      </div>

      {/* Lista de etapas */}
      <ol className="space-y-3" aria-label="Etapas do processamento">
        {steps.map((step, idx) => (
          <li key={step.id} className="flex items-start gap-3">
            {/* Ícone de status */}
            <div className="mt-0.5 flex-shrink-0">{STEP_ICONS[step.status]}</div>

            {/* Conteúdo */}
            <div className="flex-1 min-w-0">
              <p
                className={`text-sm font-semibold leading-tight ${
                  step.status === 'active'
                    ? 'text-gov-blue'
                    : step.status === 'done'
                    ? 'text-gov-green'
                    : step.status === 'error'
                    ? 'text-gov-red'
                    : 'text-gov-dark-gray'
                }`}
              >
                {step.label}
              </p>
              {step.detail && (
                <p className="mt-0.5 text-xs text-gov-dark-gray truncate" title={step.detail}>
                  {step.detail}
                </p>
              )}
            </div>

            {/* Linha conectora (exceto na última etapa) */}
            {idx < steps.length - 1 && (
              <div className="absolute" aria-hidden="true" />
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}

/** Mapa de step SSE → índice na lista de etapas fixas */
export const SSE_STEP_MAP: Record<string, StepId> = {
  extract: 'extract',
  enhance: 'enhance',
  describe: 'describe',
  build: 'build',
  done: 'done',
  result: 'done',
};

export const INITIAL_STEPS: Step[] = [
  { id: 'extract', label: 'Extração de gráficos', status: 'pending' },
  { id: 'enhance', label: 'Aprimoramento de contraste', status: 'pending' },
  { id: 'describe', label: 'Descrição acessível com IA', status: 'pending' },
  { id: 'build',   label: 'Construção do PDF acessível', status: 'pending' },
  { id: 'done',    label: 'Concluído', status: 'pending' },
];
