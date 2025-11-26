import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  currentUser: string | null;
  setCurrentUser: (user: string | null) => void;
  availableUsers: string[];
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Predefined AWS IAM users (matches users in AWS account)
const AVAILABLE_USERS = [
  'aws-admin-user',
  'terraform-user',
  'kartik-aws-user',
  'test-user',
  'demo-user'
];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUserState] = useState<string | null>(null);

  // Clear saved user on mount to ensure fresh start
  useEffect(() => {
    localStorage.removeItem('nhi-agent-current-user');
  }, []);

  // Save to localStorage when user changes
  const setCurrentUser = (user: string | null) => {
    setCurrentUserState(user);
    if (user) {
      localStorage.setItem('nhi-agent-current-user', user);
    } else {
      localStorage.removeItem('nhi-agent-current-user');
    }
  };

  return (
    <AuthContext.Provider value={{ currentUser, setCurrentUser, availableUsers: AVAILABLE_USERS }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
