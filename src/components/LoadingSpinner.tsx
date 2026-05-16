export function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center">
      <div
        className="w-12 h-12 rounded-full border-4 border-gov-light-gray border-t-gov-blue animate-spin"
        role="status"
        aria-label="Processando seu arquivo"
        aria-busy="true"
      >
        <span className="sr-only">Carregando, por favor aguarde...</span>
      </div>
    </div>
  );
}
