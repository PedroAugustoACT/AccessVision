import { Header, FileUpload } from './components'

function App() {
  return (
    <main className="w-full h-screen bg-gradient-to-br from-gov-light-gray via-white to-blue-50 flex flex-col items-center justify-center overflow-hidden" role="main">
      <div className="w-full max-w-2xl px-4">
        {/* Header */}
        <Header />

        {/* Componente de Upload */}
        <div className="bg-white rounded-xl shadow-lg p-8 md:p-12" role="region" aria-label="Formulário de upload de arquivo">
          <FileUpload />
        </div>

        {/* Footer informativo */}
        <footer className="mt-8 text-center text-sm text-gov-dark-gray font-medium" role="contentinfo">
          <p>
            Informática na Educação - UFAL | Desenvolvido
          </p>
        </footer>
      </div>
    </main>
  )
}

export default App
