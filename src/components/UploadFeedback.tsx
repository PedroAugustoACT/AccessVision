import { LoadingSpinner } from "./LoadingSpinner";


interface UploadFeedbackProps {
  status: 'loading' | 'success' | 'error';
  fileName?: string;
  message?: string;
  onDownload?: () => void;
}

export function UploadFeedback({ status, fileName, message, onDownload }: UploadFeedbackProps) {
  return (
    <div className="flex flex-col items-center justify-center py-8" aria-live="polite" aria-atomic="true">
      {status === 'loading' && (
        <>
          <LoadingSpinner />
          <p className="mt-4 text-sm text-gov-dark-gray font-medium" aria-label="Processando arquivo">
            Processando arquivo...
          </p>
          {fileName && (
            <p className="mt-2 text-xs text-gov-dark-gray font-medium truncate max-w-xs" title={fileName}>
              {fileName}
            </p>
          )}
        </>
      )}

      {status === 'success' && (
        <>
          <div className="flex items-center justify-center w-16 h-16 rounded-full bg-green-100" role="img" aria-label="Sucesso">
            <svg
              className="w-8 h-8 text-gov-green"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h4 className="mt-4 text-lg font-semibold text-gov-green" id="success-message">
            {message}
          </h4>
          {fileName && (
            <p className="mt-2 text-sm text-gov-dark-gray" id="processed-file-name">
              Arquivo: <strong>{fileName}</strong>
            </p>
          )}
          {onDownload && (
            <button
              onClick={onDownload}
              className="mt-6 px-6 py-3 bg-gov-blue text-white font-semibold rounded-lg hover:bg-[#005080] active:bg-[#004a6b] transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gov-blue focus:ring-offset-2 flex items-center gap-2"
              aria-label="Baixar PDF adaptado para acessibilidade"
              aria-describedby="success-message processed-file-name"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Baixar PDF Modificado
            </button>
          )}
        </>
      )}
    </div>
  );
}
