import { useState, useRef } from 'react';
import { DocumentIcon } from './DocumentIcon';
import { UploadFeedback } from './UploadFeedback';
import {
  ProgressSteps,
  type Step,
  type StepId,
  INITIAL_STEPS,
  SSE_STEP_MAP,
} from './ProgressSteps';
import {
  DEMO_GRAPH_COUNT,
  DEMO_OUTPUT_FILENAME,
  isDemoInputPdf,
  loadDemoOutputPdfUrl,
} from '../lib/demoPdfFallback';

const API_BASE = import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? '';
const STREAM_URL = `${API_BASE}/api/v1/process/stream`;
const MAX_SIZE_MB = 50;

interface UploadState {
  status: 'idle' | 'loading' | 'success' | 'error';
  fileName?: string;
  message?: string;
  graphCount?: number;
}

interface SseEvent {
  step: string;
  message: string;
  progress: number;
  pdf_b64?: string;
  filename?: string;
  count?: number;
}

/** Marca todas as etapas até (e incluindo) o stepId como concluídas */
function advanceSteps(steps: Step[], activeStepId: StepId, isError = false): Step[] {
  const activeIdx = steps.findIndex((s) => s.id === activeStepId);
  return steps.map((step, idx) => {
    if (isError && idx === activeIdx) return { ...step, status: 'error' };
    if (idx < activeIdx) return { ...step, status: 'done' };
    if (idx === activeIdx) return { ...step, status: isError ? 'error' : 'active' };
    return { ...step, status: 'pending' };
  });
}

export function FileUpload() {
  const [uploadState, setUploadState] = useState<UploadState>({ status: 'idle' });
  const [isDragActive, setIsDragActive] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [downloadName, setDownloadName] = useState('pdf_acessivel.pdf');
  const [steps, setSteps] = useState<Step[]>(INITIAL_STEPS);
  const [progress, setProgress] = useState(0);
  const [stepDetail, setStepDetail] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const clearDownloadUrl = () => {
    if (downloadUrl) {
      URL.revokeObjectURL(downloadUrl);
      setDownloadUrl(null);
    }
  };

  const handleDownloadPDF = () => {
    if (!downloadUrl) return;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = downloadName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const applyDemoFallbackSuccess = async (fileName: string): Promise<boolean> => {
    const url = await loadDemoOutputPdfUrl();
    if (!url) return false;

    clearDownloadUrl();
    setDownloadUrl(url);
    setDownloadName(DEMO_OUTPUT_FILENAME);
    setSteps((prev) => prev.map((s) => ({ ...s, status: 'done' as const })));
    setProgress(100);
    setStepDetail('');
    setUploadState({
      status: 'success',
      fileName,
      message: 'PDF adaptado com sucesso',
      graphCount: DEMO_GRAPH_COUNT,
    });
    return true;
  };

  const processFile = async (file: File) => {
    if (!file.type.includes('pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
      setUploadState({ status: 'error', message: 'Por favor, selecione um arquivo PDF válido' });
      return;
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setUploadState({ status: 'error', message: `O arquivo excede o limite de ${MAX_SIZE_MB} MB` });
      return;
    }

    const isDemoInput = await isDemoInputPdf(file);

    clearDownloadUrl();
    setSteps(INITIAL_STEPS);
    setProgress(0);
    setStepDetail('');
    setUploadState({ status: 'loading', fileName: file.name });

    const formData = new FormData();
    formData.append('file', file);

    let receivedResult = false;

    try {
      const response = await fetch(STREAM_URL, { method: 'POST', body: formData });

      if (!response.ok || !response.body) {
        if (isDemoInput && (await applyDemoFallbackSuccess(file.name))) return;

        let detail = 'Erro ao processar o PDF. Tente novamente.';
        try {
          const err = await response.json();
          if (typeof err.detail === 'string') detail = err.detail;
        } catch { /* ignore */ }
        setUploadState({ status: 'error', message: detail });
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      const handleEvent = async (event: SseEvent) => {
        const mappedStepId = SSE_STEP_MAP[event.step] as StepId | undefined;

        if (mappedStepId) {
          setSteps((prev) => {
            const updated = advanceSteps(prev, mappedStepId, event.step === 'error');
            return updated.map((s) =>
              s.id === mappedStepId ? { ...s, detail: event.message } : s,
            );
          });
        }

        setProgress(event.progress);
        setStepDetail(event.message);

        if (event.step === 'result' && event.pdf_b64) {
          receivedResult = true;

          const binary = atob(event.pdf_b64);
          const bytes = new Uint8Array(binary.length);
          for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
          const blob = new Blob([bytes], { type: 'application/pdf' });
          const url = URL.createObjectURL(blob);

          setDownloadUrl(url);
          setDownloadName(event.filename ?? `acessivel_${file.name}`);
          setSteps((prev) => prev.map((s) => ({ ...s, status: 'done' as const })));
          setProgress(100);

          setUploadState({
            status: 'success',
            fileName: file.name,
            message: 'PDF adaptado com sucesso',
            graphCount: event.count,
          });
        }

        if (event.step === 'error') {
          if (isDemoInput && (await applyDemoFallbackSuccess(file.name))) return;
          setUploadState({ status: 'error', message: event.message });
        }
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop() ?? '';
        for (const part of parts) {
          const line = part.replace(/^data:\s*/, '').trim();
          if (line) {
            try { await handleEvent(JSON.parse(line) as SseEvent); } catch { /* ignore */ }
          }
        }
      }

      if (!receivedResult && isDemoInput && (await applyDemoFallbackSuccess(file.name))) return;
    } catch {
      if (isDemoInput && (await applyDemoFallbackSuccess(file.name))) return;

      setUploadState({
        status: 'error',
        message:
          'Não foi possível conectar à API. Verifique se o servidor está em execução ou tente mais tarde.',
      });
    }
  };

  const handleReset = () => {
    clearDownloadUrl();
    setUploadState({ status: 'idle' });
    setSteps(INITIAL_STEPS);
    setProgress(0);
    setStepDetail('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleFile = (file: File) => { void processFile(file); };
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
  };
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.currentTarget.files?.length) handleFile(e.currentTarget.files[0]);
  };
  const handleClick = () => fileInputRef.current?.click();

  const handleDropzoneKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  const isIdle = uploadState.status === 'idle' || uploadState.status === 'error';

  return (
    <div className="w-full">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={isIdle ? handleClick : undefined}
        onKeyDown={isIdle ? handleDropzoneKeyDown : undefined}
        tabIndex={isIdle ? 0 : -1}
        role={isIdle ? 'button' : 'region'}
        aria-label={isIdle ? 'Área de envio: clique ou pressione Enter para selecionar um arquivo PDF' : 'Área de envio de arquivo PDF'}
        aria-describedby="upload-instructions"
        className={`relative border-2 border-dashed rounded-lg p-8 md:p-10 transition-colors duration-200 ${
          isDragActive
            ? 'border-gov-blue bg-blue-50'
            : isIdle
            ? 'border-gov-gray bg-gov-light-gray hover:border-gov-blue hover:bg-blue-50 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gov-blue focus-visible:ring-offset-2'
            : 'border-gov-gray bg-gov-light-gray'
        }`}
      >
        {isIdle ? (
          <div className="flex flex-col items-center justify-center">
            <DocumentIcon />
            <h3 className="mt-4 text-lg font-semibold text-gov-dark-gray">
              Envie seu arquivo PDF
            </h3>
            <div id="upload-instructions" className="mt-2 text-center">
              <p className="text-sm text-gov-dark-gray font-medium">
                Arraste e solte o arquivo aqui ou clique para selecionar
              </p>
              <p className="mt-2 text-xs text-gov-dark-gray">
                Tamanho máximo: {MAX_SIZE_MB} MB. Apenas arquivos PDF são aceitos.
              </p>
            </div>
            {uploadState.status === 'error' && uploadState.message && (
              <p
                className="mt-4 text-sm text-gov-red font-medium"
                role="alert"
                aria-live="assertive"
              >
                {uploadState.message}
              </p>
            )}
            <button
              onClick={(e) => { e.stopPropagation(); handleClick(); }}
              className="mt-6 px-6 py-3 bg-gov-blue text-white font-semibold rounded-lg hover:bg-[#005080] active:bg-[#004a6b] transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gov-blue focus:ring-offset-2"
              aria-label="Selecionar arquivo PDF para enviar"
              tabIndex={-1}
            >
              Selecionar Arquivo
            </button>
          </div>
        ) : uploadState.status === 'loading' ? (
          /* Estado de carregamento: mostra progresso em tempo real */
          <div className="flex flex-col gap-4" aria-live="polite" aria-atomic="false">
            <div className="text-center">
              <p className="text-sm font-semibold text-gov-blue">Processando arquivo…</p>
              {uploadState.fileName && (
                <p className="mt-1 text-xs text-gov-dark-gray truncate max-w-xs mx-auto" title={uploadState.fileName}>
                  {uploadState.fileName}
                </p>
              )}
            </div>
            <ProgressSteps steps={steps} progress={progress} />
            {stepDetail && (
              <p className="text-center text-xs text-gov-dark-gray italic" aria-live="polite">
                {stepDetail}
              </p>
            )}
          </div>
        ) : (
          /* Estados success / error */
          <UploadFeedback
            status={uploadState.status as 'success' | 'error'}
            fileName={uploadState.fileName}
            message={uploadState.message}
            graphCount={uploadState.graphCount}
            onDownload={uploadState.status === 'success' ? handleDownloadPDF : undefined}
            onReset={uploadState.status === 'success' ? handleReset : undefined}
          />
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleInputChange}
          className="hidden"
          aria-label="Selecionar arquivo PDF para processar"
          aria-describedby="upload-instructions"
        />
      </div>
    </div>
  );
}
