import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface SecurityContextType {
  secureMode: boolean;
  setSecureMode: (mode: boolean) => void;
}

const SecurityContext = createContext<SecurityContextType | undefined>(undefined);

export function SecurityProvider({ children }: { children: ReactNode }) {
  const [secureMode, setSecureModeState] = useState<boolean>(false);

  // Load mode from localStorage on mount
  useEffect(() => {
    const savedMode = localStorage.getItem('nhi-agent-secure-mode');
    if (savedMode === 'true') {
      setSecureModeState(true);
    }
  }, []);

  // Save to localStorage when mode changes
  const setSecureMode = (mode: boolean) => {
    setSecureModeState(mode);
    localStorage.setItem('nhi-agent-secure-mode', mode.toString());
  };

  return (
    <SecurityContext.Provider value={{ secureMode, setSecureMode }}>
      {children}
    </SecurityContext.Provider>
  );
}

export function useSecurity() {
  const context = useContext(SecurityContext);
  if (context === undefined) {
    throw new Error('useSecurity must be used within a SecurityProvider');
  }
  return context;
}
