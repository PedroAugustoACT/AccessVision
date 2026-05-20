import { useState, useRef } from 'react';
import { DocumentIcon } from './DocumentIcon';
import { UploadFeedback } from './UploadFeedback';

const API_BASE = import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? '';
const PROCESS_URL = `${API_BASE}/api/v1/process`;
const MAX_SIZE_MB = 50;

interface UploadState {
  status: 'idle' | 'loading' | 'success' | 'error';
  fileName?: string;
  message?: string;
}

export function FileUpload() {
  const [uploadState, setUploadState] = useState<UploadState>({ status: 'idle' });
  const [isDragActive, setIsDragActive] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [downloadName, setDownloadName] = useState('pdf_acessivel.pdf');
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

  const processFile = async (file: File) => {
    if (!file.type.includes('pdf')) {
      setUploadState({
        status: 'error',
        message: 'Por favor, selecione um arquivo PDF válido',
      });
      return;
    }

    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setUploadState({
        status: 'error',
        message: `O arquivo excede o limite de ${MAX_SIZE_MB} MB`,
      });
      return;
    }

    clearDownloadUrl();
    setUploadState({
      status: 'loading',
      fileName: file.name,
    });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(PROCESS_URL, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let detail = 'Erro ao processar o PDF. Tente novamente.';
        try {
          const err = await response.json();
          if (err.detail) {
            detail = typeof err.detail === 'string' ? err.detail : detail;
          }
        } catch {
          /* ignore */
        }
        setUploadState({ status: 'error', message: detail });
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const baseName = file.name.replace(/\.pdf$/i, '');
      setDownloadUrl(url);
      setDownloadName(`acessivel_${baseName}.pdf`);
      setUploadState({
        status: 'success',
        fileName: file.name,
        message: 'PDF adaptado com sucesso',
      });

      setTimeout(() => {
        setUploadState({ status: 'idle' });
        clearDownloadUrl();
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }, 30000);
    } catch {
      setUploadState({
        status: 'error',
        message:
          'Não foi possível conectar à API. Verifique se o servidor está em execução ou tente mais tarde.',
      });
    }
  };

  const handleFile = (file: File) => {
    void processFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-lg p-8 md:p-12 transition-colors duration-200 ${
          isDragActive
            ? 'border-gov-blue bg-blue-50'
            : 'border-gov-gray bg-gov-light-gray hover:border-gov-blue hover:bg-blue-50'
        }`}
        role="region"
        aria-label="Área de envio de arquivo PDF"
        aria-describedby="upload-instructions"
      >
        {uploadState.status === 'idle' || uploadState.status === 'error' ? (
          <div className="flex flex-col items-center justify-center cursor-pointer">
            <DocumentIcon />
            <h3 className="mt-4 text-lg font-semibold text-gov-dark-gray">
              Envie seu arquivo PDF
            </h3>
            <div id="upload-instructions" className="mt-2 text-center">
              <p className="text-sm text-gov-dark-gray font-medium">
                Arraste e solte o arquivo aqui ou clique para selecionar
              </p>
              <p className="mt-2 text-xs text-gov-dark-gray">
                Tamanho máximo: {MAX_SIZE_MB}MB. Apenas arquivos PDF são aceitos.
              </p>
            </div>
            {uploadState.status === 'error' && uploadState.message && (
              <p className="mt-4 text-sm text-gov-red font-medium" role="alert" aria-live="assertive">
                {uploadState.message}
              </p>
            )}
            <button
              onClick={handleClick}
              className="mt-6 px-6 py-3 bg-gov-blue text-white font-semibold rounded-lg hover:bg-[#005080] active:bg-[#004a6b] transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gov-blue focus:ring-offset-2"
              aria-label="Selecionar arquivo PDF para enviar"
            >
              Selecionar Arquivo
            </button>
          </div>
        ) : (
          <UploadFeedback
            status={uploadState.status}
            fileName={uploadState.fileName}
            message={uploadState.message}
            onDownload={uploadState.status === 'success' ? handleDownloadPDF : undefined}
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
