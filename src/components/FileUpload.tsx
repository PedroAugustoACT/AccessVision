import { useState, useRef } from 'react';
import { DocumentIcon } from './DocumentIcon';
import { UploadFeedback } from './UploadFeedback';


interface UploadState {
  status: 'idle' | 'loading' | 'success' | 'error';
  fileName?: string;
  message?: string;
}

export function FileUpload() {
  const [uploadState, setUploadState] = useState<UploadState>({ status: 'idle' });
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleFile = (file: File) => {
    if (!file.type.includes('pdf')) {
      setUploadState({
        status: 'error',
        message: 'Por favor, selecione um arquivo PDF válido',
      });
      return;
    }

    // Simulando upload com loading
    setUploadState({
      status: 'loading',
      fileName: file.name,
    });

    // Simula delay de upload
    setTimeout(() => {
      setUploadState({
        status: 'success',
        fileName: file.name,
        message: 'Arquivo enviado com sucesso',
      });

      // Limpa a mensagem após 5 segundos
      setTimeout(() => {
        setUploadState({ status: 'idle' });
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }, 5000);
    }, 2000);
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
      >
        {uploadState.status === 'idle' || uploadState.status === 'error' ? (
          <div className="flex flex-col items-center justify-center cursor-pointer">
            <DocumentIcon />
            <h3 className="mt-4 text-lg font-semibold text-gov-dark-gray">
              Envie seu arquivo PDF
            </h3>
            <p className="mt-2 text-sm text-gov-dark-gray font-medium">
              Arraste e solte o arquivo aqui ou clique para selecionar
            </p>
            <p className="mt-2 text-xs text-gov-dark-gray">
              Tamanho máximo: 50MB
            </p>
            {uploadState.status === 'error' && uploadState.message && (
              <p className="mt-4 text-sm text-gov-red font-medium" role="alert">
                {uploadState.message}
              </p>
            )}
            <button
              onClick={handleClick}
              className="mt-6 px-6 py-3 bg-gov-blue text-white font-semibold rounded-lg hover:bg-[#005080] active:bg-[#004a6b] transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gov-blue focus:ring-offset-2"
              aria-label="Selecionar arquivo PDF"
            >
              Selecionar Arquivo
            </button>
          </div>
        ) : (
          <UploadFeedback
            status={uploadState.status}
            fileName={uploadState.fileName}
            message={uploadState.message}
          />
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleInputChange}
          className="hidden"
          aria-label="Entrada de arquivo"
        />
      </div>
    </div>
  );
}
