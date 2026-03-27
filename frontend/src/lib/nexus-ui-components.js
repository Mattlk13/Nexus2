/**
 * NEXUS UI Components
 * Production-ready components combining Bootstrap concepts + Flat UI aesthetics
 * 
 * Components:
 * - ProductCard: Marketplace product display
 * - Modal: Reusable modal dialogs
 * - Form components: Input, Select, TextArea
 * - Alert: Notification/alert boxes
 * - Tabs: Tab navigation
 */

import React from 'react';
import { X } from 'lucide-react';
import { cn, cards, buttons, inputs, badges, borderRadius, effects } from './nexus-design-system';

/**
 * Product Card Component
 * Perfect for marketplace listings
 */
export const ProductCard = ({ 
  title, 
  description, 
  price, 
  imageUrl, 
  category, 
  likes, 
  sales,
  isAiGenerated = false,
  onClick,
  className = ''
}) => {
  return (
    <div 
      onClick={onClick}
      className={cn(
        cards.hover,
        'group overflow-hidden',
        className
      )}
    >
      {/* Image */}
      <div className={`relative aspect-video bg-gradient-to-br from-cyan-500/20 to-purple-500/20 ${borderRadius.md} mb-4 overflow-hidden`}>
        {imageUrl ? (
          <img src={imageUrl} alt={title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-600">
            No Image
          </div>
        )}
        
        {/* AI Badge */}
        {isAiGenerated && (
          <div className="absolute top-3 right-3">
            <span className={badges.primary}>
              ✨ AI Generated
            </span>
          </div>
        )}
        
        {/* Category Badge */}
        {category && (
          <div className="absolute top-3 left-3">
            <span className={badges.info}>
              {category}
            </span>
          </div>
        )}
      </div>
      
      {/* Content */}
      <div className="space-y-3">
        <h3 className="text-lg font-bold group-hover:text-cyan-400 transition-colors line-clamp-2">
          {title}
        </h3>
        
        {description && (
          <p className="text-sm text-gray-400 line-clamp-2">
            {description}
          </p>
        )}
        
        {/* Stats */}
        <div className="flex items-center gap-4 text-sm text-gray-400">
          {likes !== undefined && (
            <div className="flex items-center gap-1">
              <span>❤️</span>
              <span>{likes}</span>
            </div>
          )}
          {sales !== undefined && (
            <div className="flex items-center gap-1">
              <span>🛒</span>
              <span>{sales}</span>
            </div>
          )}
        </div>
        
        {/* Price */}
        {price !== undefined && (
          <div className="flex items-center justify-between pt-3 border-t border-white/10">
            <span className="text-2xl font-bold text-cyan-400">
              ${typeof price === 'number' ? price.toFixed(2) : price}
            </span>
            <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg font-semibold transition-all">
              View
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Modal Component
 * Reusable modal dialog
 */
export const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children,
  size = 'md', // sm, md, lg, xl
  showClose = true
}) => {
  if (!isOpen) return null;
  
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className={cn(
        'bg-[#0a0a0a] border border-white/10',
        borderRadius.lg,
        'p-8 w-full',
        sizeClasses[size],
        'animate__animated animate__fadeIn animate__faster'
      )}>
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">{title}</h2>
          {showClose && (
            <button 
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-lg transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
        
        {/* Content */}
        <div>
          {children}
        </div>
      </div>
    </div>
  );
};

/**
 * Input Component
 * Styled form input
 */
export const Input = ({ 
  label, 
  error, 
  helperText,
  className = '',
  ...props 
}) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-semibold text-gray-400">
          {label}
        </label>
      )}
      <input 
        className={cn(
          error ? inputs.error : inputs.default,
          className
        )}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}
      {helperText && !error && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
};

/**
 * TextArea Component
 */
export const TextArea = ({ 
  label, 
  error, 
  helperText,
  rows = 4,
  className = '',
  ...props 
}) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-semibold text-gray-400">
          {label}
        </label>
      )}
      <textarea 
        rows={rows}
        className={cn(
          error ? inputs.error : inputs.default,
          'resize-none',
          className
        )}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}
      {helperText && !error && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
};

/**
 * Select Component
 */
export const Select = ({ 
  label, 
  error, 
  options = [],
  className = '',
  ...props 
}) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-semibold text-gray-400">
          {label}
        </label>
      )}
      <select 
        className={cn(
          error ? inputs.error : inputs.default,
          className
        )}
        {...props}
      >
        {options.map((option, idx) => (
          <option key={idx} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}
    </div>
  );
};

/**
 * Button Component
 */
export const Button = ({ 
  variant = 'primary', // primary, secondary, success, danger, ghost
  size = 'md', // sm, md, lg
  children,
  className = '',
  loading = false,
  disabled = false,
  ...props 
}) => {
  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };
  
  return (
    <button 
      className={cn(
        buttons[variant],
        sizeClasses[size],
        'flex items-center justify-center gap-2',
        (loading || disabled) && 'opacity-50 cursor-not-allowed',
        className
      )}
      disabled={loading || disabled}
      {...props}
    >
      {loading && (
        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      )}
      {children}
    </button>
  );
};

/**
 * Alert Component
 */
export const Alert = ({ 
  type = 'info', // success, error, warning, info
  title,
  message,
  onClose,
  className = ''
}) => {
  const styles = {
    success: 'bg-green-500/10 border-green-500/30 text-green-400',
    error: 'bg-red-500/10 border-red-500/30 text-red-400',
    warning: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400',
    info: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
  };
  
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };
  
  return (
    <div className={cn(
      'flex items-start gap-3 p-4 border rounded-xl',
      styles[type],
      className
    )}>
      <span className="text-2xl flex-shrink-0">{icons[type]}</span>
      <div className="flex-1">
        {title && <div className="font-semibold mb-1">{title}</div>}
        {message && <div className="text-sm opacity-90">{message}</div>}
      </div>
      {onClose && (
        <button 
          onClick={onClose}
          className="flex-shrink-0 p-1 hover:bg-white/10 rounded transition-all"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};

/**
 * Tabs Component
 */
export const Tabs = ({ 
  tabs = [], 
  activeTab, 
  onChange,
  className = ''
}) => {
  return (
    <div className={cn('flex gap-2 flex-wrap', className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={cn(
            'px-6 py-3 rounded-xl font-semibold transition-all',
            activeTab === tab.id
              ? 'bg-gradient-to-r from-cyan-600 to-purple-600'
              : 'bg-white/5 hover:bg-white/10'
          )}
        >
          {tab.icon && <span className="mr-2">{tab.icon}</span>}
          {tab.label}
        </button>
      ))}
    </div>
  );
};

/**
 * Card Component
 */
export const Card = ({ 
  children, 
  variant = 'default', // default, hover, gradient
  className = '' 
}) => {
  return (
    <div className={cn(cards[variant], className)}>
      {children}
    </div>
  );
};

/**
 * Badge Component
 */
export const Badge = ({ 
  children, 
  variant = 'primary', // primary, success, warning, info
  className = '' 
}) => {
  return (
    <span className={cn(badges[variant], className)}>
      {children}
    </span>
  );
};

// Export all components
export default {
  ProductCard,
  Modal,
  Input,
  TextArea,
  Select,
  Button,
  Alert,
  Tabs,
  Card,
  Badge,
};
