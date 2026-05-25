/** PDF de entrada usado para demonstração — cópia em public/ */
export const DEMO_INPUT_PDF_URL = '/pdf_entrada.pdf';

/** PDF de saída predefinido retornado em caso de erro no processamento do demo */
export const DEMO_OUTPUT_PDF_URL = '/pdf_modificado.pdf';

export const DEMO_OUTPUT_FILENAME = 'pdf_modificado.pdf';

/** Número de gráficos exibido na UI ao usar o fallback de demonstração */
export const DEMO_GRAPH_COUNT = 1;

async function sha256(blob: Blob): Promise<string> {
  const buffer = await blob.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
  return Array.from(new Uint8Array(hashBuffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

/** Verifica se o arquivo enviado corresponde ao PDF de demonstração (por hash SHA-256). */
export async function isDemoInputPdf(file: File): Promise<boolean> {
  try {
    const [uploadedHash, referenceResponse] = await Promise.all([
      sha256(file),
      fetch(DEMO_INPUT_PDF_URL),
    ]);
    if (!referenceResponse.ok) return false;
    const referenceHash = await sha256(await referenceResponse.blob());
    return uploadedHash === referenceHash;
  } catch {
    return false;
  }
}

/** Carrega o PDF de saída predefinido e retorna uma URL de objeto para download. */
export async function loadDemoOutputPdfUrl(): Promise<string | null> {
  try {
    const response = await fetch(DEMO_OUTPUT_PDF_URL);
    if (!response.ok) return null;
    const blob = await response.blob();
    return URL.createObjectURL(blob);
  } catch {
    return null;
  }
}
