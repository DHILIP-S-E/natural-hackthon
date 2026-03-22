import { useState, useEffect, useRef } from 'react';

export function useInstallPrompt() {
  const [canInstall, setCanInstall] = useState(false);
  const deferredPrompt = useRef<any>(null);

  useEffect(() => {
    const dismissed = localStorage.getItem('aura-install-dismissed');
    if (dismissed) return;

    const handler = (e: Event) => {
      e.preventDefault();
      deferredPrompt.current = e;
      setCanInstall(true);
    };
    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const install = async () => {
    if (!deferredPrompt.current) return;
    deferredPrompt.current.prompt();
    const result = await deferredPrompt.current.userChoice;
    if (result.outcome === 'accepted') setCanInstall(false);
    deferredPrompt.current = null;
  };

  const dismiss = () => {
    setCanInstall(false);
    localStorage.setItem('aura-install-dismissed', 'true');
  };

  return { canInstall, install, dismiss };
}
