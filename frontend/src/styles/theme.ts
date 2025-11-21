/**
 * Theme configuration for AI-Avangard
 * Following GitHub Copilot design system
 */

export const colors = {
  dark: {
    // Main backgrounds
    bg: {
      primary: '#0E1117',
      secondary: '#161B22',
      tertiary: '#21262D',
    },
    // Text colors
    text: {
      primary: '#e6edf3',
      secondary: '#8b949e',
      tertiary: '#57606a',
      white: '#ffffff',
    },
    // Borders
    border: {
      primary: '#30363D',
      secondary: '#21262D',
      muted: '#21262d',
    },
    // Accent colors
    accent: {
      blue: '#1B3554',
      blueHover: '#80AAD3',
      blueGradient: 'linear-gradient(135deg, #1B3554 0%, #80AAD3 100%)',
      green: '#238636',
      red: '#da3633',
      orange: '#d29922',
    },
  },
  light: {
    // Main backgrounds
    bg: {
      primary: '#f6f8fa',
      secondary: '#ffffff',
      tertiary: '#e6eaef',
    },
    // Text colors
    text: {
      primary: '#24292f',
      secondary: '#57606a',
      tertiary: '#8b949e',
      black: '#1f2328',
    },
    // Borders
    border: {
      primary: '#d0d7de',
      secondary: '#e6eaef',
      muted: '#c8d1da',
    },
    // Accent colors
    accent: {
      blue: '#1B3554',
      blueHover: '#80AAD3',
      blueGradient: 'linear-gradient(135deg, #1B3554 0%, #80AAD3 100%)',
      green: '#1a7f37',
      red: '#cf222e',
      orange: '#bf8700',
    },
  },
} as const;

export const breakpoints = {
  mobile: 375,
  mobileLarge: 430,
  tablet: 768,
  desktop: 1024,
  desktopLarge: 1440,
} as const;

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  xxl: '32px',
  xxxl: '48px',
} as const;

export const typography = {
  fontSize: {
    xs: '12px',
    sm: '13px',
    base: '14px',
    md: '16px',
    lg: '20px',
    xl: '24px',
    xxl: '28px',
    xxxl: '32px',
  },
  fontWeight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
  fontFamily: {
    base: '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
    mono: '"SF Mono", Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
  },
} as const;

export const shadows = {
  sm: '0 1px 3px rgba(0, 0, 0, 0.12)',
  md: '0 2px 6px rgba(0, 0, 0, 0.15)',
  lg: '0 4px 12px rgba(0, 0, 0, 0.15)',
  xl: '0 8px 24px rgba(0, 0, 0, 0.15)',
} as const;

export const borderRadius = {
  sm: '4px',
  md: '6px',
  lg: '8px',
  xl: '12px',
  full: '9999px',
} as const;

export const transitions = {
  fast: '0.15s ease',
  base: '0.2s ease',
  slow: '0.3s ease-out',
} as const;

export const zIndex = {
  base: 0,
  dropdown: 10,
  sticky: 50,
  overlay: 100,
  modal: 200,
  tooltip: 300,
} as const;

// Helper function to get theme colors
export const getThemeColors = (theme: 'light' | 'dark') => colors[theme];

// Type exports
export type Theme = 'light' | 'dark';
export type ThemeColors = typeof colors.dark | typeof colors.light;
