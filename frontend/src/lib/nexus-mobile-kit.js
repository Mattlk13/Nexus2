/**
 * NEXUS Mobile Kit
 * Mobile-optimized components and utilities
 * Combines: Ratchet concepts + Photon aesthetics + Modernizr detection
 * 
 * Features:
 * - Touch-optimized components
 * - Mobile navigation patterns
 * - Feature detection utilities
 * - Responsive helpers
 */

import { useEffect, useState } from 'react';

/**
 * Feature Detection Utilities
 */
export const detectFeatures = () => {
  if (typeof window === 'undefined') return {};
  
  return {
    // Device type
    isMobile: /iPhone|iPad|iPod|Android/i.test(navigator.userAgent),
    isTablet: /iPad|Android/i.test(navigator.userAgent) && !/Mobile/i.test(navigator.userAgent),
    isDesktop: !/iPhone|iPad|iPod|Android/i.test(navigator.userAgent),
    
    // Screen
    isSmallScreen: window.innerWidth < 640,
    isMediumScreen: window.innerWidth >= 640 && window.innerWidth < 1024,
    isLargeScreen: window.innerWidth >= 1024,
    
    // Capabilities
    hasTouch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
    hasServiceWorker: 'serviceWorker' in navigator,
    hasNotifications: 'Notification' in window,
    hasGeolocation: 'geolocation' in navigator,
    
    // Network
    isOnline: navigator.onLine,
    connection: navigator.connection || navigator.mozConnection || navigator.webkitConnection,
    
    // Storage
    hasLocalStorage: (() => {
      try {
        localStorage.setItem('test', 'test');
        localStorage.removeItem('test');
        return true;
      } catch (e) {
        return false;
      }
    })(),
  };
};

/**
 * Hook for responsive detection
 */
export const useResponsive = () => {
  const [features, setFeatures] = useState(detectFeatures());
  
  useEffect(() => {
    const handleResize = () => {
      setFeatures(detectFeatures());
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return features;
};

/**
 * Mobile Navigation Drawer
 */
export const MobileDrawer = ({ 
  isOpen, 
  onClose, 
  side = 'left', // left or right
  children 
}) => {
  const translateClass = side === 'left' 
    ? (isOpen ? 'translate-x-0' : '-translate-x-full')
    : (isOpen ? 'translate-x-0' : 'translate-x-full');
  
  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Drawer */}
      <div 
        className={`
          fixed top-0 ${side}-0 bottom-0 
          w-[280px] max-w-[80vw]
          bg-[#0a0a0a] 
          border-${side === 'left' ? 'r' : 'l'} border-white/10
          z-50 
          transform ${translateClass}
          transition-transform duration-300 ease-in-out
          overflow-y-auto
          lg:hidden
        `}
      >
        {children}
      </div>
    </>
  );
};

/**
 * Touch-optimized Button Bar
 */
export const ButtonBar = ({ buttons = [], className = '' }) => {
  return (
    <div className={`flex gap-2 ${className}`}>
      {buttons.map((button, idx) => (
        <button
          key={idx}
          onClick={button.onClick}
          disabled={button.disabled}
          className={`
            flex-1 
            px-4 py-3 
            bg-white/5 
            hover:bg-white/10 
            active:bg-white/15
            rounded-xl 
            font-semibold 
            transition-all 
            touch-manipulation
            ${button.primary ? 'bg-gradient-to-r from-cyan-600 to-purple-600' : ''}
            ${button.disabled ? 'opacity-50 cursor-not-allowed' : ''}
            ${button.className || ''}
          `}
        >
          {button.icon && <span className="mr-2">{button.icon}</span>}
          {button.label}
        </button>
      ))}
    </div>
  );
};

/**
 * Mobile Bottom Navigation
 */
export const BottomNav = ({ items = [], activeItem, onChange }) => {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-[#0a0a0a] border-t border-white/10 z-30 lg:hidden">
      <div className="flex items-center justify-around px-2 py-3">
        {items.map((item) => {
          const isActive = activeItem === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onChange(item.id)}
              className={`
                flex flex-col items-center gap-1 
                px-4 py-2 
                rounded-lg 
                transition-all 
                touch-manipulation
                ${isActive ? 'text-cyan-400' : 'text-gray-400'}
              `}
            >
              {item.icon}
              <span className="text-xs font-semibold">{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

/**
 * Swipeable Card
 */
export const SwipeableCard = ({ 
  children, 
  onSwipeLeft, 
  onSwipeRight,
  className = '' 
}) => {
  const [startX, setStartX] = useState(0);
  const [translateX, setTranslateX] = useState(0);
  
  const handleTouchStart = (e) => {
    setStartX(e.touches[0].clientX);
  };
  
  const handleTouchMove = (e) => {
    const currentX = e.touches[0].clientX;
    setTranslateX(currentX - startX);
  };
  
  const handleTouchEnd = () => {
    if (translateX < -100 && onSwipeLeft) {
      onSwipeLeft();
    } else if (translateX > 100 && onSwipeRight) {
      onSwipeRight();
    }
    setTranslateX(0);
  };
  
  return (
    <div
      className={`touch-manipulation ${className}`}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      style={{
        transform: `translateX(${translateX}px)`,
        transition: translateX === 0 ? 'transform 0.3s ease-out' : 'none',
      }}
    >
      {children}
    </div>
  );
};

/**
 * Pull to Refresh
 */
export const PullToRefresh = ({ onRefresh, children, threshold = 80 }) => {
  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [startY, setStartY] = useState(0);
  
  const handleTouchStart = (e) => {
    if (window.scrollY === 0) {
      setStartY(e.touches[0].clientY);
    }
  };
  
  const handleTouchMove = (e) => {
    if (window.scrollY === 0 && startY > 0) {
      const currentY = e.touches[0].clientY;
      const distance = Math.max(0, currentY - startY);
      setPullDistance(Math.min(distance, threshold * 1.5));
    }
  };
  
  const handleTouchEnd = async () => {
    if (pullDistance >= threshold) {
      setIsRefreshing(true);
      await onRefresh();
      setIsRefreshing(false);
    }
    setPullDistance(0);
    setStartY(0);
  };
  
  return (
    <div
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="relative"
    >
      {/* Pull indicator */}
      <div 
        className="absolute top-0 left-0 right-0 flex items-center justify-center text-cyan-400 font-semibold transition-all"
        style={{ 
          height: `${pullDistance}px`,
          opacity: pullDistance / threshold 
        }}
      >
        {isRefreshing ? (
          <div className="animate-spin">⟳</div>
        ) : pullDistance >= threshold ? (
          <div>Release to refresh</div>
        ) : (
          <div>Pull to refresh</div>
        )}
      </div>
      
      <div style={{ transform: `translateY(${pullDistance}px)`, transition: 'transform 0.2s' }}>
        {children}
      </div>
    </div>
  );
};

/**
 * Touch-optimized List Item
 */
export const TouchListItem = ({ 
  icon, 
  title, 
  subtitle, 
  rightElement, 
  onClick,
  className = '' 
}) => {
  return (
    <div
      onClick={onClick}
      className={`
        flex items-center gap-4 
        p-4 
        active:bg-white/5 
        transition-colors 
        touch-manipulation
        cursor-pointer
        ${className}
      `}
    >
      {icon && (
        <div className="flex-shrink-0">
          {icon}
        </div>
      )}
      
      <div className="flex-1 min-w-0">
        <div className="font-semibold truncate">{title}</div>
        {subtitle && (
          <div className="text-sm text-gray-400 truncate">{subtitle}</div>
        )}
      </div>
      
      {rightElement && (
        <div className="flex-shrink-0">
          {rightElement}
        </div>
      )}
    </div>
  );
};

/**
 * Mobile-optimized Modal (Bottom Sheet)
 */
export const BottomSheet = ({ 
  isOpen, 
  onClose, 
  title, 
  children,
  height = 'auto' // auto, half, full
}) => {
  const heightClasses = {
    auto: 'max-h-[80vh]',
    half: 'h-[50vh]',
    full: 'h-[90vh]',
  };
  
  if (!isOpen) return null;
  
  return (
    <>
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black/60 z-40 lg:hidden"
        onClick={onClose}
      />
      
      {/* Sheet */}
      <div className={`
        fixed bottom-0 left-0 right-0
        bg-[#0a0a0a] 
        border-t border-white/10
        rounded-t-3xl
        z-50
        ${heightClasses[height]}
        overflow-y-auto
        animate__animated animate__slideInUp animate__faster
        lg:hidden
      `}>
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-2">
          <div className="w-12 h-1 bg-white/20 rounded-full" />
        </div>
        
        {/* Header */}
        {title && (
          <div className="px-6 py-3 border-b border-white/10">
            <h3 className="text-xl font-bold">{title}</h3>
          </div>
        )}
        
        {/* Content */}
        <div className="p-6">
          {children}
        </div>
      </div>
    </>
  );
};

/**
 * Haptic Feedback (if supported)
 */
export const triggerHaptic = (type = 'medium') => {
  if (window.navigator && window.navigator.vibrate) {
    const patterns = {
      light: 10,
      medium: 20,
      heavy: 30,
    };
    window.navigator.vibrate(patterns[type] || patterns.medium);
  }
};

// Export all components and utilities
export default {
  detectFeatures,
  useResponsive,
  MobileDrawer,
  ButtonBar,
  BottomNav,
  SwipeableCard,
  PullToRefresh,
  TouchListItem,
  BottomSheet,
  triggerHaptic,
};
