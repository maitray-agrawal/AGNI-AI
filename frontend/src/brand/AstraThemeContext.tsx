import React, { createContext, useContext, useState, useEffect } from 'react';
import { AstraProjectId } from './ProjectMark';
import { astraProducts, AstraProduct } from './astraProducts';

export type AstraThemeMode = 'light' | 'dark' | 'sandstone' | 'monochrome';

interface AstraThemeContextType {
  theme: AstraThemeMode;
  setTheme: (theme: AstraThemeMode) => void;
  project: AstraProjectId;
  setProject: (project: AstraProjectId) => void;
  currentProduct: AstraProduct;
}

const AstraThemeContext = createContext<AstraThemeContextType | undefined>(undefined);

export const AstraThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<AstraThemeMode>(() => {
    return (localStorage.getItem('astra-theme') as AstraThemeMode) || 'light';
  });

  const [project, setProjectState] = useState<AstraProjectId>(() => {
    return (localStorage.getItem('astra-project') as AstraProjectId) || 'agni';
  });

  const setTheme = (newTheme: AstraThemeMode) => {
    setThemeState(newTheme);
    localStorage.setItem('astra-theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  const setProject = (newProject: AstraProjectId) => {
    setProjectState(newProject);
    localStorage.setItem('astra-project', newProject);
    document.documentElement.setAttribute('data-project', newProject);
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-project', project);
  }, [theme, project]);

  const currentProduct = astraProducts[project] || astraProducts['agni'];

  return (
    <AstraThemeContext.Provider value={{ theme, setTheme, project, setProject, currentProduct }}>
      {children}
    </AstraThemeContext.Provider>
  );
};

export const useAstraTheme = (): AstraThemeContextType => {
  const context = useContext(AstraThemeContext);
  if (!context) {
    throw new Error('useAstraTheme must be used within an AstraThemeProvider');
  }
  return context;
};
