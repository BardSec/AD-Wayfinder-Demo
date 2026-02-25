import { Network } from 'lucide-react'

function MicrosoftLogo() {
  return (
    <svg width="20" height="20" viewBox="0 0 21 21" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="1" y="1" width="9" height="9" fill="#f25022" />
      <rect x="11" y="1" width="9" height="9" fill="#7fba00" />
      <rect x="1" y="11" width="9" height="9" fill="#00a4ef" />
      <rect x="11" y="11" width="9" height="9" fill="#ffb900" />
    </svg>
  )
}

export default function LoginPage() {
  return (
    <div className="h-screen flex flex-col items-center justify-center bg-slate-900">
      <div className="bg-slate-800 rounded-2xl shadow-2xl p-10 flex flex-col items-center gap-6 w-full max-w-sm border border-slate-700">
        <div className="flex items-center gap-3">
          <Network size={32} className="text-indigo-400" />
          <span className="text-white text-2xl font-bold tracking-tight">AD Wayfinder</span>
        </div>

        <p className="text-slate-400 text-sm text-center leading-relaxed">
          Sign in with your Microsoft account to access the Active Directory browser.
        </p>

        <a
          href="/auth/login"
          className="w-full flex items-center justify-center gap-3 bg-[#0078d4] hover:bg-[#106ebe] active:bg-[#005a9e] text-white font-medium py-3 px-4 rounded-lg transition-colors"
        >
          <MicrosoftLogo />
          Sign in with Microsoft
        </a>
      </div>
    </div>
  )
}
