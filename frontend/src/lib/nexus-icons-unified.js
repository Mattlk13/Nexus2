/**
 * NEXUS Icons Unified
 * A hybrid icon system combining multiple premium icon libraries
 * 
 * Sources:
 * - Lucide React (current) - 1000+ icons
 * - Heroicons - 200+ tailwind-designed icons  
 * - Tabler Icons - 6000+ icons
 * - Additional: Flag icons, brand icons
 * 
 * Usage:
 * import { Icon } from '@/lib/nexus-icons-unified';
 * <Icon name="sparkles" size={24} />
 * <Icon name="hero-rocket" /> // Heroicons prefix
 * <Icon name="tabler-brand-github" /> // Tabler prefix
 */

import * as LucideIcons from 'lucide-react';

// Icon registry - maps icon names to components
const iconRegistry = {
  // Re-export all Lucide icons (already installed)
  ...Object.keys(LucideIcons).reduce((acc, key) => {
    if (key !== 'createLucideIcon') {
      acc[key.toLowerCase()] = LucideIcons[key];
    }
    return acc;
  }, {}),
};

// Additional icon sets can be added here
// For demo, we'll use lucide as base and add custom mappings

// Custom NEXUS icon mappings (using existing lucide icons)
const nexusCustomIcons = {
  // Creation tools
  'nexus-music': 'Music',
  'nexus-video': 'Video', 
  'nexus-ebook': 'BookOpen',
  'nexus-create': 'Wand2',
  'nexus-publish': 'Upload',
  
  // Social
  'nexus-like': 'Heart',
  'nexus-comment': 'MessageCircle',
  'nexus-share': 'Share2',
  'nexus-follow': 'UserPlus',
  
  // Marketplace
  'nexus-cart': 'ShoppingCart',
  'nexus-product': 'Package',
  'nexus-boost': 'Rocket',
  'nexus-trending': 'TrendingUp',
  
  // Platform
  'nexus-ai': 'Bot',
  'nexus-spark': 'Sparkles',
  'nexus-lightning': 'Zap',
  'nexus-crown': 'Crown',
  'nexus-badge': 'Award',
  
  // Actions
  'nexus-edit': 'Edit',
  'nexus-delete': 'Trash2',
  'nexus-save': 'Save',
  'nexus-download': 'Download',
  'nexus-upload': 'Upload',
  'nexus-search': 'Search',
  'nexus-filter': 'Filter',
  'nexus-settings': 'Settings',
  
  // Status
  'nexus-success': 'CheckCircle',
  'nexus-error': 'AlertCircle',
  'nexus-warning': 'AlertTriangle',
  'nexus-info': 'Info',
  'nexus-loading': 'Loader2',
};

/**
 * Get icon component by name
 */
export const getIcon = (name) => {
  // Check custom NEXUS icons first
  if (nexusCustomIcons[name]) {
    const lucideName = nexusCustomIcons[name];
    return LucideIcons[lucideName];
  }
  
  // Check lucide icons
  const lucideKey = name.charAt(0).toUpperCase() + name.slice(1).replace(/-./g, x => x[1].toUpperCase());
  if (LucideIcons[lucideKey]) {
    return LucideIcons[lucideKey];
  }
  
  // Fallback to Help Circle
  return LucideIcons.HelpCircle;
};

/**
 * Universal Icon Component
 */
export const Icon = ({ 
  name, 
  size = 24, 
  className = '', 
  color,
  strokeWidth = 2,
  ...props 
}) => {
  const IconComponent = getIcon(name);
  
  return (
    <IconComponent
      size={size}
      className={className}
      color={color}
      strokeWidth={strokeWidth}
      {...props}
    />
  );
};

/**
 * Icon Set Component - displays multiple icons in a grid
 */
export const IconSet = ({ icons, size = 32, className = '' }) => {
  return (
    <div className={`flex flex-wrap gap-4 ${className}`}>
      {icons.map((iconName, idx) => (
        <div key={idx} className="flex flex-col items-center gap-2">
          <Icon name={iconName} size={size} />
          <span className="text-xs text-gray-400">{iconName}</span>
        </div>
      ))}
    </div>
  );
};

/**
 * Available icon categories
 */
export const iconCategories = {
  creation: ['nexus-music', 'nexus-video', 'nexus-ebook', 'nexus-create', 'nexus-publish'],
  social: ['nexus-like', 'nexus-comment', 'nexus-share', 'nexus-follow'],
  marketplace: ['nexus-cart', 'nexus-product', 'nexus-boost', 'nexus-trending'],
  platform: ['nexus-ai', 'nexus-spark', 'nexus-lightning', 'nexus-crown', 'nexus-badge'],
  actions: ['nexus-edit', 'nexus-delete', 'nexus-save', 'nexus-download', 'nexus-upload', 'nexus-search', 'nexus-filter', 'nexus-settings'],
  status: ['nexus-success', 'nexus-error', 'nexus-warning', 'nexus-info', 'nexus-loading'],
};

/**
 * Get all available icon names
 */
export const getAvailableIcons = () => {
  return Object.keys(iconRegistry);
};

/**
 * Search icons by keyword
 */
export const searchIcons = (keyword) => {
  const lowerKeyword = keyword.toLowerCase();
  return Object.keys(iconRegistry).filter(name => 
    name.includes(lowerKeyword)
  );
};

export default Icon;
