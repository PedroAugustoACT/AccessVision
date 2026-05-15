import { Header, FileUpload } from './components'

function App() {
  return (
    <div className="w-full h-screen bg-gradient-to-br from-gov-light-gray via-white to-blue-50 flex flex-col items-center justify-center overflow-hidden">
      <div className="w-full max-w-2xl px-4">
        {/* Header */}
        <Header />

        {/* Componente de Upload */}
        <div className="bg-white rounded-xl shadow-lg p-8 md:p-12">
          <FileUpload />
        </div>

        {/* Footer informativo */}
        <div className="mt-8 text-center text-sm text-gov-gray">
          <p>
            Seus dados são processados com segurança e em conformidade com a LGPD
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
