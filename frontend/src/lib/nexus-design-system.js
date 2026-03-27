/**
 * NEXUS Design System
 * Hybrid combining: DaisyUI + Animate.css + Custom NEXUS tokens
 * 
 * Features:
 * - Color palette optimized for NEXUS brand
 * - Animation utilities for smooth transitions
 * - Design tokens for consistency
 * - Tailwind-first approach
 */

// NEXUS Color System
export const colors = {
  // Primary gradient colors
  primary: {
    cyan: {
      50: '#ecfeff',
      100: '#cffafe',
      200: '#a5f3fc',
      300: '#67e8f9',
      400: '#22d3ee',
      500: '#06b6d4', // NEXUS cyan
      600: '#0891b2',
      700: '#0e7490',
      800: '#155e75',
      900: '#164e63',
    },
    purple: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#c084fc',
      500: '#a855f7', // NEXUS purple
      600: '#9333ea',
      700: '#7e22ce',
      800: '#6b21a8',
      900: '#581c87',
    },
  },
  
  // Background colors (dark theme)
  background: {
    primary: '#050505',    // Main background
    secondary: '#0a0a0a',  // Cards, modals
    tertiary: '#0f0f0f',   // Elevated surfaces
  },
  
  // Semantic colors
  semantic: {
    success: '#10b981',    // Green
    error: '#ef4444',      // Red
    warning: '#f59e0b',    // Amber
    info: '#3b82f6',       // Blue
  },
  
  // Text colors
  text: {
    primary: '#ffffff',
    secondary: '#9ca3af',
    tertiary: '#6b7280',
    muted: '#4b5563',
  },
};

// NEXUS Typography Scale
export const typography = {
  // Heading sizes (mobile-first, responsive)
  h1: 'text-4xl sm:text-5xl lg:text-6xl font-bold',
  h2: 'text-3xl sm:text-4xl lg:text-5xl font-bold',
  h3: 'text-2xl sm:text-3xl lg:text-4xl font-bold',
  h4: 'text-xl sm:text-2xl lg:text-3xl font-bold',
  h5: 'text-lg sm:text-xl lg:text-2xl font-semibold',
  h6: 'text-base sm:text-lg font-semibold',
  
  // Body text
  body: 'text-base',
  bodyLarge: 'text-lg',
  bodySmall: 'text-sm',
  caption: 'text-xs',
  
  // Gradients
  gradientText: 'bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent',
};

// NEXUS Spacing System
export const spacing = {
  section: 'py-12 md:py-16 lg:py-24',
  container: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8',
  card: 'p-6 lg:p-8',
  cardSmall: 'p-4 lg:p-6',
};

// NEXUS Border Radius
export const borderRadius = {
  sm: 'rounded-lg',
  md: 'rounded-xl',
  lg: 'rounded-2xl',
  full: 'rounded-full',
};

// NEXUS Shadows & Glows
export const effects = {
  // Neon glow effects
  glow: {
    cyan: 'shadow-[0_0_20px_rgba(6,182,212,0.3)]',
    purple: 'shadow-[0_0_20px_rgba(168,85,247,0.3)]',
    both: 'shadow-[0_0_20px_rgba(6,182,212,0.2),0_0_40px_rgba(168,85,247,0.2)]',
  },
  
  // Standard shadows
  shadow: {
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
  },
  
  // Glass morphism
  glass: 'bg-white/5 backdrop-blur-xl border border-white/10',
  glassHover: 'hover:bg-white/10 hover:border-white/20',
};

// NEXUS Animation Classes
export const animations = {
  // Entrance animations (from animate.css)
  fadeIn: 'animate__animated animate__fadeIn',
  fadeInUp: 'animate__animated animate__fadeInUp',
  fadeInDown: 'animate__animated animate__fadeInDown',
  slideInLeft: 'animate__animated animate__slideInLeft',
  slideInRight: 'animate__animated animate__slideInRight',
  zoomIn: 'animate__animated animate__zoomIn',
  bounceIn: 'animate__animated animate__bounceIn',
  
  // Attention seekers
  pulse: 'animate__animated animate__pulse animate__infinite',
  bounce: 'animate__animated animate__bounce',
  shake: 'animate__animated animate__shake',
  
  // Custom durations
  faster: 'animate__faster',
  fast: 'animate__fast',
  slow: 'animate__slow',
  slower: 'animate__slower',
  
  // Tailwind animations
  spin: 'animate-spin',
  ping: 'animate-ping',
  
  // Custom NEXUS animations
  float: 'animate-float',
  glow: 'animate-glow',
};

// NEXUS Button Styles
export const buttons = {
  primary: `
    px-6 py-3 
    bg-gradient-to-r from-cyan-600 to-purple-600 
    hover:from-cyan-700 hover:to-purple-700 
    ${borderRadius.md} 
    font-semibold 
    transition-all duration-300
    ${effects.glow.both}
  `,
  
  secondary: `
    px-6 py-3 
    bg-white/5 
    hover:bg-white/10 
    border border-white/10 
    hover:border-white/20 
    ${borderRadius.md} 
    font-semibold 
    transition-all duration-300
  `,
  
  success: `
    px-6 py-3 
    bg-green-600 
    hover:bg-green-700 
    ${borderRadius.md} 
    font-semibold 
    transition-all duration-300
  `,
  
  danger: `
    px-6 py-3 
    bg-red-600 
    hover:bg-red-700 
    ${borderRadius.md} 
    font-semibold 
    transition-all duration-300
  `,
  
  ghost: `
    px-6 py-3 
    hover:bg-white/5 
    ${borderRadius.md} 
    font-semibold 
    transition-all duration-300
  `,
};

// NEXUS Card Styles
export const cards = {
  default: `
    ${effects.glass} 
    ${borderRadius.lg} 
    ${spacing.card}
    transition-all duration-300
  `,
  
  hover: `
    ${effects.glass} 
    ${borderRadius.lg} 
    ${spacing.card}
    ${effects.glassHover}
    transition-all duration-300
    cursor-pointer
  `,
  
  gradient: `
    bg-gradient-to-br from-cyan-500/10 to-purple-500/10 
    border border-cyan-500/20 
    ${borderRadius.lg} 
    ${spacing.card}
    transition-all duration-300
  `,
};

// NEXUS Input Styles
export const inputs = {
  default: `
    w-full 
    bg-white/5 
    border border-white/10 
    ${borderRadius.md} 
    px-4 py-3 
    focus:outline-none 
    focus:border-cyan-500 
    transition-all duration-300
  `,
  
  error: `
    w-full 
    bg-white/5 
    border border-red-500 
    ${borderRadius.md} 
    px-4 py-3 
    focus:outline-none 
    focus:border-red-400 
    transition-all duration-300
  `,
};

// NEXUS Badge Styles
export const badges = {
  primary: `
    px-3 py-1 
    bg-gradient-to-r from-cyan-600 to-purple-600 
    ${borderRadius.full} 
    text-sm font-semibold
  `,
  
  success: `
    px-3 py-1 
    bg-green-500/20 
    border border-green-500/30 
    text-green-400 
    ${borderRadius.full} 
    text-sm font-semibold
  `,
  
  warning: `
    px-3 py-1 
    bg-yellow-500/20 
    border border-yellow-500/30 
    text-yellow-400 
    ${borderRadius.full} 
    text-sm font-semibold
  `,
  
  info: `
    px-3 py-1 
    bg-blue-500/20 
    border border-blue-500/30 
    text-blue-400 
    ${borderRadius.full} 
    text-sm font-semibold
  `,
};

// Utility function to combine classes
export const cn = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

// Export design system as default
const designSystem = {
  colors,
  typography,
  spacing,
  borderRadius,
  effects,
  animations,
  buttons,
  cards,
  inputs,
  badges,
  cn,
};

export default designSystem;
